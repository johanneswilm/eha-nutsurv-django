var mappingChecks = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/'
    },
    initiate: function () {
        mappingChecks.createMap();
        dataGetter.addNew(mappingChecks.urls.survey, mappingChecks.updateMap, true);
    },
    createMap: function () {
      var osm = L.tileLayer(map.osmUrl, {
          minZoom: 1,
          maxZoom: 18,
          attribution: false
      });
        mappingChecks.map = L.map('mapping_checks_map', {
            minZoom: 1,
            maxZoom: 18,
            layers: [osm],
            fullscreenControl: true,
            fullscreenControlOptions: {
                position: 'topleft'
            }
        });
        mappingChecks.map.attributionControl.setPrefix('');
    },
    mapMarkers: [],
    updateMap: function (data) {
      var group, incorrectSurveys = [];
        _.each(mappingChecks.mapMarkers, function(marker) {
            // Remove all previous markers
            home.map.removeLayer(marker);
        });
        _.each(data.survey_data, function(survey){
            var icon = survey.correct_area ? map.markers.green : map.markers.red,
            marker = L.marker(survey.location, {icon: icon}),
            popupHTML = "Team: "+survey.team+"<br>"+"Cluster #: "+survey.cluster;
            mappingChecks.mapMarkers.push(marker);
            if (survey.correct_area) {
                marker.addTo(mappingChecks.map).bindPopup(popupHTML);
            } else {
                marker.addTo(mappingChecks.map).bindPopup("ERROR!<br>"+popupHTML);
                incorrectSurveys.push(survey);
            }
        });
        group = new L.featureGroup(mappingChecks.mapMarkers);
        mappingChecks.map.fitBounds(group.getBounds());
        mappingChecks.drawAlerts(incorrectSurveys);
    },

    drawAlerts: function (incorrectSurveys) {
        jQuery('#mapping_checks_alerts_list').empty();
        _.each(incorrectSurveys,function(survey){
            jQuery('#mapping_checks_alerts_list').append(mappingChecks.alertTmp(survey));
        });
    },
    alertTmp: _.template('<li>Incorrect placement! Team <%- team %></li>'),

};

mappingChecks.initiate();
