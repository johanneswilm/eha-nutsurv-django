jQuery(function() {

    jQuery('#tabs a').click(function(e) {
        var tab = jQuery(this),
            loadurl = tab.attr('href'),
            target = tab.attr('data-target');
        if (!tab.hasClass('loaded')) {
            tab.addClass('loaded');
            jQuery.get(loadurl, function(data) {
                jQuery(target).html(data);
            });
        }

        tab.tab('show');
        return false;
    });
    jQuery('#tabs a:first').click();
    jQuery('#last_update').button({
        icons: {
            primary: "ui-icon-arrowrefresh-1-w"
        }
    }).click(
        function(event) {
            event.preventDefault();
            dataGetter.getAll();
        }
    );
});
