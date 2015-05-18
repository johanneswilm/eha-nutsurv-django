(function() {

function read_querystring() {
  var qs = {};
  window.location.search.substring(1).split('&').forEach(function(el) {
    el = el.split('=');
    qs[el[0]] = el[1];
  });
  return qs;
}

function change_querystring() {
  window.location.search = '?' + jQuery.param({
    team_lead: $("#missing_data_teams").val(),
    stratum: $("#missing_data_strata").val(),
  });
}

function fill_selectpicker(sel, template, data, selected_value) {
  var el = jQuery(sel);
  var tmpl = _.template(template);
  _.each(data, function(names, id) {
      el.append(tmpl({id: id, names: names}));
  });
  el.selectpicker();
  el.selectpicker('val', selected_value);
  el.on('change', change_querystring);
}

$.get('/dashboard/teammembers/', function (data) {
  fill_selectpicker(
    "#missing_data_teams",
    '<option value="<%- names.id %>"><%- names.firstName %> <%- names.lastName %></option>',
    data,
    read_querystring()['team_lead']
  );
});

$.get('/dashboard/clustersjsonview/', function (data) {
  fill_selectpicker(
    "#missing_data_strata",
    '<option value="<%- names.first_admin_level_name %>" ><%- names.cluster_name %></option>',
    data.clusters,
    read_querystring()['stratum']
  );
});

}());

