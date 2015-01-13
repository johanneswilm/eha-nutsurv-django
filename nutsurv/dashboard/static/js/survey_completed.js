jQuery('#survey_completed_tabs a').click(function(e) {
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
jQuery('#survey_completed_tabs a:first').click();
