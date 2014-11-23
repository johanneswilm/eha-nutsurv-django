var missingData = {
    urls: {
        survey: '/static/sample_data/survey.json',
        teams: '/static/sample_data/teams.json',
        states: '/static/sample_data/states.json',
        collectableData: '/static/sample_data/collectable_data.json'
    },
    initiate: function() {
        jQuery('#missing_data_teams,#missing_data_states').selectmenu({
            change: missingData.changeStateOrTeam
        });
        dataGetter.addNew(missingData.urls.teams, missingData.fillTeamsList, false);
        dataGetter.addNew(missingData.urls.states, missingData.fillStatesList, false);
        dataGetter.addNew(missingData.urls.survey, missingData.listChildren, true);
        dataGetter.addNew(missingData.urls.survey, missingData.listWomen, true);
        dataGetter.addNew(missingData.urls.collectableData, missingData.listChildren, false);
        dataGetter.addNew(missingData.urls.collectableData, missingData.listWomen, false);
    },
    fillTeamsList: function(data) {
        _.each(data.teams, function(names, id) {
            jQuery('#missing_data_teams').append(missingData.teamOptionTmp({
                id: id,
                names: names
            }));
        });
    },
    teamOptionTmp: _.template('<option value="<%- id %>"><%- names %></option>'),
    fillStatesList: function(data) {
        _.each(data.states.sort(), function(state) {
            jQuery('#missing_data_states').append(missingData.stateOptionTmp({
                state: state
            }));
        });
    },
    stateOptionTmp: _.template('<option value="<%- state %>" ><%- state %></option>'),
    changeStateOrTeam: function() {
        var data = dataGetter.downloads[missingData.urls.survey].data,
            team = jQuery('#missing_data_teams').val(),
            state = jQuery('#missing_data_states').val();
        missingData.listChildren(data, team, state);
        missingData.listWomen(data, team, state);
    },
    listTmp: _.template('<li><span class="item"><%- detail.charAt(0).toUpperCase() + detail.slice(1).replace("_"," ") %>:</span><span class="description"><%= percentage %>%</span></li>'),
    listWomen: function(data, team, state) {
        if (!dataGetter.checkAll([missingData.urls.survey, missingData.urls.collectableData])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        var collectableData = dataGetter.downloads[missingData.urls.collectableData].data.collectable_data,
            surveyData = dataGetter.downloads[missingData.urls.survey].data.survey_data,
            womenTotal = 0,
            womenDetails = {},
            percentages = [];

        _.each(collectableData.women, function(detail) {
            womenDetails[detail] = 0;
        });

        _.each(surveyData, function(survey) {

            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }

            _.each(survey.members, function(member) {
                if (member.gender == 'F' && member.age > 14 && member.age < 50) {
                    womenTotal++;
                }
            });

            _.each(survey.women_surveys, function(woman) {
                _.each(collectableData.women, function(detail) {
                    if (detail in woman) {
                        womenDetails[detail] ++;
                    }
                });
            });
        });

        if (womenTotal > 0) {
            _.each(collectableData.women, function(detail) {
                percentages.push({
                    detail: detail,
                    percentage: Math.round((womenTotal - womenDetails[detail]) / womenTotal * 100 * 10) /10
                });
            });
        }

        percentages = _.sortBy(percentages, 'detail');

        jQuery('#missing_data_women_list').empty();

        _.each(percentages, function(percentage) {
            jQuery('#missing_data_women_list').append(missingData.listTmp(percentage));
        });
    },
    listChildren: function(data, team, state) {
        if (!dataGetter.checkAll([missingData.urls.survey, missingData.urls.collectableData])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        var collectableData = dataGetter.downloads[missingData.urls.collectableData].data.collectable_data,
            surveyData = dataGetter.downloads[missingData.urls.survey].data.survey_data,
            childrenTotal = 0,
            childDetails = {},
            percentages = [];

        _.each(collectableData.children, function(detail) {
            childDetails[detail] = 0;
        });

        _.each(surveyData, function(survey) {

            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }

            _.each(survey.members, function(member) {
                if (member.age < 5) {
                    childrenTotal++;
                }
            });

            _.each(survey.child_surveys, function(child) {
                _.each(collectableData.children, function(detail) {
                    if (detail in child) {
                        childDetails[detail] ++;
                    }
                });
            });
        });

        if (childrenTotal > 0) {
            _.each(collectableData.children, function(detail) {
                percentages.push({
                    detail: detail,
                    percentage: Math.round((childrenTotal - childDetails[detail]) / childrenTotal * 100 * 10) /10
                });
            });
        }

        percentages = _.sortBy(percentages, 'detail');

        jQuery('#missing_data_children_list').empty();
        _.each(percentages, function(percentage) {
            jQuery('#missing_data_children_list').append(missingData.listTmp(percentage));
        });
    }
};
missingData.initiate();
