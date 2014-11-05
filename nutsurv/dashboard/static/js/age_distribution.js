var ageDistribution = {
    urls : {
        survey: '/static/sample_data/survey.json',
        teams: '/static/sample_data/teams.json',
        states: '/static/sample_data/states.json'
    },
    initiate: function () {
        jQuery('#age_distribution_teams,#age_distribution_states').selectmenu();
        dataGetter.addNew(ageDistribution.urls.teams, ageDistribution.fillTeamsList, false);
        dataGetter.addNew(ageDistribution.urls.states, ageDistribution.fillStatesList, false);
        dataGetter.addNew(ageDistribution.urls.survey, ageDistribution.drawHouseholdAgeDistribution, true);
    },
    fillTeamsList: function (data) {
        _.each(data.teams, function(names, id) {
            jQuery('#age_distribution_teams').append(ageDistribution.teamOptionTmp({id:id,names:names}));
        });
    },
    teamOptionTmp: _.template('<option data-id="<%- id %>"><%- names %></option>'),
    fillStatesList: function (data) {
        _.each(data.states, function(state) {
            jQuery('#age_distribution_states').append(ageDistribution.stateOptionTmp({state:state}));
        });
    },
    stateOptionTmp: _.template('<option><%- state %></option>'),
    drawHouseholdAgeDistribution: function (data) {
        var ages = {}, ageList;
        jQuery('#age_distribution_household_members_chart').empty();
        _.each(data.survey_data, function(survey){
            _.each(survey.members, function(member){
                if (ages.hasOwnProperty(member.age)) {
                    ages[member.age]++;
                } else {
                    ages[member.age] = 1;
                }
            });
        });
        ageList = _.map(ages, function(num, age){ return [parseInt(age),num]; });
        jQuery.plot('#age_distribution_household_members_chart', [ageList], {
    series: {
        color: "#2779AA",
        bars: {
            show: true,
            fillColor: "#D7EBF9",

        },
    }
});
    }
};

ageDistribution.initiate();
