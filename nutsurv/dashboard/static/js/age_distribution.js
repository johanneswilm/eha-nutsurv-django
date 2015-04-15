var ageDistribution = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        firstAdminLevels: '/dashboard/firstadminleveljsonview/'
    },
    initiate: function() {
        var selectors = jQuery('#age_distribution_teams,#age_distribution_strata');
        selectors.selectpicker();
        selectors.on('change', ageDistribution.changeStratumOrTeam);
        //jQuery('#age_distribution_teams,#age_distribution_strata').selectmenu({
        //    change: ageDistribution.changeStratumOrTeam
        //})
        jQuery('#age_distribution_households_download').on('click', ageDistribution.downloadHouseholdAgeListCSV);
        jQuery('#age_distribution_children_download').on('click', ageDistribution.downloadChildrenAgeListCSV);

        ageDistribution.drawHouseholdAgeDistribution();
        ageDistribution.drawChildrenAgeDistribution();
        dataGetter.addNew(ageDistribution.urls.teams, ageDistribution.fillTeamsList, false);
        dataGetter.addNew(ageDistribution.urls.firstAdminLevels, ageDistribution.fillStrataList, false);
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
    fillStrataList: function(data) {
        var selector = jQuery('#age_distribution_strata');
        _.each(data.first_admin_levels.sort(), function(stratum) {
            selector.append(ageDistribution.stratumOptionTmp({
                stratum: stratum
            }));
        });
        selector.selectpicker('refresh');
    },
    stratumOptionTmp: _.template('<option value="<%- stratum %>" ><%- stratum %></option>'),
    changeStratumOrTeam: function () {
        var data = dataGetter.downloads[ageDistribution.urls.survey].data,
            team = jQuery('#age_distribution_teams').val(),
            stratum = jQuery('#age_distribution_strata').val();
        ageDistribution.updateHouseholdAgeDistribution(data,team,stratum);
        ageDistribution.updateChildrenAgeDistribution(data,team,stratum);
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
    householdAgeList: false,
    updateHouseholdAgeDistribution: function(data, team, stratum) {
        var ages = {};

        _.each(data.survey_data, function(survey) {
            if (team && team > -1 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && stratum != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }
            _.each(survey.members, function(member) {
                if (member.hasOwnProperty('age')) {
                  if (member.age == 999) {
                    console.warn('Member age: 999');
                    return;
                  }
                    if (ages.hasOwnProperty(member.age)) {
                        ages[member.age] ++;
                    } else {
                        ages[member.age] = 1;
                    }
                } else {
                    console.warn('No member age defined');
                    return;
                }
            });
        });
        ageDistribution.householdAgeList = _.map(ages, function(num, age) {
            return [parseInt(age), num];
        });
        ageDistribution.householdAgeDistributionPlot.setData([ageDistribution.householdAgeList]);
        ageDistribution.householdAgeDistributionPlot.setupGrid();
        ageDistribution.householdAgeDistributionPlot.draw();
    },
    downloadHouseholdAgeListCSV: function () {
        if (!ageDistribution.householdAgeList) {
            return false;
        }
        var output = 'age (years),count\n';

        _.each(ageDistribution.householdAgeList, function(age) {
            output += age[0] + ',' + age[1] + '\n';
        });

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'households_age_list.csv'
        );
    },
    childrenAgeList: false,
    updateChildrenAgeDistribution: function(data, team, stratum) {
        var ages = {};

        _.each(data.survey_data, function(survey) {
            var childSurveys;

            if (team && team > -1 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && strata != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }


            childSurveys = _.pluck(_.where(survey.members, {'surveyType': 'child'}), 'survey');


            _.each(childSurveys, function(child) {
                var childAge, months;
                if (child.hasOwnProperty('birthDate')) {
                    childAge = new Date(new Date()-new Date(child.birthDate));
                    months = (childAge.getYear()-70)*12+childAge.getMonth();
                } else if (child.hasOwnProperty('ageInMonths')) {
                    months = child.ageInMonths;
                    if (months == 99) {
                        console.warn('Child age: 99');
                        return;
                    }
                } else {
                    console.warn('No child age defined');
                    return;
                }

                if (ages.hasOwnProperty(months)) {
                    ages[months] ++;
                } else {
                    ages[months] = 1;
                }
            });

        });
        ageDistribution.childrenAgeList = _.map(ages, function(num, age) {
            return [parseInt(age), num];
        });
        ageDistribution.childrenAgeDistributionPlot.setData([ageDistribution.childrenAgeList]);
        ageDistribution.childrenAgeDistributionPlot.setupGrid();
        ageDistribution.childrenAgeDistributionPlot.draw();
    },
    downloadChildrenAgeListCSV: function () {
        if (!ageDistribution.childrenAgeList) {
            return false;
        }
        var output = 'age (months),count\n';

        _.each(ageDistribution.childrenAgeList, function(age) {
            output += age[0] + ',' + age[1] + '\n';
        });

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'children_age_list.csv'
        );
    },
};

ageDistribution.initiate();
