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

        var genderIcon = {
          M: '<i class="fa fa-male"></i> ',
          F: '<i class="fa fa-female"></i> '
        }

        _.each(personnelData, function(person, id) {

            var personnelObject = {
                name: genderIcon[person.gender] + '<div class="personnel-name"><strong>' + person.name + '</strong><br> 33 years</div>',
                personnel_id: id,
                contact: '<a href="mailto:' + person.email + '">' + person.email + '</a><br>' + person.phone,
                position: person.position,
                first_admin_level: '',
                second_admin_level: '',
                cluster: '',
                date: '',
                team: person.team,
                age: ''
            };

            perPersonnelData.push(personnelObject);
        });

        _.each(surveyData, function(survey, id) {

            // Join on "team"
            var teamMembers = _.where(perPersonnelData, {team: survey.team}),
            surveyDate = survey.endTime.split('T')[0];

            if (teamMembers.length > 0 && teamMembers[0].date < surveyDate) {
                _.each(teamMembers, function(teamMember) {

                    var cluster = clusterInfo.findName(survey.cluster) + ' #' + survey.cluster;
                    var first_admin = clusterInfo.findFirstAdminLevel(survey.cluster);
                    var second_admin = clusterInfo.findSecondAdminLevel(survey.cluster);       

                    teamMember.position = teamMember.position + '<br>' + moment(surveyDate).format('MMM D, YYYY');
                    teamMember.date = 'Team Leader<br>' + moment(surveyDate).format('MMM D YYYY');
                    teamMember.location = cluster + '<br> Admin Levels: ' + first_admin + ' / ' + second_admin; 
                });
            }
        });

        if (personnel.table) {
            // If the table exists already, we destroy it
            // as it cannot easily be reinitialized.
            personnel.table.fnDestroy();
        }

        personnel.table = jQuery('#personnel_table').dataTable({
            paging: true,
            ordering: true,
            searching: true,
            dom: '<"#personnel_data" <"page-header"fr<"clear">><t><"bottom">ip<"clear">>',
            data: perPersonnelData,
            responsive: {
                details: {
                    renderer: function(api, rowIdx) {
                        // Select hidden columns for the given row
                        var data = api.cells(rowIdx, ':hidden').eq(0).map( function(cell) {
                            var header = jQuery( api.column( cell.column ).header() );
                            return '<tr class="was-ist-das">'+
                                    '<td>'+ header.attr('data-column-name')+':'+'</td> '+
                                    '<td>'+ api.cell(cell).data()+'</td>'+
                                '</tr>';
                        }).toArray().join('');

                        return data ? $('<table/>').append(data) : false;
                    },
                }
            },
            columns: [
                { name: 'name', data: 'name' },
                { name: 'personnel_id', data: 'personnel_id' },
                { name: 'contact', data: 'contact' },
                { name: 'position', data: 'position' },
                { name: 'location', data: 'location' },
                { "searchable": false, data: function() { return ''; }, orderable: false }
            ],
            "order": [[ 1, "asc" ]]
        });

        // Add UI Items
        $('.page-header').append('<h1><i class="fa fa-user"></i> Personnel</h1>');
        $('#personnel_table_filter').addClass('pull-right');
        $('.page-header').prepend('<button class="pull-right btn btn-default dataTables_extra_button">Download</button>');

        // Download Button Action
        jQuery('#personnel_download button').on('click', function (){
            personnel.downloadData();
        });

    },
};

personnel.initiate();
