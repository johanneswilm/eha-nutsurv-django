var personnel = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        personnel: '/dashboard/personneljsonview/',
        clusterData: '/dashboard/clustersjsonview/',
        teams: '/dashboard/teamsjsonview/'
    },
    initiate: function () {
        dataGetter.addNew(personnel.urls.survey, personnel.drawTable, true);
        dataGetter.addNew(personnel.urls.personnel, personnel.drawTable, false);
        dataGetter.addNew(personnel.urls.clusterData, personnel.drawTable, false);
    },
    downloadData: function () {
        if (!personnel.table) {
            return false;
        }
        var data = personnel.table.fnGetData(), i, j, output='';

        output += _.keys(data[0]).join(',');
        output += '\n';

        for (i=0;i<data.length;i++) {
            output += _.values(data[i]).join(',');
            output += '\n';
        }

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'personnel.csv'
        );
    },
    table: false,
    drawTable: function (data) {
        if (!dataGetter.checkAll([personnel.urls.survey, personnel.urls.personnel, personnel.urls.clusterData])) {
            /* Check that all relevant data has been downloaded, else cancel.
            See home.js. */
            return false;
        }

        var surveyData = dataGetter.downloads[personnel.urls.survey].data.survey_data,
            personnelData = dataGetter.downloads[personnel.urls.personnel].data.personnel,
            clusterData = dataGetter.downloads[personnel.urls.clusterData].data.clusters, // Cluster data not actually used directly in this function, but we need t make sure it is there for clusterInfo
            perPersonnelData = [];
        _.each(personnelData, function(person, id) {
            var personnelObject = {
                    personnel_id: id,
                    name: person.name,
                    gender: person.gender,
                    phone: person.phone,
                    email: person.email,
                    position: person.position,
                    first_admin_level: '',
                    second_admin_level: '',
                    cluster: '',
                    cluster_number: '',
                    date: '',
                    team: person.team,
                    age: person.age.toString()
                };

            perPersonnelData.push(personnelObject);
        });

        _.each(surveyData, function(survey, id) {
            var teamMembers = _.where(perPersonnelData, {team: survey.team}),
            surveyDate = survey.endTime.split('T')[0];

            if (teamMembers.length > 0 && teamMembers[0].date < surveyDate) {
                _.each(teamMembers, function(teamMember) {
                    teamMember.date = surveyDate;
                    teamMember.cluster_number = survey.cluster;
                    teamMember.cluster = clusterInfo.findName(survey.cluster);
                    teamMember.first_admin_level = clusterInfo.findFirstAdminLevel(survey.cluster);
                    teamMember.second_admin_level = clusterInfo.findSecondAdminLevel(survey.cluster);
                });
            }
        });

        if (personnel.table) {
            // If the table exists already, we destroy it, as it cannot easily be reinitialized.
            personnel.table.fnDestroy();
        }

        personnel.table = jQuery('#personnel_table').dataTable({
            dom: '<"#personnel_download">lfrtip',
            data: perPersonnelData,
            responsive: {
                        details: {
                            renderer: function ( api, rowIdx ) {
                                // Select hidden columns for the given row
                                var data = api.cells( rowIdx, ':hidden' ).eq(0).map( function ( cell ) {
                                    var header = jQuery( api.column( cell.column ).header() );
                                    return '<tr>'+
                                            '<td>'+
                                                header.attr('data-column-name')+':'+
                                            '</td> '+
                                            '<td>'+
                                                api.cell( cell ).data()+
                                            '</td>'+
                                        '</tr>';
                                } ).toArray().join('');

                                return data ?
                                    $('<table/>').append( data ) :
                                    false;
                            },
                        }
                    },
            columns: [
                { "searchable": false, data: function(){return '';}, orderable: false },
                { name: 'personnel_id', data: 'personnel_id' },
                { name: 'name', data: 'name' },
                { name: 'position', data: 'position' },
                { name: 'age', data: 'age' },
                { name: 'gender', data: 'gender' },
                { name: 'phone', data: 'phone' },
                { name: 'email', data: 'email' },
                { name: 'date', data: 'date' },
                { name: 'first_admin_level', data: 'first_admin_level' },
                { name: 'second_admin_level', data: 'second_admin_level' },
                { name: 'cluster', data: 'cluster' },
                { name: 'cluster_number', data: 'cluster_number' }
            ],
            "order": [[ 1, "asc" ]]
        });

        jQuery('#personnel_download').html('<button></button>');
        jQuery('#personnel_download button').addClass('btn btn-default dataTables_extra_button');
        jQuery('#personnel_download button').text('Download');

        jQuery('#personnel_download button').on('click', function (){
            personnel.downloadData();
        });

    },
};

personnel.initiate();
