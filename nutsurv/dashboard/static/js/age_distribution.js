$.get('/dashboard/householdmember/age_distribution/.json' + window.location.search, function (data) {
  var opts = {
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
  };

  var allAgeDistribution = data.ageDistribution.householdMember;

  var childrensAgeDistribution = data.ageDistribution.children.filter(function(o) {
    return o.age_in_months <= 59 && o.age_in_months >= 0;
  });

  jQuery.plot('#age_distribution_children_chart', [childrensAgeDistribution.map(function(o) {
    return [o.age_in_months, o.count];
  })], opts);

  jQuery.plot('#age_distribution_household_members_chart', [allAgeDistribution.map(function(o) {
    return [o.age_in_years, o.count];
  })], opts);

});

teamStrataSelectors.init();
