var surveyCompletedTeams = {
    urls : {
        survey: '/static/sample_data/survey.json',
        clustersPerTeam: '/static/sample_data/clusters_per_team.json',
        teams: '/static/sample_data/teams.json',
    },
    initiate: function () {
        dataGetter.addNew(surveyCompletedTeams.urls.teams, surveyCompletedTeams.setupTablePerTeam, false);
        dataGetter.addNew(surveyCompletedTeams.urls.survey, surveyCompletedTeams.setupTablePerTeam, true);
        dataGetter.addNew(surveyCompletedTeams.urls.clustersPerTeam, surveyCompletedTeams.setupTablePerTeam, false);
    },
    setupTablePerTeam: function (data) {
        if (!dataGetter.checkAll([surveyCompletedTeams.urls.survey,surveyCompletedTeams.urls.clustersPerTeam,surveyCompletedTeams.urls.teams])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }

        var surveyData = dataGetter.downloads[home.urls.survey].data,
            clustersPerTeamData = dataGetter.downloads[surveyCompletedTeams.urls.clustersPerTeam].data,
            teamData = dataGetter.downloads[surveyCompletedTeams.urls.teams].data,
            perTeamData = [];

        _.each(clustersPerTeamData.teams, function(clusters, team) {
            var teamObject = {
                    team: parseInt(team),
                    teamNames: teamData.teams[team],
                    households: 0,
                    women: 0,
                    children: 0,
                    members: 0,
                    clusterCodes: {},
                    clusters: clusters,
                    clustersComplete: 0,
                    minWomen: -1,
                    maxWomen: 0,
                    minChildren: -1,
                    maxChildren: 0,
                    minMembers: -1,
                    maxMembers: 0
                };

            perTeamData.push(teamObject);
        });
        console.log('ping')
        _.each(surveyData.survey_data, function(survey) {
            //var state = clusterInfo.findState(survey.cluster),
            console.log([survey.team,perTeamData]);
            var teamObject = _.findWhere(perTeamData, {team: survey.team});
            // Increase the number of households surveyed for this state by one.
            teamObject.households++;

            if (!survey.cluster in teamObject.clusterCodes) {
                teamObject.clusterCodes[survey.cluster] = 1;
                teamObject.clusters++;
            } else {
                teamObject.clusterCodes[survey.cluster]++;
                if (teamObject.clusterCodes[survey.cluster]===20) {
                    // When there are exactly 20 surveyed households in a given cluster, it is counted as complete.
                    teamObject.clustersComplete++;
                }
            }


            teamObject.members += survey.members.length;
            if (survey.members.length < teamObject.minMembers || teamObject.minMembers === -1) {
                teamObject.minMembers = survey.members.length;
            }
            if (survey.members.length > teamObject.maxMembers) {
                teamObject.maxMembers = survey.members.length;
            }

            if ('women_surveys' in survey) {
                teamObject.women += survey.women_surveys.length;
                if (survey.women_surveys.length < teamObject.minWomen || teamObject.minWomen === -1) {
                    teamObject.minWomen = survey.women_surveys.length;
                }
                if (survey.women_surveys.length > teamObject.maxWomen) {
                    teamObject.maxWomen = survey.women_surveys.length;
                }
            }
            if ('child_surveys' in survey) {
                teamObject.children += survey.child_surveys.length;
                if (survey.child_surveys.length < teamObject.minChildren || teamObject.minChildren === -1) {
                    teamObject.minChildren = survey.child_surveys.length;
                }
                if (survey.child_surveys.length > teamObject.maxChildren) {
                    teamObject.maxChildren = survey.child_surveys.length;
                }
            }

        });

        _.each(perTeamData, function(teamObject) {
            if (teamObject.households > 0) {
                teamObject.meanMembers = Math.round(teamObject.members / teamObject.households * 10) /10;
                teamObject.meanWomen = Math.round(teamObject.women / teamObject.households * 10) /10;
                teamObject.meanChildren = Math.round(teamObject.children / teamObject.households * 10) /10;
            } else {
                teamObject.meanMembers = 0;
                teamObject.meanWomen = 0;
                teamObject.meanChildren = 0;
            }
            if (teamObject.minMembers === -1) {
                teamObject.minMembers = 0;
            }
            if (teamObject.minChildren === -1) {
                teamObject.minChildren = 0;
            }
            if (teamObject.minWomen === -1) {
                teamObject.minWomen = 0;
            }
        });


        $('#survey_completed_teams_table').dataTable({
            data: perTeamData,
            responsive: {
                        details: {
                            renderer: function ( api, rowIdx ) {
                                // Select hidden columns for the given row
                                var data = api.cells( rowIdx, ':hidden' ).eq(0).map( function ( cell ) {
                                    var header = $( api.column( cell.column ).header() );
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
                { name: 'team', data: 'teamNames' },
                { name: 'households', data: 'households' },
                { name: 'clusters_total', data: 'clusters' },
                { name: 'clusters_complete', data: 'clustersComplete' },
                { name: 'members_min', data: 'minMembers' },
                { name: 'members_max', data: 'maxMembers' },
                { name: 'members_mean', data: 'meanMembers' },
                { name: 'women_total', data: 'women' },
                { name: 'women_min', data: 'minWomen' },
                { name: 'women_max', data: 'maxWomen' },
                { name: 'women_mean', data: 'meanWomen' },
                { name: 'children_total', data: 'children' },
                { name: 'children_min', data: 'minChildren' },
                { name: 'children_max', data: 'maxChildren' },
                { name: 'children_mean', data: 'meanChildren' },
            ],
            "order": [[ 1, "asc" ]]
        });

    },

};

surveyCompletedTeams.initiate();
