var personell = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        personell: '/static/sample_data/personell.json',
        clusterData: '/static/sample_data/cluster_data.json',
        teams: '/dashboard/teamsjsonview/'
    },
    initiate: function () {
        dataGetter.addNew(personell.urls.survey, personell.drawTable, true);
        dataGetter.addNew(personell.urls.personell, personell.drawTable, false);
        dataGetter.addNew(personell.urls.clusterData, personell.drawTable, false);
    },
    table: false,
    drawTable: function (data) {
        if (!dataGetter.checkAll([personell.urls.survey, personell.urls.personell, personell.urls.clusterData])) {
            /* Check that all relevant data has been downloaded, else cancel.
            See home.js. */
            return false;
        }

        var surveyData = dataGetter.downloads[personell.urls.survey].data.survey_data,
            personellData = dataGetter.downloads[personell.urls.personell].data.personell,
            clusterData = dataGetter.downloads[personell.urls.clusterData].data.clusters, // Cluster data not actually used directly in this function, but we need t make sure it is there for clusterInfo
            perPersonellData = [];

        _.each(personellData, function(personell, id) {
            var personellObject = {
                    personell_id: id,
                    name: personell.name,
                    gender: personell.gender,
                    phone: personell.phone,
                    email: personell.email,
                    position: personell.position,
                    state: '',
                    lga: '',
                    cluster: '',
                    date: '',
                    team: personell.team
                },
                birthdate = new Date(personell.birthdate),
                ageDiff = Date.now() - birthdate.getTime(),
                ageDate = new Date(ageDiff),
                age = Math.abs(ageDate.getUTCFullYear() - 1970);

            personellObject.age = age.toString();

            perPersonellData.push(personellObject);
        });

        _.each(surveyData, function(survey, id) {
            var teamMembers = _.where(perPersonellData, {team: survey.team}),
            surveyDate = survey.end_time.split('T')[0];

            if (teamMembers.length > 0 && teamMembers[0].date < surveyDate) {
                _.each(teamMembers, function(teamMember) {
                    teamMember.date = surveyDate;
                    teamMember.cluster = survey.cluster;
                    teamMember.state = clusterInfo.findState(survey.cluster);
                    teamMember.lga = clusterInfo.findLGA(survey.cluster);
                });
            }
        });

        if (personell.table) {
            // If the table exists already, we destroy it, as it cannot easily be reinitialized.
            personell.table.fnDestroy();
        }

        personell.table = jQuery('#personell_table').dataTable({
            data: perPersonellData,
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
                { name: 'personell_id', data: 'personell_id' },
                { name: 'name', data: 'name' },
                { name: 'position', data: 'position' },
                { name: 'age', data: 'age' },
                { name: 'gender', data: 'gender' },
                { name: 'phone', data: 'phone' },
                { name: 'email', data: 'email' },
                { name: 'state', data: 'state' },
                { name: 'lga', data: 'lga' },
                { name: 'cluster', data: 'cluster' },
                { name: 'date', data: 'date' },
            ],
            "order": [[ 1, "asc" ]]
        });

    },
};

personell.initiate();
