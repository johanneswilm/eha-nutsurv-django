var home = {
    urls : {
        survey: '/static/sample_data/survey.json',
        alerts: '/static/sample_data/alerts.json',
        teams: '/static/sample_data/teams.json'
    },
    initiate: function () {
        home.drawMap();
        dataGetter.addNew(home.urls.survey, home.updateMap, true);

        dataGetter.addNew(home.urls.alerts, home.drawAlerts, true);

        dataGetter.addNew(home.urls.survey, home.drawLatestContacts, true);
        dataGetter.addNew(home.urls.teams, home.drawLatestContacts, false);
    },
    drawMap: function () {
        var osm = L.tileLayer(map.osmUrl, {
            minZoom: 1,
            maxZoom: 18,
            attribution: false
        });
        home.map = L.map('home_map', {
            center: [10.9049100685, 7.7650104523],
            zoom: 6,
            minZoom: 1,
            maxZoom: 18,
            layers: [osm],
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
        if (!dataGetter.checkAll([home.urls.survey,home.urls.teams])) {
            /* Check that all the relative data has been downloaded, else cancel.
            This function will be called for each piece of arriving data, so it
            will be executed once the last piece of data arrives.
            This is the way to make a specific dashboardview function depend on
            the arrival of several pieces of data. */
            return false;
        }
        var latestTeamContacts = [],
            surveyData = dataGetter.downloads[home.urls.survey].data,
            teamData = dataGetter.downloads[home.urls.teams].data;

        jQuery('#home_last_contact_list').empty();
        _.each(surveyData.survey_data, function (survey) {
            var latestContact = _.find(latestTeamContacts, {team: survey.team});
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
