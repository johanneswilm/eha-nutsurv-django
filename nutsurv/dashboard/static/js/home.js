$(function() {
    var osm = L.tileLayer(mapConfig.osmUrl, {
        minZoom: 1,
        maxZoom: 18,
        attribution: false
    });
    var map = L.map('home_map', {
        minZoom: 1,
        maxZoom: 18,
        layers: [osm],
        fullscreenControl: true,
        fullscreenControlOptions: {
            position: 'topleft'
        }
    });
    var mapMarkers = L.markerClusterGroup();
    var updateMap = function(data) {
        var group;

        mapMarkers.clearLayers();

        _.each(data.survey_data, function(survey) {
            var marker = L.marker(survey.location, {
                    icon: mapConfig.markers.green
                }),
                popupHTML = "Team leader: " + survey.team + "<br>" + "Cluster #: " + survey.cluster;
            marker.bindPopup(popupHTML);
            mapMarkers.addLayer(marker);
        });
        map.fitBounds(mapMarkers.getBounds());
    };

    map.attributionControl.setPrefix('');
    map.addLayer(mapMarkers);
    $.get('/dashboard/aggregatesurveydatajsonview/', updateMap);
});
