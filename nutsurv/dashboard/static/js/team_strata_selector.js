teamStrataSelectors = {

  read_querystring: function() {
    function decode(uri) {
      return window.decodeURIComponent(uri || '').replace(/\+/g, ' ');
    }
    var qs = {};
    window.location.search.substring(1).split('&').forEach(function(el) {
      el = el.split('=');
      qs[el[0]] = decode(el[1]);
    });
    return qs;
  },

  change_querystring: function() {
    window.location.search = '?' + jQuery.param({
      team_lead: $("#team_lead_selector").val(),
      stratum: $("#strata_selector").val(),
    });
  },

  fill_selectpicker : function(sel, template, data, selected_value, callback) {
    var el = jQuery(sel);
    var tmpl = _.template(template);
    _.each(data, function(datum, id) {
        if (_.isObject(datum)) {
          el.append(tmpl({id: id, names: datum}));
        } else {
          el.append(tmpl({first_admin_level_name: datum}));
        }
    });
    el.selectpicker();
    el.selectpicker('val', selected_value);

    el.on('change', callback || this.change_querystring);
  },

  init: function(callback) {
    var scope = this;
    $.get('/dashboard/teammembers/', function (data) {
      scope.fill_selectpicker(
        "#team_lead_selector",
        '<option value="<%- names.id %>"><%- names.id %></option>',
        data,
        scope.read_querystring()['team_lead'],
        callback
      );
    });

    $.get('/dashboard/firstadminleveljsonview/', function (data) {
      scope.fill_selectpicker(
        "#strata_selector",
        '<option value="<%- first_admin_level_name %>" ><%- first_admin_level_name %></option>',
        data.first_admin_levels,
        scope.read_querystring()['stratum'],
        callback
      );
    });
  }
};
