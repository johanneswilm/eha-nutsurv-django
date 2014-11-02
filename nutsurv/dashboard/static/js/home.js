var home = {
    initiate: function () {
        home.drawMap();
        dataGetter.addNew('/static/sample_data/survey.json', home.drawSurvey);
        dataGetter.addNew('/static/sample_data/alerts.json', home.drawAlerts);
    },
    drawSurvey: function (data) {
        home.updateMap(data);
        home.drawLatestContacts(data);
    },
    drawMap: function () {
        home.map = L.map('home_map', {
            center: [10.9049100685, 7.7650104523],
            zoom: 6,
            minZoom: 1,
            maxZoom: 18,
            layers: [map.osm],
            fullscreenControl: true,
            fullscreenControlOptions: {
                position: 'topleft'
            }
        });
        home.map.attributionControl.setPrefix('');

    },
    mapMarkers: [],
    updateMap: function (data) {
      var group;
        _.each(home.mapMarkers, function(marker) {
            // Remove all previous markers
            home.map.removeLayer(marker);
        });
        _.each(data.survey_data, function(survey){
            var marker = L.marker(survey.location, {icon: map.markers.green});
            home.mapMarkers.push(marker);
            marker.addTo(home.map).bindPopup("Team: "+survey.team);
        });
        group = new L.featureGroup(home.mapMarkers);
        home.map.fitBounds(group.getBounds());
    },
    drawLatestContacts: function (data) {
        // We assume teams don't constantly change, so teams will only be redrawn if survey data changes.
        jQuery.get('/static/sample_data/teams.json', function (teamData) {
            var latestTeamContacts = [];
            jQuery('#home_last_contact_list').empty();
            _.each(data.survey_data, function (survey) {
                latestContact = _.find(latestTeamContacts, {team: survey.team});
                if (!latestContact) {
                    latestTeamContacts.push({
                        team: survey.team,
                        time: survey.end_time
                    });
                } else if (latestContact.time < survey.end_time) {
                    latestContact.time = survey.end_time;
                }
            });
            latestTeamContacts = _.sortBy(latestTeamContacts, 'time').reverse();
            _.each(latestTeamContacts, function(contact){
                jQuery('#home_last_contact_list').append(home.contactTmp({teamNo: contact.team, teamName: teamData.teams[contact.team], time: contact.time}));
            });
        });
    },
    contactTmp: _.template('<li>Team <%- teamNo %> (<%- teamName %>):<br> <%= new Date(time) %></li>'),
    drawAlerts: function (data) {
        jQuery('#home_alerts_list').empty();
        _.each(data.alerts,function(alert){
            jQuery('#home_alerts_list').append(home.alertTmp({alert:alert}));
        });
    },
    alertTmp: _.template('<li><%- alert %></li>'),


};

home.initiate();
