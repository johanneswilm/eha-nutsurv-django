$.get('/dashboard/householdmember/age_distribution/.json' + window.location.search, function (data) {
  var opts = {
      grid: {
          hoverable: true
      },
      tooltip: {
          show: true,
          content: "Age: %x, Count: %y"
      },
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
    return o.ageInMonths <= 59 && o.ageInMonths >= 0;
  });

  jQuery.plot('#age_distribution_children_chart', [childrensAgeDistribution.map(function(o) {
    return [o.ageInMonths, o.count];
  })], opts);

  jQuery.plot('#age_distribution_household_members_chart', [allAgeDistribution.map(function(o) {
    return [o.age_in_years, o.count];
  })], opts);

});

teamStrataSelectors.init();
