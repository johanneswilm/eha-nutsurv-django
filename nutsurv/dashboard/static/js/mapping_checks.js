var mappingChecks = {
    urls : {
        alerts: '/dashboard/alerts/'
    },
    initiate: function () {
        jQuery('#mapping_checks_alerts_download').on('click', mappingChecks.downloadAlertsCSV);

        mappingChecks.createMap();
        dataGetter.addNew(mappingChecks.urls.alerts, mappingChecks.updateMap, true);
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
    incorrectSurveys: false,
    popupTmp: _.template('ERROR!<br>Team <%- team_name %>(<%- team_id%>)<% if (cluster_id) { %><br>Cluster #: <%- cluster_id %><% } %>'),
    updateMap: function (data) {
      var group, incorrectSurveys = [],

        mapAlerts = _.where(data, {category:'map'});
        _.each(mappingChecks.mapMarkers, function(marker) {
            // Remove all previous markers
            home.map.removeLayer(marker);
        });

        _.each(mapAlerts, function(mapAlert){
            var marker;
            if (mapAlert.hasOwnProperty('location')) {
                marker = L.marker(mapAlert.location, {icon: map.markers.red}),
                mappingChecks.mapMarkers.push(marker),
                marker.addTo(mappingChecks.map).bindPopup(mappingChecks.popupTmp(mapAlert));
            }
            incorrectSurveys.push(mapAlert);

        });
        mappingChecks.incorrectSurveys = incorrectSurveys;
        group = new L.featureGroup(mappingChecks.mapMarkers);
        mappingChecks.map.fitBounds(group.getBounds());
        mappingChecks.drawAlerts(mappingChecks.incorrectSurveys);
    },
    downloadAlertsCSV: function () {
        if (!mappingChecks.incorrectSurveys) {
            return false;
        }

        var output = 'team_id,cluster_id\n';

        _.each(mappingChecks.incorrectSurveys, function (survey) {
            output += survey.team_id + ',' + survey.cluster_id + '\n';
        });

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'mapping_alerts.csv'
        );
    },
    drawAlerts: function (incorrectSurveys) {
        jQuery('#mapping_checks_alerts_list').empty();
        _.each(incorrectSurveys,function(survey){
            jQuery('#mapping_checks_alerts_list').append(mappingChecks.alertTmp[survey.type](survey));
        });
    },
    alertTmp: {
        'mapping_check_wrong_location': _.template('<li>Wrong location! Team <%- team_name %> (<%- team_id %>)</li>'),
        'mapping_check_unknown_cluster': _.template('<li>Unknown cluster! Team <%- team_name %> (<%- team_id %>)</li>'),
        'mapping_check_missing_location': _.template('<li>Missing location! Team <%- team_name %> (<%- team_id %>)</li>'),
        'mapping_check_missing_cluster_id': _.template('<li>Missing cluster ID! Team <%- team_name %> (<%- team_id %>)</li>')
    }

};

mappingChecks.initiate();
