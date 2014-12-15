var timeOfDataCollection = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        states: '/static/sample_data/states.json'
    },
    initiate: function() {
        jQuery('#time_of_data_collection_teams,#time_of_data_collection_states').selectmenu({
            change: timeOfDataCollection.changeStateOrTeam
        });
        timeOfDataCollection.drawTable();

        dataGetter.addNew(timeOfDataCollection.urls.teams, timeOfDataCollection.fillTeamsList, false);
        dataGetter.addNew(timeOfDataCollection.urls.states, timeOfDataCollection.fillStatesList, false);
        dataGetter.addNew(timeOfDataCollection.urls.survey, timeOfDataCollection.updateTable, true);
    },
    fillTeamsList: function(data) {
        _.each(data.teams, function(names, id) {
            jQuery('#time_of_data_collection_teams').append(timeOfDataCollection.teamOptionTmp({
                id: id,
                names: names
            }));
        });
    },
    teamOptionTmp: _.template('<option value="<%- id %>"><%- names %></option>'),
    changeStateOrTeam: function () {
        var data = dataGetter.downloads[timeOfDataCollection.urls.survey].data,
            team = jQuery('#time_of_data_collection_teams').val(),
            state = jQuery('#time_of_data_collection_states').val();
        timeOfDataCollection.updateCharts(data,team,state);
        timeOfDataCollection.updateTable(data,team,state);
        timeOfDataCollection.updateList(data,team,state);
    },
    fillStatesList: function(data) {
        _.each(data.states.sort(), function(state) {
            jQuery('#time_of_data_collection_states').append(timeOfDataCollection.stateOptionTmp({
                state: state
            }));
        });
    },
    stateOptionTmp: _.template('<option value="<%- state %>" ><%- state %></option>'),
    table: false,
    drawTable: function () {
        timeOfDataCollection.table = jQuery('#time_of_data_collection_table').dataTable({
            paging: false,
            searching: false,
            info: false
        });
    },
    updateTable: function (data, team, state) {

        _.each(data.survey_data, function(survey) {
            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }


        });

        if (timeOfDataCollection.table) {
            timeOfDataCollection.table.fnDestroy();
            timeOfDataCollection.drawTable();
        }
    }
};

timeOfDataCollection.initiate();
