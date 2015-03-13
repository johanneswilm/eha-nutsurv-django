var home = {
    urls : {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        alerts: '/dashboard/alertsjsonview/',
        teams: '/dashboard/teamsjsonview/'
    },
    initiate: function () {
        jQuery('#home_alerts_download').on('click', home.downloadAlertsCSV);
        jQuery('#home_lastcontact_download').on('click', home.downloadLatestTeamContactsCSV);

        home.createMap();
        dataGetter.addNew(home.urls.survey, home.updateMap, true);

        dataGetter.addNew(home.urls.alerts, home.drawAlerts, true);
        dataGetter.addNew(home.urls.alerts, home.createAlertsCSV, true);

        dataGetter.addNew(home.urls.survey, home.drawLatestContacts, true);
        dataGetter.addNew(home.urls.teams, home.drawLatestContacts, false);

    },
    createMap: function () {
        var osm = L.tileLayer(map.osmUrl, {
            minZoom: 1,
            maxZoom: 18,
            attribution: false
        });
        home.map = L.map('home_map', {
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
            var marker = L.marker(survey.location, {icon: map.markers.green}),
                popupHTML = "Team: "+survey.team+"<br>"+"Cluster #: "+survey.cluster;
            home.mapMarkers.push(marker);
            marker.addTo(home.map).bindPopup(popupHTML);
        });
        group = new L.featureGroup(home.mapMarkers);
        home.map.fitBounds(group.getBounds());
    },
    latestTeamContacts: false,
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
            surveyData = dataGetter.downloads[home.urls.survey].data.survey_data,
            teamData = dataGetter.downloads[home.urls.teams].data.teams;

        jQuery('#home_last_contact_list').empty();
        _.each(surveyData, function (survey) {
            var latestContact = _.find(latestTeamContacts, {team: survey.team});
            if (!latestContact) {
                latestTeamContacts.push({
                    team: survey.team,
                    time: survey.endTime
                });
            } else if (latestContact.time < survey.endTime) {
                latestContact.time = survey.endTime;
            }
        });
        home.latestTeamContacts = _.sortBy(latestTeamContacts, 'time').reverse();
        _.each(home.latestTeamContacts, function(contact){
            jQuery('#home_last_contact_list').append(home.contactTmp({teamNo: contact.team, teamName: teamData[contact.team], time: contact.time}));
        });

    },
    downloadLatestTeamContactsCSV: function () {
        if (!home.latestTeamContacts) {
            return false;
        }
        if (!dataGetter.checkAll([home.urls.teams])) {
            /* Check that all the relative data has been downloaded, else cancel.
            See above. */
            return false;
        }

        var output = 'team ID,team name,timestamp\n',
            teamData = dataGetter.downloads[home.urls.teams].data.teams;

        _.each(home.latestTeamContacts, function(contact){
            output += contact.team+',"'+teamData[contact.team]+'",'+contact.time+'\n';
        });

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'latest_team_contacts.csv'
        );

    },
    contactTmp: _.template('<li>Team <%- teamNo %> (<%- teamName %>):<br> <%- new Date(time) %></li>'),
    drawAlerts: function (data) {

        jQuery('#home_alerts_list').empty();

        _.each(data.alerts, function(alert) {

            if (alert.category === 'map') {
            console.log(alert.message.type);
            }


            var alertTemplate = _.template($('#home-alert-item').html());
            var alertType = home.alertType[alert.message.type];
            jQuery('#home_alerts_list').append(alertTemplate({ message: alert.message, type: alertType }));

        });

    },
    alertType: {
        data_collection_time: {
            title: 'Data Collection Time',
            icon: 'fa-clock-o'
        },
        child_age_displacement: {
            title: 'Child Age Displacement',
            icon: 'fa-child'
        },
        child_age_in_months_ratio: { 
            title: 'Child Age Months Ratio',
            icon: 'fa-child'
        },
        womange_age_14_15_displacement: {
            title: 'Women Aged 14 - 15 Displacement',
            icon: 'fa-female'
        },
        woman_age_4549_5054_displacement: {
            title: 'Women aged 45 to 54 have displacement',
            icon: 'fa-female'
        },
        sex_ratio: { 
            title: 'Sex Ratio',
            icon: 'fa-users'
        },        
        digit_preference: {
            title: 'Digit Preference',
            icon: 'fa-calculator'
        },
        digit_preference_issue: {
            title: 'Digit Preferences Issue',
            icon: 'fa-clipboard'
        },
        time_to_complete_single_survey: {
            title: 'Time to Complete Single Survey',
            icon: 'fa-clock-o'
        },
        daily_data_collection_duration: {
            title: 'Daily Data Collection Duration',
            icon: 'fa-calendar'
        },
        mapping_check_unknown_cluster: {
            title: 'Mapping Check Unknown Cluster',
            icon: 'fa-map-marker'
        },
        mapping_check_unknown_cluster: {
            title: 'Mapping Check Unknown Cluster',
            icon: 'fa-map-marker'
        }
    },
    createAlertsCSV: function (data) {
        var output = 'timestamp,message\n';
        _.each(data.alerts,function(alert){
            output += alert.timestamp + ',' + alert.message + '\n';
        });
        home.alertsCSV = output;
    },
    alertsCSV: false,
    downloadAlertsCSV: function () {
        if (!home.alertsCSV) {
            return false;
        }

        saveAs(
            new Blob( [home.alertsCSV], {type : 'text/csv'}),
            'alerts.csv'
        );

    }
};
home.initiate();
