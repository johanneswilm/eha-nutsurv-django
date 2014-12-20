var ageDistribution = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        states: '/static/sample_data/states.json'
    },
    initiate: function() {
        var selectors = jQuery('#age_distribution_teams,#age_distribution_states');
        selectors.selectpicker();
        selectors.on('change', ageDistribution.changeStateOrTeam);

        ageDistribution.drawHouseholdAgeDistribution();
        ageDistribution.drawChildrenAgeDistribution();
        dataGetter.addNew(ageDistribution.urls.teams, ageDistribution.fillTeamsList, false);
        dataGetter.addNew(ageDistribution.urls.states, ageDistribution.fillStatesList, false);
        dataGetter.addNew(ageDistribution.urls.survey, ageDistribution.updateHouseholdAgeDistribution, true);
        dataGetter.addNew(ageDistribution.urls.survey, ageDistribution.updateChildrenAgeDistribution, true);
    },
    fillTeamsList: function(data) {
        var selector = jQuery('#age_distribution_teams');
        _.each(data.teams, function(names, id) {
            selector.append(ageDistribution.teamOptionTmp({
                id: id,
                names: names
            }));
        });
        selector.selectpicker('refresh');
    },
    teamOptionTmp: _.template('<option value="<%- id %>"><%- names %></option>'),
    fillStatesList: function(data) {
        var selector = jQuery('#age_distribution_states');
        _.each(data.states.sort(), function(state) {
            selector.append(ageDistribution.stateOptionTmp({
                state: state
            }));
        });
        selector.selectpicker('refresh');
    },
    stateOptionTmp: _.template('<option value="<%- state %>" ><%- state %></option>'),
    changeStateOrTeam: function () {
        var data = dataGetter.downloads[ageDistribution.urls.survey].data,
            team = jQuery('#age_distribution_teams').val(),
            state = jQuery('#age_distribution_states').val();
        ageDistribution.updateHouseholdAgeDistribution(data,team,state);
        ageDistribution.updateChildrenAgeDistribution(data,team,state);
    },
    householdAgeDistributionPlot: false,
    drawHouseholdAgeDistribution: function() {
        ageDistribution.householdAgeDistributionPlot = jQuery.plot('#age_distribution_household_members_chart', [], {
            series: {
                color: "#2779AA",
                bars: {
                    show: true,
                    fillColor: "#D7EBF9",
                },
            },
            yaxis: {
                tickDecimals: 0,
                min: 0
            },
            xaxis: {
                tickDecimals: 0,
                min: 0
            }
        });
    },
    childrenAgeDistributionPlot: false,
    drawChildrenAgeDistribution: function() {
        ageDistribution.childrenAgeDistributionPlot = jQuery.plot('#age_distribution_children_chart', [], {
            series: {
                color: "#2779AA",
                bars: {
                    show: true,
                    fillColor: "#D7EBF9",
                },
            },
            yaxis: {
                tickDecimals: 0,
                min: 0
            },
            xaxis: {
                tickDecimals: 0,
                min: 0
            }
        });
    },
    updateHouseholdAgeDistribution: function(data, team, state) {
        var ages = {},
            ageList;
        _.each(data.survey_data, function(survey) {
            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }
            _.each(survey.members, function(member) {
                if (ages.hasOwnProperty(member.age)) {
                    ages[member.age] ++;
                } else {
                    ages[member.age] = 1;
                }
            });
        });
        ageList = _.map(ages, function(num, age) {
            return [parseInt(age), num];
        });
        ageDistribution.householdAgeDistributionPlot.setData([ageList]);
        ageDistribution.householdAgeDistributionPlot.setupGrid();
        ageDistribution.householdAgeDistributionPlot.draw();
    },
    updateChildrenAgeDistribution: function(data, team, state) {
        var ages = {},
            ageList;
        _.each(data.survey_data, function(survey) {
            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }
            if (survey.hasOwnProperty('child_surveys')) {
                _.each(survey.child_surveys, function(child) {
                    var childAge = new Date(new Date()-new Date(child.birthdate)),
                        months = (childAge.getYear()-70)*12+childAge.getMonth();
                    if (ages.hasOwnProperty(months)) {
                        ages[months] ++;
                    } else {
                        ages[months] = 1;
                    }
                });
            }
        });
        ageList = _.map(ages, function(num, age) {
            return [parseInt(age), num];
        });
        ageDistribution.childrenAgeDistributionPlot.setData([ageList]);
        ageDistribution.childrenAgeDistributionPlot.setupGrid();
        ageDistribution.childrenAgeDistributionPlot.draw();
    }
};

ageDistribution.initiate();
