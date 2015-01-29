jQuery(document).ready(function() {

    // Dropdowns
    $('.dropdown-toggle').dropdown();

    // Main Panel Navigation
    jQuery('#navbar a').on('click',function(event) {
        var tab = jQuery(this),
            loadurl = tab.attr('href'),
            target = tab.attr('data-target');


        if (tab.hasClass('dropdown-toggle') && !tab.parent().hasClass('open')) {
            console.log('yolo dropdown is open');
        } else {
            console.log('awww it is not open');
        }

        if (!tab.hasClass('loaded') && !tab.hasClass('dropdown-toggle')) {
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
