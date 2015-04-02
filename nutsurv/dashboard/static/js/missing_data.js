var missingData = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        firstAdminLevels: '/dashboard/firstadminleveljsonview/',
        qsl: '/dashboard/activequestionnairespecificationview/',
    },
    initiate: function() {
        var selectors = jQuery('#missing_data_teams,#missing_data_strata');
        selectors.selectpicker();
        selectors.on('change', missingData.changeStratumOrTeam);

        dataGetter.addNew(missingData.urls.teams, missingData.fillTeamsList, false);
        dataGetter.addNew(missingData.urls.firstAdminLevels, missingData.fillStrataList, false);
        dataGetter.addNew(missingData.urls.survey, missingData.listChildren, true);
        dataGetter.addNew(missingData.urls.survey, missingData.listWomen, true);
        dataGetter.addNew(missingData.urls.survey, missingData.listHouseholdMembers, false);
        dataGetter.addNew(missingData.urls.qsl, missingData.listChildren, false);
        dataGetter.addNew(missingData.urls.qsl, missingData.listWomen, false);
        dataGetter.addNew(missingData.urls.qsl, missingData.listHouseholdMembers, false);

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
    fillStrataList: function(data) {
        var selector = jQuery('#missing_data_strata');
        _.each(data.first_admin_levels.sort(), function(stratum) {
            selector.append(missingData.stratumOptionTmp({
                stratum: stratum
            }));
        });
        selector.selectpicker('refresh');
    },
    stratumOptionTmp: _.template('<option value="<%- stratum %>" ><%- stratum %></option>'),
    changeStratumOrTeam: function() {
        var data = dataGetter.downloads[missingData.urls.survey].data,
            team = jQuery('#missing_data_teams').val(),
            stratum = jQuery('#missing_data_strata').val();
        missingData.listChildren(data, team, stratum);
        missingData.listWomen(data, team, stratum);
        missingData.listHouseholdMembers(data, team, stratum);
    },
    listTmp: _.template('<li><span class="item"><%- detail.replace(/([A-Z])/g, \' $1\').replace(/^./, function(str){ return str.toUpperCase(); }).replace("_"," ") %>:</span><span class="description"><%= percentage %>%</span></li>'),
    qsl: false,
    listWomen: function(data, team, stratum) {
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
            collectableData = [
                "breastfeeding",
                "muac",
                "height",
                "weight",
                "age",
                "pregnant",
                "edema",
            ], womenQSL;

        if (!missingData.qsl) {
            missingData.qsl = parseQSL(qsl);
        }

        womenQSL = _.findWhere(missingData.qsl,{key:'women:'});

        if (womenQSL) {
            _.each(womenQSL.children, function (detail) {
                collectableData.push(detail.key);
            });
        }

        _.each(collectableData, function(detail) {
            womenDetails[detail] = 0;
        });

        _.each(surveyData, function(survey) {

            var womenMembers;

            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && stratum != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }

            _.each(survey.members, function(member) {
                if (member.gender == 'F' && member.age > 14 && member.age < 50) {
                    womenTotal++;
                }
            });

            womenMembers = _.where(survey.members, {'surveyType': 'women'});
            _.each(womenMembers, function(woman) {
                _.each(collectableData, function(detail) {
                    if (detail in woman || detail in woman.survey) {
                        womenDetails[detail] ++;
                    }
                });
            });
        });

        if (womenTotal > 0) {
            _.each(collectableData, function(detail) {
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
    listChildren: function(data, team, stratum) {
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
            collectableData = [
                "muac",
                "weight",
                "heightType",
                "edema",
                "birthDate",
                "ageInMonths",
                "height"
            ],
            childrenQSL;

        if (!missingData.qsl) {
            missingData.qsl = parseQSL(qsl);
        }

        childrenQSL = _.findWhere(missingData.qsl,{key:'children:'});

        if (childrenQSL) {
            _.each(childrenQSL.children, function (detail) {
                collectableData.push(detail.key);
            });
        }

        _.each(collectableData, function(detail) {
            childDetails[detail] = 0;
        });

        _.each(surveyData, function(survey) {

            var childMembers;

            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && stratum != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }

            _.each(survey.members, function(member) {
                if (member.age < 6) {
                    childrenTotal++;
                }
            });

            childMembers = _.where(survey.members, {'surveyType': 'child'});

            _.each(childMembers, function(child) {
                _.each(collectableData, function(detail) {
                    if (detail in child || detail in child.survey) {
                        childDetails[detail] ++;
                    }
                });
            });
        });

        if (childrenTotal > 0) {
            _.each(collectableData, function(detail) {
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
    },
    listHouseholdMembers: function(data, team, state) {

        if (!dataGetter.checkAll([missingData.urls.survey, missingData.urls.qsl])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See home.js. */
            return false;
        }
        var qsl = dataGetter.downloads[missingData.urls.qsl].data,
            surveyData = dataGetter.downloads[missingData.urls.survey].data.survey_data,
            householdMembersTotal = 0,
            householdMembersDetails = {},
            percentages = [],
            collectableData = [
                "age",
                "gender"
            ],
            householdMembersQSL;

        if (!missingData.qsl) {
            missingData.qsl = parseQSL(qsl);
        }

        householdMembersQSL = _.findWhere(missingData.qsl,{key:'household members:'});

        if (householdMembersQSL) {
            _.each(householdMembersQSL.children, function (detail) {
                collectableData.push(detail.key);
            });
        }

        _.each(collectableData, function(detail) {
            householdMembersDetails[detail] = 0;
        });

        _.each(surveyData, function(survey) {

            var householdMembers;

            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }

            _.each(survey.members, function(member) {
                householdMembersTotal++;
            });

            householdMembers = survey.members;

            _.each(householdMembers, function(hhMember) {
                _.each(collectableData, function(detail) {
                    if (detail in hhMember || detail in hhMember.survey) {
                        householdMembersDetails[detail] ++;
                    }
                });
            });
        });

        if (householdMembersTotal > 0) {
            _.each(collectableData, function(detail) {
                percentages.push({
                    detail: detail,
                    percentage: Math.round((householdMembersTotal - householdMembersDetails[detail]) / householdMembersTotal * 100 * 10) /10
                });
            });
        }

        percentages = _.sortBy(percentages, 'detail');


        jQuery('#missing_data_household_members_list').empty();
        _.each(percentages, function(percentage) {
            jQuery('#missing_data_household_members_list').append(missingData.listTmp(percentage));
        });
    }
};
missingData.initiate();
