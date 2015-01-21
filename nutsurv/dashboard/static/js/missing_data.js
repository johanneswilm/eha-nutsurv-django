var missingData = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        states: '/dashboard/statesjsonview/',
        qsl: '/dashboard/activequestionnairespecificationview/',
    },
    initiate: function() {
        var selectors = jQuery('#missing_data_teams,#missing_data_states');
        selectors.selectpicker();
        selectors.on('change', missingData.changeStateOrTeam);

        dataGetter.addNew(missingData.urls.teams, missingData.fillTeamsList, false);
        dataGetter.addNew(missingData.urls.states, missingData.fillStatesList, false);
        dataGetter.addNew(missingData.urls.survey, missingData.listChildren, true);
        dataGetter.addNew(missingData.urls.survey, missingData.listWomen, true);
        dataGetter.addNew(missingData.urls.qsl, missingData.listChildren, false);
        dataGetter.addNew(missingData.urls.qsl, missingData.listWomen, false);
    },
    fillTeamsList: function(data) {
        var selector = jQuery('#missing_data_teams');
        _.each(data.teams, function(names, id) {
            selector.append(missingData.teamOptionTmp({
                id: id,
                names: names
            }));
        });
        selector.selectpicker('refresh');
    },
    teamOptionTmp: _.template('<option value="<%- id %>"><%- names %></option>'),
    fillStatesList: function(data) {
        var selector = jQuery('#missing_data_states');
        _.each(data.states.sort(), function(state) {
            selector.append(missingData.stateOptionTmp({
                state: state
            }));
        });
        selector.selectpicker('refresh');
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
    cleanQSL: function (rawQSL) {
        var rawLines= rawQSL.split('\n'),
            cleanedLines = [], QSL = [], indentionLength = 0, i = 0;

        _.each(rawLines, function(rawLine) {
            var lineWoComment=rawLine.split('#')[0].trimRight();
            if (lineWoComment.trim().length > 0) {
                cleanedLines.push(lineWoComment);
            }
        });

        while(indentionLength === 0 && i < cleanedLines.length) {
            if (cleanedLines[i].length - cleanedLines[i].trimLeft().length > 0) {
                indentionLength = cleanedLines[i].length - cleanedLines[i].trimLeft().length;
            }
            i++;
        }

        _.each(cleanedLines, function (cleanedLine) {
            var indentions = (cleanedLine.length - cleanedLine.trimLeft().length)/indentionLength, j, currentArray = QSL;
            for (j=0;j<indentions;j++) {
                currentArray = currentArray[currentArray.length - 1]['children'];
            }
            currentArray.push({key:cleanedLine.trimLeft(),children:[]});
        });
        return QSL;
    },
    qsl: false,
    listWomen: function(data, team, state) {
        if (!dataGetter.checkAll([missingData.urls.survey, missingData.urls.qsl])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        var qsl = dataGetter.downloads[missingData.urls.qsl].data,
            surveyData = dataGetter.downloads[missingData.urls.survey].data.survey_data,
            womenTotal = 0,
            womenDetails = {},
            percentages = [],
            collectableData;

        if (!missingData.qsl) {
            missingData.qsl = missingData.cleanQSL(qsl);
        }

        collectableData = _.findWhere(missingData.qsl,{key:'women:'}).children;

        _.each(collectableData, function(detail) {
            womenDetails[detail.key] = 0;
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
                _.each(collectableData, function(detail) {
                    if (detail.key in woman) {
                        womenDetails[detail.key] ++;
                    }
                });
            });
        });

        if (womenTotal > 0) {
            _.each(collectableData, function(detail) {
                percentages.push({
                    detail: detail.key,
                    percentage: Math.round((womenTotal - womenDetails[detail.key]) / womenTotal * 100 * 10) /10
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
        if (!dataGetter.checkAll([missingData.urls.survey, missingData.urls.qsl])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        var qsl = dataGetter.downloads[missingData.urls.qsl].data,
            surveyData = dataGetter.downloads[missingData.urls.survey].data.survey_data,
            childrenTotal = 0,
            childDetails = {},
            percentages = [],
            collectableData;

        if (!missingData.qsl) {
            missingData.qsl = missingData.cleanQSL(qsl);
        }

        collectableData = _.findWhere(missingData.qsl,{key:'children:'}).children;

        _.each(collectableData, function(detail) {
            childDetails[detail.key] = 0;
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
                _.each(collectableData, function(detail) {
                    if (detail.key in child) {
                        childDetails[detail.key] ++;
                    }
                });
            });
        });

        if (childrenTotal > 0) {
            _.each(collectableData, function(detail) {
                percentages.push({
                    detail: detail.key,
                    percentage: Math.round((childrenTotal - childDetails[detail.key]) / childrenTotal * 100 * 10) /10
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
