$.get(window.location.pathname, function (data) {
  $('table').dataTable({
    data: data,
    paging: false,
    searching: false,
    ordering:  false,
    columns: [
     {data: 'id'},
     {data: 'created'},
     {data: 'url',
      render: function (data, type, full, meta ) {
        return '<a class="btn btn-sm btn-primary" href="'+data+'"><i class="fa fa-eye"></i> Room details</a>';
      }},
    ],
  });
});
