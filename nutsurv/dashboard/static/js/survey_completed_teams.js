var surveyCompletedTeams = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teammembers/'
    },
    initiate: function () {
        dataGetter.addNew(surveyCompletedTeams.urls.teams, surveyCompletedTeams.setupTablePerTeam, false);
        dataGetter.addNew(surveyCompletedTeams.urls.survey, surveyCompletedTeams.setupTablePerTeam, true);
    },
    downloadData: function () {
        if (!surveyCompletedTeams.table) {
            return false;
        }
        var data = surveyCompletedTeams.table.fnGetData(), i, j, output='';

        output += _.keys(data[0]).join(',');
        output += '\n';

        for (i=0;i<data.length;i++) {
            output += _.values(data[i]).join(',');
            output += '\n';
        }

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'survey_completed_teams.csv'
        );
    },
    table: false,
    setupTablePerTeam: function (data) {
        if (!dataGetter.checkAll([surveyCompletedTeams.urls.survey,surveyCompletedTeams.urls.teams])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }

        var surveyData = dataGetter.downloads[surveyCompletedTeams.urls.survey].data.survey_data,
            teamData = dataGetter.downloads[surveyCompletedTeams.urls.teams].data,
            perTeamData = [];

        _.each(teamData, function(team) {
            var teamObject = {
                    team: team.id,
                    teamID: team.id,
                    households: 0,
                    women: 0,
                    children: 0,
                    members: 0,
                    clusterCodes: {},
                    clusters: 0,
                    minWomen: -1,
                    maxWomen: 0,
                    minChildren: -1,
                    maxChildren: 0,
                    minMembers: -1,
                    maxMembers: 0,
                    maxHouseholdsPerCluster: 0,
                    minHouseholdsPerCluster: -1,
                    meanHouseholdsPerCluster: 0,
                };

            perTeamData.push(teamObject);
        });
        _.each(surveyData, function(survey) {
            var teamObject = _.findWhere(perTeamData, {team: survey.team}),
            childMembers = _.where(survey.members, {'surveyType': 'child'}),
            womenMembers = _.where(survey.members, {'surveyType': 'women'});
            // Increase the number of households surveyed for this team by one.
            if (teamObject) {
                teamObject.households++;

                if (!(survey.cluster in teamObject.clusterCodes)) {
                    teamObject.clusterCodes[survey.cluster] = 1;
                    teamObject.clusters++;
                } else {
                    teamObject.clusterCodes[survey.cluster]++;
                }

                teamObject.members += survey.members.length;
                if (survey.members.length < teamObject.minMembers || teamObject.minMembers === -1) {
                    teamObject.minMembers = survey.members.length;
                }
                if (survey.members.length > teamObject.maxMembers) {
                    teamObject.maxMembers = survey.members.length;
                }


                teamObject.women += womenMembers.length;
                if (womenMembers.length < teamObject.minWomen || teamObject.minWomen === -1) {
                    teamObject.minWomen = womenMembers.length;
                }
                if (womenMembers.length > teamObject.maxWomen) {
                    teamObject.maxWomen = womenMembers.length;
                }


                teamObject.children += childMembers.length;
                if (childMembers.length < teamObject.minChildren || teamObject.minChildren === -1) {
                    teamObject.minChildren = childMembers.length;
                }
                if (childMembers.length > teamObject.maxChildren) {
                    teamObject.maxChildren = childMembers.length;
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
            _.each(teamObject.clusterCodes, function(households, clusterCode) {
                if (households < teamObject.minHouseholdsPerCluster || teamObject.minHouseholdsPerCluster === -1) {
                    teamObject.minHouseholdsPerCluster = households;
                }
                if (households > teamObject.maxHouseholdsPerCluster) {
                    teamObject.maxHouseholdsPerCluster = households;
                }
            });
            delete teamObject.clusterCodes;
            if (teamObject.minHouseholdsPerCluster === -1) {
                teamObject.minHouseholdsPerCluster = 0;
            } else {
                teamObject.meanHouseholdsPerCluster = Math.round(teamObject.households / teamObject.clusters * 10) /10;
            }
        });

        if (surveyCompletedTeams.table) {
            // If the table exists already, we destroy it, as it cannot easily be reinitialized.
            surveyCompletedTeams.table.fnDestroy();
        }

        surveyCompletedTeams.table = jQuery('#survey_completed_teams_table').dataTable({
            dom: '<"#survey_completed_teams_download">lfrtip',
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
                { name: 'team', data: 'teamID' },
                { name: 'clusters', data: 'clusters' },
                { name: 'households', data: 'households' },
                { name: 'households_per_cluster_min', data: 'minHouseholdsPerCluster' },
                { name: 'households_per_cluster_max', data: 'maxHouseholdsPerCluster' },
                { name: 'households_per_cluster_mean', data: 'meanHouseholdsPerCluster' },
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
            order: [[ 1, "asc" ]]
        });

        jQuery('#survey_completed_teams_download').html('<button></button>');
        jQuery('#survey_completed_teams_download button').addClass('btn btn-default dataTables_extra_button');
        jQuery('#survey_completed_teams_download button').text('Download');

        jQuery('#survey_completed_teams_download button').on('click', function (){
            surveyCompletedTeams.downloadData();
        });

    },

};

surveyCompletedTeams.initiate();
