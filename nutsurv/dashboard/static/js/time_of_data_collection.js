var timeOfDataCollection = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
    },
    initiate: function() {
        teamStrataSelectors.init(this.changeStratumOrTeam);
        dataGetter.addNew(timeOfDataCollection.urls.survey, timeOfDataCollection.drawTable, true);
    },
    changeStratumOrTeam: function () {
        var data = dataGetter.downloads[timeOfDataCollection.urls.survey].data,
            team = jQuery('#team_lead_selector').val(),
            stratum = jQuery('#strata_selector').val();
        timeOfDataCollection.drawTable(data,team,stratum);
    },
    table: false,
    drawTable: function (data, team, stratum) {
        var datesTimes = {},
            totalSurveyTime = 0,
            medianSurveyTime,
            totalWorkTime = 0,
            totalStartTime = 0,
            totalEndTime = 0,
            tableData = {
                "per interview, N" : 0,
                "per interview, max" : "",
                "per interview, min" : "",
                "per interview, median" : "",
                "daily collection, N" : 0,
                "daily collection, max" : "",
                "daily collection, min" : "",
                "daily collection, median" : "",
                "daily collection start, max" : "",
                "daily collection start, min" : "",
                "daily collection start, median" : "",
                "daily collection end, max" : "",
                "daily collection end, min" : "",
                "daily collection end, median" : "",
            };

        var surveyTimes = [];

        _.each(data.survey_data, function(survey) {
            var surveyStartDate, surveyEndDate, startTime, endTime, surveyTime, surveyTimeString,
              surveyStart, endHours;
            if (team && team > -1 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && stratum != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }

            if(survey.hasOwnProperty('startTime') && survey.hasOwnProperty('endTime')) {
                surveyStart = moment(survey.startTime);
                surveyEnd = moment(survey.endTime);
                surveyTime = surveyEnd - surveyStart;
                surveyTimeString = moment(surveyTime).format('HH:mm:ss');
                if (tableData["per interview, min"] > surveyTimeString || tableData["per interview, min"]==='') {
                    tableData["per interview, min"] = surveyTimeString;
                }
                if (tableData["per interview, max"] < surveyTimeString) {
                    tableData["per interview, max"] = surveyTimeString;
                }

                tableData["per interview, N"]++;
                totalSurveyTime += surveyTime;
                surveyTimes.push(surveyTime);
                surveyStartDate = surveyStart.format('YYYY-MM-DD');
                surveyEndDate = surveyEnd.format('YYYY-MM-DD');
                startTime = surveyStart.format('HH:mm:ss');
                endTime = surveyEnd.format('HH:mm:ss');


                if (surveyStartDate!=surveyEndDate) {
                    // TODO: Data collection start and end are not on the same day.
                    console.warn('Survey started and ended on different dates: '+surveyStartDate+' '+surveyEndDate);
                    return;
                }

                if (datesTimes.hasOwnProperty(surveyStartDate)) {
                    if (datesTimes[surveyStartDate].start > startTime) {
                        datesTimes[surveyStartDate].start = startTime;
                    }
                    if (datesTimes[surveyStartDate].end < endTime) {
                        datesTimes[surveyStartDate].end = endTime;
                    }
                } else {
                    datesTimes[surveyStartDate] = {
                        start: startTime,
                        end: endTime
                    }
                }



            }

        });

        if(tableData["per interview, N"]>0) {
            tableData["per interview, median"] = moment(_.median(surveyTimes)).format('HH:mm:ss');
        }

        var allStartTimes = [];
        var allEndTimes = [];
        var allWorkTimes = [];

        _.each(datesTimes, function(surveyTimes) {
            var startTime = moment('1970-01-01T'+surveyTimes.start),
                endTime = moment('1970-01-01T'+surveyTimes.end),
                workTime = moment(endTime - startTime),
                workTimeString = workTime.format('HH:mm:ss'),
                startTimeString = startTime.format('HH:mm:ss'),
                endTimeString = endTime.format('HH:mm:ss');

            totalStartTime += startTime;
            allStartTimes.push(startTime);
            totalEndTime += endTime;
            allEndTimes.push(endTime);
            totalWorkTime += workTime;
            allWorkTimes.push(workTime);

            tableData["daily collection, N"]++;

            if (tableData["daily collection, min"] > workTimeString || tableData["daily collection, min"]==='') {
                tableData["daily collection, min"] = workTimeString;
            }
            if (tableData["daily collection, max"] < workTimeString) {
                tableData["daily collection, max"] = workTimeString;
            }
            if (tableData["daily collection start, min"] > startTimeString || tableData["daily collection start, min"]==='') {
                tableData["daily collection start, min"] = startTimeString;
            }
            if (tableData["daily collection start, max"] < startTimeString) {
                tableData["daily collection start, max"] = startTimeString;
            }
            if (tableData["daily collection end, min"] > endTimeString || tableData["daily collection end, min"]==='') {
                tableData["daily collection end, min"] = endTimeString;
            }
            if (tableData["daily collection end, max"] < endTimeString) {
                tableData["daily collection end, max"] = endTimeString;
            }
        });

        if (tableData["daily collection, N"]>0) {
            tableData["daily collection, median"] = moment(_.median(allWorkTimes)).format('HH:mm:ss');
            tableData["daily collection start, median"] = moment(_.median(allStartTimes)).format('HH:mm:ss');
            tableData["daily collection end, median"] = moment(_.median(allEndTimes)).format('HH:mm:ss');

            // TODO: Figure out if we really should show the same value thrice
            tableData["daily collection start, N" ] = tableData["daily collection end, N"] = tableData["daily collection, N"];
        }

        if (timeOfDataCollection.table) {
            timeOfDataCollection.table.fnDestroy();
        }

        timeOfDataCollection.table = jQuery('#time_of_data_collection_table').dataTable({
            paging: false,
            searching: false,
            bSort: false,
            info: false,
            responsive: {
                        details: {
                            renderer: function ( api, rowIdx ) {
                                // Select hidden columns for the given row
                                var data = api.cells( rowIdx, ':hidden' ).eq(0).map( function ( cell ) {
                                    var header = jQuery( api.column( cell.column ).header() );
                                    return '<tr>'+
                                            '<td>'+
                                                header.attr('data-column-name')+':'+
                                            '</td> '+
                                            '<td>'+
                                                api.cell( cell ).data()+
                                            '</td>'+
                                        '</tr>';
                                } ).toArray().join('');

                                return data ?
                                    $('<table/>').append( data ) :
                                    false;
                            },
                        }
                    },
            data : [tableData],
            columns: [
                { name: 'per interview, N', data: 'per interview, N', orderable: false},
                { name: 'per interview, max', data: 'per interview, max', orderable: false},
                { name: 'per interview, median', data: 'per interview, median', orderable: false},
                { name: 'per interview, min', data: 'per interview, min', orderable: false},
                { name: 'daily collection, N', data: 'daily collection, N', orderable: false},
                { name: 'daily collection, max', data: 'daily collection, max', orderable: false},
                { name: 'daily collection, median', data: 'daily collection, median', orderable: false},
                { name: 'daily collection, min', data: 'daily collection, min', orderable: false},
                { name: 'daily collection start, max', data: 'daily collection start, max', orderable: false},
                { name: 'daily collection start, median', data: 'daily collection start, median', orderable: false},
                { name: 'daily collection start, min', data: 'daily collection start, min', orderable: false},
                { name: 'daily collection end, max', data: 'daily collection end, max', orderable: false},
                { name: 'daily collection end, median', data: 'daily collection end, median', orderable: false},
                { name: 'daily collection end, min', data: 'daily collection end, min', orderable: false}
            ],
            "order": [[ 1, "asc" ]]
        });
    }
};

timeOfDataCollection.initiate();
