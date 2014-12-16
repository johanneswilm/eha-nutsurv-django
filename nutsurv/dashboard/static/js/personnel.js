var personnel = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        personnel: '/static/sample_data/personnel.json',
        clusterData: '/static/sample_data/cluster_data.json',
        teams: '/dashboard/teamsjsonview/'
    },
    initiate: function () {
        dataGetter.addNew(personnel.urls.survey, personnel.drawTable, true);
        dataGetter.addNew(personnel.urls.personnel, personnel.drawTable, false);
        dataGetter.addNew(personnel.urls.clusterData, personnel.drawTable, false);
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

        _.each(personnelData, function(personnel, id) {
            var personnelObject = {
                    personnel_id: id,
                    name: personnel.name,
                    gender: personnel.gender,
                    phone: personnel.phone,
                    email: personnel.email,
                    position: personnel.position,
                    state: '',
                    lga: '',
                    cluster: '',
                    cluster_number: '',
                    date: '',
                    team: personnel.team
                },
                birthdate = new Date(personnel.birthdate),
                ageDiff = Date.now() - birthdate.getTime(),
                ageDate = new Date(ageDiff),
                age = Math.abs(ageDate.getUTCFullYear() - 1970);

            personnelObject.age = age.toString();

            perPersonnelData.push(personnelObject);
        });

        _.each(surveyData, function(survey, id) {
            var teamMembers = _.where(perPersonnelData, {team: survey.team}),
            surveyDate = survey.end_time.split('T')[0];

            if (teamMembers.length > 0 && teamMembers[0].date < surveyDate) {
                _.each(teamMembers, function(teamMember) {
                    teamMember.date = surveyDate;
                    teamMember.cluster_number = survey.cluster;
                    teamMember.cluster = clusterInfo.findName(survey.cluster);
                    teamMember.state = clusterInfo.findState(survey.cluster);
                    teamMember.lga = clusterInfo.findLGA(survey.cluster);
                });
            }
        });

        if (personnel.table) {
            // If the table exists already, we destroy it, as it cannot easily be reinitialized.
            personnel.table.fnDestroy();
        }

        personnel.table = jQuery('#personnel_table').dataTable({
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
                { name: 'state', data: 'state' },
                { name: 'lga', data: 'lga' },
                { name: 'cluster', data: 'cluster' },
                { name: 'cluster_number', data: 'cluster_number' },
                { name: 'date', data: 'date' },
            ],
            "order": [[ 1, "asc" ]]
        });

    },
};

personnel.initiate();
