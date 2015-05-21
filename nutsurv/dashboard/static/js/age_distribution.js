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
  jQuery.plot('#age_distribution_children_chart', [data.ageDistribution.children.map(function(o) {
    return [o.age_in_months, o.count];
  })], opts);

  jQuery.plot('#age_distribution_household_members_chart', [data.ageDistribution.householdMember.map(function(o) {
    return [o.age_in_years, o.count];
  })], opts);

})
