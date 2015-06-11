var surveyCompletedStrata = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        clustersPerFirstAdminLevel: '/dashboard/clustersperfirstadminlevelsjsonview/',
        clusterData: '/dashboard/clustersjsonview/',
        firstAdminLevelsWithReserveClusters: '/dashboard/firstadminlevelswithreserveclustersjsonview/'
    },
    initiate: function () {
        dataGetter.addNew(surveyCompletedStrata.urls.survey, surveyCompletedStrata.setupTablePerStratum, true);
        dataGetter.addNew(surveyCompletedStrata.urls.clustersPerFirstAdminLevel, surveyCompletedStrata.setupTablePerStratum, false);
        dataGetter.addNew(surveyCompletedStrata.urls.clusterData, surveyCompletedStrata.setupTablePerStratum, false);
        dataGetter.addNew(surveyCompletedStrata.urls.firstAdminLevelsWithReserveClusters, surveyCompletedStrata.setupTablePerStratum, true);
    },
    downloadData: function () {
        if (!surveyCompletedStrata.table) {
            return false;
        }
        var data = surveyCompletedStrata.table.fnGetData(), i, j, output='';

        output += _.keys(data[0]).join(',');
        output += '\n';

        for (i=0;i<data.length;i++) {
            output += _.values(data[i]).join(',');
            output += '\n';
        }

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'survey_completed_strata.csv'
        );
    },
    table: false,
    setupTablePerStratum: function (data) {
        if (!dataGetter.checkAll([surveyCompletedStrata.urls.survey,surveyCompletedStrata.urls.clustersPerFirstAdminLevel,surveyCompletedStrata.urls.firstAdminLevelsWithReserveClusters, surveyCompletedStrata.urls.clusterData])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        var surveyData = dataGetter.downloads[surveyCompletedStrata.urls.survey].data.survey_data,
            clustersPerFirstAdminLevelData = dataGetter.downloads[surveyCompletedStrata.urls.clustersPerFirstAdminLevel].data.first_admin_levels,
            clusterData = dataGetter.downloads[surveyCompletedStrata.urls.clusterData].data.clusters, // Cluster data not actually used directly in this function, but we need t make sure it is there for clusterInfo
            firstAdminLevelsWithReserveClustersData = dataGetter.downloads[surveyCompletedStrata.urls.firstAdminLevelsWithReserveClusters].data.first_admin_levels,
            perStratumData = [];

        _.each(clustersPerFirstAdminLevelData, function(clusters, stratum) {
            var stratumObject = {
                    stratum: stratum,
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
            if (firstAdminLevelsWithReserveClustersData.indexOf(stratum) === -1) {
                // Reserve clusters not enabled
                stratumObject.reserve = false;
                stratumObject.totalClusters = clusters.standard;
            } else {
                // Reserves have been enabled for this stratum
                stratumObject.reserve = true;
                stratumObject.totalClusters = clusters.standard + clusters.reserve;
            }
            perStratumData.push(stratumObject);
        });

        _.each(surveyData, function(survey) {
            var stratum = clusterInfo.findFirstAdminLevel(survey.cluster),
            stratumObject = _.findWhere(perStratumData, {stratum: stratum});

            if (!stratumObject) {
                console.warn('Unknown cluster: '+survey.cluster);
                return;
            }

            // Increase the number of households surveyed for this stratum by one.
            stratumObject.households++,
            childMembers = _.where(survey.members, {'surveyType': 'child'}),
            womenMembers = _.where(survey.members, {'surveyType': 'women'});

            if (!(survey.cluster in stratumObject.clusterCodes)) {
                stratumObject.clusterCodes[survey.cluster] = 1;
                stratumObject.clusters++;
            } else {
                stratumObject.clusterCodes[survey.cluster]++;
                if (stratumObject.clusterCodes[survey.cluster]===20) {
                    // When there are exactly 20 surveyed households in a given cluster, it is counted as complete.
                    stratumObject.clustersComplete++;
                }
            }


            stratumObject.members += survey.members.length;
            if (survey.members.length < stratumObject.minMembers || stratumObject.minMembers === -1) {
                stratumObject.minMembers = survey.members.length;
            }
            if (survey.members.length > stratumObject.maxMembers) {
                stratumObject.maxMembers = survey.members.length;
            }


            stratumObject.women += womenMembers.length;
            if (womenMembers.length < stratumObject.minWomen || stratumObject.minWomen === -1) {
                stratumObject.minWomen = womenMembers.length;
            }
            if (womenMembers.length > stratumObject.maxWomen) {
                stratumObject.maxWomen = womenMembers.length;
            }


            stratumObject.children += childMembers.length;
            if (childMembers.length < stratumObject.minChildren || stratumObject.minChildren === -1) {
                stratumObject.minChildren = childMembers.length;
            }
            if (childMembers.length > stratumObject.maxChildren) {
                stratumObject.maxChildren = childMembers.length;
            }


        });

        _.each(perStratumData, function(stratumObject) {
            if (stratumObject.households > 0) {
                stratumObject.meanMembers = Math.round(stratumObject.members / stratumObject.households * 10) /10;
                stratumObject.meanWomen = Math.round(stratumObject.women / stratumObject.households * 10) /10;
                stratumObject.meanChildren = Math.round(stratumObject.children / stratumObject.households * 10) /10;
            } else {
                stratumObject.meanMembers = 0;
                stratumObject.meanWomen = 0;
                stratumObject.meanChildren = 0;
            }
            if (stratumObject.minMembers === -1) {
                stratumObject.minMembers = 0;
            }
            if (stratumObject.minChildren === -1) {
                stratumObject.minChildren = 0;
            }
            if (stratumObject.minWomen === -1) {
                stratumObject.minWomen = 0;
            }
            _.each(stratumObject.clusterCodes, function(households, clusterCode) {
                if (households < stratumObject.minHouseholdsPerCluster || stratumObject.minHouseholdsPerCluster === -1) {
                    stratumObject.minHouseholdsPerCluster = households;
                }
                if (households > stratumObject.maxHouseholdsPerCluster) {
                    stratumObject.maxHouseholdsPerCluster = households;
                }
            });
            delete stratumObject.clusterCodes;
            if (stratumObject.minHouseholdsPerCluster === -1) {
                stratumObject.minHouseholdsPerCluster = 0;
            } else {
                stratumObject.meanHouseholdsPerCluster = Math.round(stratumObject.households / stratumObject.clusters * 10) /10;
            }
        });

        if (surveyCompletedStrata.table) {
            // If the table exists already, we destroy it, as it cannot easily be reinitialized.
            surveyCompletedStrata.table.fnDestroy();
        }

        surveyCompletedStrata.table = jQuery('#survey_completed_strata_table').dataTable({
            dom: '<"#survey_completed_strata_download">lfrtip',
            data: perStratumData,
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
                { name: 'stratum', data: 'stratum' },
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

        jQuery('#survey_completed_strata_download').html('<button></button>');
        jQuery('#survey_completed_strata_download button').addClass('btn btn-default dataTables_extra_button');
        jQuery('#survey_completed_strata_download button').text('Download');

        jQuery('#survey_completed_strata_download button').on('click', function (){
            surveyCompletedStrata.downloadData();
        });

    },
};

surveyCompletedStrata.initiate();
