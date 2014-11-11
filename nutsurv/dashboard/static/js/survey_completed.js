var surveyCompleted = {
    urls : {
        survey: '/static/sample_data/survey.json',
        clustersPerState: '/static/sample_data/clusters_per_state.json',
        clustersPerTeam: '/static/sample_data/clusters_per_team.json',
        statesWithReserveClusters: '/static/sample_data/states_with_reserve_clusters.json',
    },
    initiate: function () {
        dataGetter.addNew(surveyCompleted.urls.survey, surveyCompleted.drawTable, true);
        dataGetter.addNew(surveyCompleted.urls.clustersPerState, surveyCompleted.drawTable, false);
        dataGetter.addNew(surveyCompleted.urls.statesWithReserveClusters, surveyCompleted.drawTable, true);
        dataGetter.addNew(surveyCompleted.urls.clustersPerState, surveyCompleted.fillStatesList, false);
        dataGetter.addNew(surveyCompleted.urls.clustersPerTeam, surveyCompleted.fillTeamsList, false);
    },
    drawTable: function (data) {
        if (!dataGetter.checkAll([surveyCompleted.urls.survey,surveyCompleted.urls.clustersPerState,surveyCompleted.urls.statesWithReserveClusters])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        surveyData = dataGetter.downloads[home.urls.survey].data;
        clustersPerStateData = dataGetter.downloads[surveyCompleted.urls.clustersPerState].data;
        statesWithReserveClustersData = dataGetter.downloads[surveyCompleted.urls.statesWithReserveClusters].data;
    },

};

surveyCompleted.initiate();
