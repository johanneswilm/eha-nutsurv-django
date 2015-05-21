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
    team_lead: $("#team_lead_selector").val(),
    stratum: $("#strata_selector").val(),
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
    "#team_lead_selector",
    '<option value="<%- names.id %>"><%- names.firstName %> <%- names.lastName %></option>',
    data,
    read_querystring()['team_lead']
  );
});

$.get('/dashboard/clustersjsonview/', function (data) {
  fill_selectpicker(
    "#strata_selector",
    '<option value="<%- names.first_admin_level_name %>" ><%- names.cluster_name %></option>',
    data.clusters,
    read_querystring()['stratum']
  );
});

}());
