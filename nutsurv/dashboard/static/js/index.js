jQuery(function() {
  jQuery( "#tabs" ).tabs({
     beforeLoad: function( event, ui ) {
        if ( ui.tab.data( "loaded" ) ) {
          event.preventDefault();
          return;
        }

        ui.jqXHR.success(function() {
          ui.tab.data( "loaded", true );
        });
      }
  });
  jQuery('#last_update').button({icons: {
      primary: "ui-icon-arrowrefresh-1-w"
    }}).click(
    function( event ) {
      event.preventDefault();
      dataGetter.getAll();
    }
  );
});
