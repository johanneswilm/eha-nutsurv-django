jQuery(document).ready(function() {

    jQuery('#navbar a').on('click',function(event) {
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
    jQuery('#navbar a:first').click();
    jQuery('#last_update').on('click',
        function(event) {
            event.preventDefault();
            dataGetter.getAll();
        }
    );
});
