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
    var updateMap = function(surveys) {
        var group;

        mapMarkers.clearLayers();

        _.each(surveys, function(survey) {
            if (!survey.location || !survey.location.coordinates) {
                return;
            }
            var marker = L.marker(survey.location.coordinates, {
                    icon: mapConfig.markers.green
                }),
                popupHTML = "Team ID: " + survey.teamLead + "<br>" + "Cluster #: " + survey.cluster;
            marker.bindPopup(popupHTML);
            mapMarkers.addLayer(marker);
        });
        map.fitBounds(mapMarkers.getBounds());
    };

    map.attributionControl.setPrefix('');
    map.addLayer(mapMarkers);
    $.get('/dashboard/surveymap/.json', updateMap);
});
