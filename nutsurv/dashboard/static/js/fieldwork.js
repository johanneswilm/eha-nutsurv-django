var mappingChecks = {
    initiate: function () {
        $('#fieldwork_alerts_download').on('click', mappingChecks.downloadAlertsCSV);
        mappingChecks.createMap();
        $.get('/dashboard/alerts/', mappingChecks.updateMap);
    },
    createMap: function () {
      var osm = L.tileLayer(mapConfig.osmUrl, {
          minZoom: 1,
          maxZoom: 18,
          attribution: false
      });
        mappingChecks.map = L.map('fieldwork_map', {
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
    dateFormatter: new Intl.DateTimeFormat("en-GB"),
    errorFormatter: function(error) {
        error = error.replace(/_/g, " ").replace("mapping check", "").trim();
        return error.charAt(0).toUpperCase() + error.slice(1);
    },
    popupTmp: _.template('Error: <b><%- this.errorFormatter(type) %></b>' +
        '<br>Survey date: <b><%- this.dateFormatter.format(new Date(created)) %></b>' +
        '<br>Team lead: <b><%- teamLead.firstName+" "+teamLead.lastName %></b>' +
        '<% if (clusterId) { %><br>Cluster #: <b><%- clusterId %><% } %></b>'),
    updateMap: function (data) {

      var group, incorrectSurveys = [],
        mapAlerts = _.where(data.results, {category:'map'});
        if (mapAlerts.length > 0) {
            _.each(mappingChecks.mapMarkers, function(marker) {
                // Remove all previous markers
                home.map.removeLayer(marker);
            });

            _.each(mapAlerts, function(mapAlert){
                var marker;
                if (mapAlert.hasOwnProperty('location')) {
                    marker = L.marker(mapAlert.location, {icon: mapConfig.markers.red}),
                    mappingChecks.mapMarkers.push(marker),
                    marker.addTo(mappingChecks.map).bindPopup(mappingChecks.popupTmp(mapAlert));
                }
                incorrectSurveys.push(mapAlert);

            });
            mappingChecks.incorrectSurveys = incorrectSurveys;
            group = new L.featureGroup(mappingChecks.mapMarkers);
            mappingChecks.map.fitBounds(group.getBounds());
            mappingChecks.drawAlerts(mappingChecks.incorrectSurveys);
        } else {
          mappingChecks.drawAlerts([{type:'no_alerts'}]);
        }

    },
    downloadAlertsCSV: function () {
        if (!mappingChecks.incorrectSurveys) {
            return false;
        }

        var output = 'team_id,cluster_id\n';

        _.each(mappingChecks.incorrectSurveys, function (survey) {
            output += survey.teamLead.id + ',' + survey.clusterId + '\n';
        });

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'mapping_alerts.csv'
        );
    },
    drawAlerts: function (incorrectSurveys) {
        jQuery('#fieldwork_alerts_list').empty();
        _.each(incorrectSurveys,function(survey){
            jQuery('#fieldwork_alerts_list').append(mappingChecks.alertTmp[survey.type](survey));
        });
    },
    alertTmp: {
        'mapping_check_wrong_location': _.template('<li>Wrong location! Team leader <%- teamLead.id %></li>'),
        'mapping_check_unknown_cluster': _.template('<li>Unknown cluster! Team leader <%- teamLead.id %></li>'),
        'mapping_check_missing_location': _.template('<li>Missing location! Team leader <%- teamLead.id %></li>'),
        'mapping_check_missing_cluster_id': _.template('<li>Missing cluster ID! Team leader <%- teamLead.id %></li>'),
        'mapping_check_wrong_location_first_admin_level': _.template('<li>Wrong location (first admin level)! Team leader <%- teamLead.id %></li>'),
        'no_alerts': _.template('<li>Currently there are no map alerts</li>')
    }

};

mappingChecks.initiate();
