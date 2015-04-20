(function() {

$('select').selectpicker();

function mean(arr) {
  return _.reduce(arr, function(memo, num) {
    return memo + num;
  }, 0) / arr.length;
}

function is_all_data_present(obj) {
  return obj.height != undefined && obj.weight != undefined && obj.muac != undefined;
}

var format_methods = {
  'weight': function(v) { return v + '&nbsp;kg'; },
  'height': function(v) { return v + '&nbsp;cm'; },
  'muac': function(v) { return '⌀&nbsp;' + v + '&nbsp;cm'; },
  'checkmark': function(v) { return '—'; },
}

function render_from_view_as(view_as) {
   return function(obj) {
      if (
        obj == undefined ||
        obj[view_as] == null ||
        obj[view_as] == undefined ||
        obj[view_as] == NaN ||
        obj[view_as] == Infinity ||
        obj[view_as] == -Infinity) {
        return '—';
      }
      return format_methods[view_as](obj[view_as]);
   };
}

var render_methods = {
  'checkmark': function(obj) {
     if (!obj) { return '—'; }
     return '<i class="fa fa-check" style="color: greenyellow;"></i>';
   },
  'json': function(obj) {
     if (obj == undefined) { return '—'; }
     return JSON.stringify(obj);
   },
  'weight': render_from_view_as('weight'),
  'height': render_from_view_as('height'),
  'muac': render_from_view_as('muac'),
  'all': function(obj) {
     if (obj == undefined) { return '—'; }
     var d = [];
     if (obj.height != undefined) { d.push(format_methods['height'](obj.height)); }
     if (obj.weight != undefined) { d.push(format_methods['weight'](obj.weight)); }
     if (obj.muac != undefined) { d.push(format_methods['muac'](obj.muac)); }
     return d.join(", ");
   },
};

var add_family_member_columns = _.once(function(member_columns) {
  $('th[data-column-name="total_members"]').after(
    _.map(member_columns, function(column) {
      return (
        '<th data-column-name="' + column.data + '">' +
          '<abbr title="Family member ' + column.index + '">' +
            column.index +
          '</abbr>' +
        '</th>'
      );
    })
  );
});

var the_table;

function set_table(survey_data, opts) {

  var expected_total_members = opts.expected_total_members || 10;
  var view_as = opts.view_as;

  var total_members = _.max(_.map(_.pluck(survey_data, 'members'), function(a) {
    return a.length;
  }));

  var columns = [
     {
        data: 'team',
        width: '40%',
        render: function(members) {
          return _.map(members, function(member) {
            return '<b>' + member.firstName + "&nbsp;" + member.lastName + '</b>';
          }).join(', ');
        },
     }
  ];

  if (expected_total_members === 1) {
    $('th[data-column-name="total_members"]').hide()
  } else {
    columns.push({
      data: 'total_members',
    })
  }

  var member_columns = _.map(_.range(1, expected_total_members+1), function(i) {
    return {
      'index': i,
      'data': 'member_' + i,
      'render': render_methods[view_as],
    };
  });

  columns = columns.concat(member_columns);

  if (opts.show_all_data_present === false) {
    $('th[data-column-name="all_data_present"]').hide()
  } else {
    columns.push({
      data: 'all_data_present',
      render: render_methods['checkmark'],
    })
  }

  if (opts.show_mean === false) {
    $('th[data-column-name="mean"]').hide()
  } else {
    columns.push({
      data: 'mean',
      render: format_methods[view_as],
    })
  }

  if (opts.show_max === false) {
    $('th[data-column-name="max"]').hide()
  } else {
    columns.push({
      data: 'max',
      render: format_methods[view_as],
    })
  }

  add_family_member_columns(member_columns);

  if (expected_total_members === 1) {
    $('th[data-column-name="member_1"] abbr').hide()
  }

  var result = _.map(survey_data, function(su, survey_index) {

    var all_data_present = su.members.length > 0 && su.members.length === expected_total_members;
    var data = {
      'team': [su.teamLead, su.teamAssistant, su.teamAnthropometrist],
      'total_members': su.members.length,
      'mean': mean(_.pluck(su.members, view_as)),
      'max': _.max(_.pluck(su.members, view_as)),
    };
    _.each(su.members, function(member, member_index) {
      data['member_' + (member_index+1)] = member;
      if (!is_all_data_present(member)) {
        all_data_present = false;
      }
    });

    data['all_data_present'] = all_data_present;

    return data;
  });

  the_table = $('table').DataTable({
    data: result,
    paging: false,
    searching: false,
    ordering:  false,
    columns: columns,
  });

  if (_.all(_.pluck(result, 'all_data_present'))) {
    $("#survey_completed_tabs li.disabled").removeClass("disabled");
  } else {
    $("#survey_completed_tabs li.disabled a").removeAttr("href");
  }
};

var survey_data;

var MODES = {
  'tool_standardization': {view_as: 'all', expected_total_members: 1, show_max: false, show_mean: false, show_all_data_present: false},
  'all_data_present':     {view_as: 'checkmark', show_max: false, show_mean: false},
  'height':               {view_as: 'height', show_all_data_present: false},
  'weight':               {view_as: 'weight', show_all_data_present: false},
  'muac':                 {view_as: 'muac', show_all_data_present: false},
};

$(document).ready(function() {
  $.get(window.location.pathname + '?member_detail', function (data) {
    survey_data = data.surveys;
    var mode_name = (window.location.search || "all_data_present").replace("?", "");
    $("li#" + mode_name).addClass("active")
    set_table(survey_data, MODES[mode_name]);
  });
});

})();
