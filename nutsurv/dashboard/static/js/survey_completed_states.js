var surveyCompletedStates = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        clustersPerState: '/static/sample_data/clusters_per_state.json',
        clusterData: '/static/sample_data/cluster_data.json',
        statesWithReserveClusters: '/static/sample_data/states_with_reserve_clusters.json'
    },
    initiate: function () {
        dataGetter.addNew(surveyCompletedStates.urls.survey, surveyCompletedStates.setupTablePerState, true);
        dataGetter.addNew(surveyCompletedStates.urls.clustersPerState, surveyCompletedStates.setupTablePerState, false);
        dataGetter.addNew(surveyCompletedStates.urls.clusterData, surveyCompletedStates.setupTablePerState, false);
        dataGetter.addNew(surveyCompletedStates.urls.statesWithReserveClusters, surveyCompletedStates.setupTablePerState, true);
    },
    table: false,
    setupTablePerState: function (data) {
        if (!dataGetter.checkAll([surveyCompletedStates.urls.survey,surveyCompletedStates.urls.clustersPerState,surveyCompletedStates.urls.statesWithReserveClusters, surveyCompletedStates.urls.clusterData])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        var surveyData = dataGetter.downloads[surveyCompletedStates.urls.survey].data.survey_data,
            clustersPerStateData = dataGetter.downloads[surveyCompletedStates.urls.clustersPerState].data.states,
            clusterData = dataGetter.downloads[surveyCompletedStates.urls.clusterData].data.clusters, // Cluster data not actually used directly in this function, but we need t make sure it is there for clusterInfo
            statesWithReserveClustersData = dataGetter.downloads[surveyCompletedStates.urls.statesWithReserveClusters].data.states,
            perStateData = [];

        _.each(clustersPerStateData, function(clusters, state) {
            var stateObject = {
                    state: state,
                    households: 0,
                    women: 0,
                    children: 0,
                    members: 0,
                    clusterCodes: {},
                    clusters: 0,
                    clustersComplete: 0,
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
            if (statesWithReserveClustersData.indexOf(state) === -1) {
                // Reserve clusters not enabled
                stateObject.reserve = false;
                stateObject.totalClusters = clusters.standard;
            } else {
                // Reserves have been enabled for this state
                stateObject.reserve = true;
                stateObject.totalClusters = clusters.standard + clusters.reserve;
            }
            perStateData.push(stateObject);
        });

        _.each(surveyData, function(survey) {
            var state = clusterInfo.findState(survey.cluster),
            stateObject = _.findWhere(perStateData, {state: state});
            // Increase the number of households surveyed for this state by one.
            stateObject.households++;

            if (!(survey.cluster in stateObject.clusterCodes)) {
                stateObject.clusterCodes[survey.cluster] = 1;
                stateObject.clusters++;
            } else {
                stateObject.clusterCodes[survey.cluster]++;
                if (stateObject.clusterCodes[survey.cluster]===20) {
                    // When there are exactly 20 surveyed households in a given cluster, it is counted as complete.
                    stateObject.clustersComplete++;
                }
            }


            stateObject.members += survey.members.length;
            if (survey.members.length < stateObject.minMembers || stateObject.minMembers === -1) {
                stateObject.minMembers = survey.members.length;
            }
            if (survey.members.length > stateObject.maxMembers) {
                stateObject.maxMembers = survey.members.length;
            }

            if ('women_surveys' in survey) {
                stateObject.women += survey.women_surveys.length;
                if (survey.women_surveys.length < stateObject.minWomen || stateObject.minWomen === -1) {
                    stateObject.minWomen = survey.women_surveys.length;
                }
                if (survey.women_surveys.length > stateObject.maxWomen) {
                    stateObject.maxWomen = survey.women_surveys.length;
                }
            }
            if ('child_surveys' in survey) {
                stateObject.children += survey.child_surveys.length;
                if (survey.child_surveys.length < stateObject.minChildren || stateObject.minChildren === -1) {
                    stateObject.minChildren = survey.child_surveys.length;
                }
                if (survey.child_surveys.length > stateObject.maxChildren) {
                    stateObject.maxChildren = survey.child_surveys.length;
                }
            }

        });

        _.each(perStateData, function(stateObject) {
            if (stateObject.households > 0) {
                stateObject.meanMembers = Math.round(stateObject.members / stateObject.households * 10) /10;
                stateObject.meanWomen = Math.round(stateObject.women / stateObject.households * 10) /10;
                stateObject.meanChildren = Math.round(stateObject.children / stateObject.households * 10) /10;
            } else {
                stateObject.meanMembers = 0;
                stateObject.meanWomen = 0;
                stateObject.meanChildren = 0;
            }
            if (stateObject.minMembers === -1) {
                stateObject.minMembers = 0;
            }
            if (stateObject.minChildren === -1) {
                stateObject.minChildren = 0;
            }
            if (stateObject.minWomen === -1) {
                stateObject.minWomen = 0;
            }
            _.each(stateObject.clusterCodes, function(households, clusterCode) {
                if (households < stateObject.minHouseholdsPerCluster || stateObject.minHouseholdsPerCluster === -1) {
                    stateObject.minHouseholdsPerCluster = households;
                }
                if (households > stateObject.maxHouseholdsPerCluster) {
                    stateObject.maxHouseholdsPerCluster = households;
                }
            });
            if (stateObject.minHouseholdsPerCluster === -1) {
                stateObject.minHouseholdsPerCluster = 0;
            } else {
                stateObject.meanHouseholdsPerCluster = Math.round(stateObject.households / stateObject.clusters * 10) /10;
            }
        });

        if (surveyCompletedStates.table) {
            // If the table exists already, we destroy it, as it cannot easily be reinitialized.
            surveyCompletedStates.table.fnDestroy();
        }

        surveyCompletedStates.table = jQuery('#survey_completed_states_table').dataTable({
            data: perStateData,
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
                { name: 'state', data: 'state' },
                { name: 'households', data: 'households' },
                { name: 'clusters_total', data: 'clusters' },
                { name: 'clusters_complete', data: 'clustersComplete' },
                { name: 'clusters_reserve', data: 'reserve' },
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

    },
};

surveyCompletedStates.initiate();
