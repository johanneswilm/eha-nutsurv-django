var home = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        alerts: '/dashboard/alerts/',
        teams: '/dashboard/teamsjsonview/'
    },
    initiate: function() {
        jQuery('#home_alerts_download').on('click', home.downloadAlertsCSV);
        jQuery('#home_lastcontact_download').on('click', home.downloadLatestTeamContactsCSV);

        home.createMap();
        dataGetter.addNew(home.urls.survey, home.updateMap, true);

        dataGetter.addNew(home.urls.alerts, home.drawAlerts, true);
        dataGetter.addNew(home.urls.alerts, home.createAlertsCSV, true);

        dataGetter.addNew(home.urls.survey, home.drawLatestContacts, true);
        dataGetter.addNew(home.urls.teams, home.drawLatestContacts, false);

    },
    mapMarkers: L.markerClusterGroup(),
    createMap: function() {
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

        home.map.addLayer(home.mapMarkers);

    },
    updateMap: function(data) {
        var group;

        home.mapMarkers.clearLayers();

        _.each(data.survey_data, function(survey) {
            var marker = L.marker(survey.location, {
                    icon: map.markers.green
                }),
                popupHTML = "Team: " + survey.team + "<br>" + "Cluster #: " + survey.cluster;
            marker.bindPopup(popupHTML);
            home.mapMarkers.addLayer(marker);
        });


        home.map.fitBounds(home.mapMarkers.getBounds());

    },
    latestTeamContacts: [],
    drawLatestContacts: function(data) {
        if (!dataGetter.checkAll([home.urls.survey, home.urls.teams])) {
            /* Check that all the relative data has been downloaded, else cancel.
            This function will be called for each piece of arriving data, so it
            will be executed once the last piece of data arrives.
            This is the way to make a specific dashboardview function depend on
            the arrival of several pieces of data. */
            return false;
        }
        var latestTeamContacts = [];
        var surveyData = dataGetter.downloads[home.urls.survey].data.survey_data;
        var teamData = dataGetter.downloads[home.urls.teams].data.teams;

        jQuery('#home_last_contact_list').empty();

        _.each(surveyData, function(survey) {
            // Limit to only 7 entries
            if (latestTeamContacts.length < 7) {
              var latestContact = _.find(latestTeamContacts, {
                  team: survey.team
              });
              if (!latestContact) {
                  latestTeamContacts.push({ 
                      team: survey.team,
                      time: survey.endTime
                  });
              } else if (latestContact.time < survey.endTime) {
                  latestContact.time = survey.endTime;
              }
            }
        });

        home.latestTeamContacts = _.sortBy(latestTeamContacts, 'time').reverse();

        _.each(home.latestTeamContacts, function(contact) {
            jQuery('#home_last_contact_list').append(home.contactTmp({
                teamNo: contact.team,
                teamName: teamData[contact.team],
                time: contact.time
            }));
        });

    },
    downloadLatestTeamContactsCSV: function() {
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

        _.each(home.latestTeamContacts, function(contact) {
            output += contact.team + ',"' + teamData[contact.team] + '",' + contact.time + '\n';
        });

        saveAs(
            new Blob([output], {
                type: 'text/csv'
            }),
            'latest_team_contacts.csv'
        );

    },
    contactTmp: _.template($('#home-last-contacted-item').html()),
    drawAlerts: function(data) {

        var alert_list = $('#home_alerts_list').find('div.list');
        alert_list.empty();

        _.each(data, function(alert) {
            var alertTemplate = _.template($('#home-alert-item').html());
            alert_list.append(alertTemplate(_.assign(alert, home.alertType[alert.type])));
        });

        home.drawAlertFilter();
        home.paginateAlerts();
        home.contactModalAlerts();
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
        woman_age_14_15_displacement: {
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
        }
    },
    drawAlertFilter: function() {

        var type_html = '<option value="all">All Alerts</option>';
        _.each(home.alertType, function(type, key) {
            type_html += '<option value="' + key + '">' + type.title + '</option>\n';
        });

        // Append & Bootstrap Select
        $('#home_alerts_filter_type').append(type_html);
        
    },
    paginateAlerts: function() {

        // Paginate with list.js
        var paginateAlertList = new List('home_alerts_list', {
            valueNames: ['alert_title', 'alert_team_name', 'alert_type'],
            page: 10,
            plugins: [ ListPagination({}) ] 
        });

    	// Sort By Category
    	$('#home_alerts_filter_type').change(function() {			
    		var this_type = $(this).val().toString();
    		if (this_type == 'all') {
    	        paginateAlertList.filter();
    	    }
    	    else {            
    	        paginateAlertList.filter(function(item) {
    	            if (item.values().alert_type == this_type) {
    	                return true;
    	            }
    	            else {
    	                return false;
    	            }
    	        });
    	    }
            return false;
      	});

    },
    contactModalAlerts: function() {

        // Show Modal
        $('#contact-team-modal').on('show.bs.modal', function(event) {

            var button = $(event.relatedTarget);
            var modal = $(this);

            modal.find('#btn-contact-team-contacted').attr('href', button.data('url'));

            // Get "id" of alert and lookup in loaded data
            var id = button.data('id');
            var alert = _.findWhere(dataGetter.downloads['/dashboard/alerts/'].data, {id: id});

            // Prep data
            var personTemplate = _.template($('#contact-team-item').html());
            var personGender = { F: "Female", M: "Male" };
            alert.teamLead.gender = personGender[alert.teamLead.gender];

            // Inject HTML into modal
            var team_html = personTemplate(alert.teamLead);
            modal.find('ul.contact-team-list').html(team_html);

            $('#btn-contact-team-contacted').attr('href', alert.url)
        });

        // Mark As Completed
        $('#btn-contact-team-contacted').on('click', function(event) {
      		$.ajax({
      			url: $(event.target).attr('href'),
      			type: 'PATCH',
                data: {completed: true},
      			dataType: 'json',
      		  	success: function(result) {
                    // Hide Alert Item
                    $('#alert-item-' + result.id).fadeOut(function() {
                        $(this).remove();
                    });
                }
            });
        });

    },
    createAlertsCSV: function(data) {
        var output = 'created,text\n';
        _.each(data.alerts, function(alert) {
            output += alert.created + ',' + alert.text + '\n';
        });
        home.alertsCSV = output;
    },
    alertsCSV: false,
    downloadAlertsCSV: function() {
        if (!home.alertsCSV) {
            return false;
        }

        saveAs(
            new Blob([home.alertsCSV], {
                type: 'text/csv'
            }),
            'alerts.csv'
        );

    }
};
home.initiate();