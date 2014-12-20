var timeOfDataCollection = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        states: '/static/sample_data/states.json'
    },
    initiate: function() {
        var selectors = jQuery('#time_of_data_collection_teams,#time_of_data_collection_states');
        selectors.selectpicker();
        selectors.on('change', timeOfDataCollection.changeStateOrTeam);

        dataGetter.addNew(timeOfDataCollection.urls.teams, timeOfDataCollection.fillTeamsList, false);
        dataGetter.addNew(timeOfDataCollection.urls.states, timeOfDataCollection.fillStatesList, false);
        dataGetter.addNew(timeOfDataCollection.urls.survey, timeOfDataCollection.drawTable, true);
    },
    fillTeamsList: function(data) {
        var selector = jQuery('#time_of_data_collection_teams');
        _.each(data.teams, function(names, id) {
            selector.append(timeOfDataCollection.teamOptionTmp({
                id: id,
                names: names
            }));
        });
        selector.selectpicker('refresh');
    },
    teamOptionTmp: _.template('<option value="<%- id %>"><%- names %></option>'),
    fillStatesList: function(data) {
        var selector = jQuery('#time_of_data_collection_states');
        _.each(data.states.sort(), function(state) {
            selector.append(timeOfDataCollection.stateOptionTmp({
                state: state
            }));
        });
        selector.selectpicker('refresh');
    },
    stateOptionTmp: _.template('<option value="<%- state %>" ><%- state %></option>'),
    changeStateOrTeam: function () {
        var data = dataGetter.downloads[timeOfDataCollection.urls.survey].data,
            team = jQuery('#time_of_data_collection_teams').val(),
            state = jQuery('#time_of_data_collection_states').val();
        timeOfDataCollection.drawTable(data,team,state);
    },
    table: false,
    drawTable: function (data, team, state) {
        var datesTimes = {},
            totalSurveyTime = 0,
            averageSurveyTime,
            totalWorkTime = 0,
            totalStartTime = 0,
            totalEndTime = 0,
            tableData = {
                "per interview, N" : 0,
                "per interview, max" : "",
                "per interview, min" : "",
                "per interview, average" : "",
                "daily collection, N" : 0,
                "daily collection, max" : "",
                "daily collection, min" : "",
                "daily collection, average" : "",
                "daily collection start, max" : "",
                "daily collection start, min" : "",
                "daily collection start, average" : "",
                "daily collection end, max" : "",
                "daily collection end, min" : "",
                "daily collection end, average" : "",
            };


        _.each(data.survey_data, function(survey) {
            var surveyDate, startTimeArray,endTimeArray, startTime, endTime, surveyTime, surveyTimeString;
            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }

            if(survey.hasOwnProperty('start_time') && survey.hasOwnProperty('end_time')) {
                surveyTime = new Date(survey.end_time) - new Date(survey.start_time);
                surveyTimeString = parseInt(surveyTime/60000) + ':' + String('0'+parseInt(surveyTime%60000/1000)).substr(-2);
                if (tableData["per interview, min"] > surveyTimeString || tableData["per interview, min"]==='') {
                    tableData["per interview, min"] = surveyTimeString;
                }
                if (tableData["per interview, max"] < surveyTimeString) {
                    tableData["per interview, max"] = surveyTimeString;
                }

                tableData["per interview, N"]++;
                totalSurveyTime += surveyTime;
                startTimeArray = survey.start_time.split('T');
                endTimeArray = survey.end_time.split('T');

                if (startTimeArray[0]===endTimeArray[0]) {
                    // start and end time are on the same date
                    surveyDate = startTimeArray[0];
                    startTime = startTimeArray[1];
                    endTime = endTimeArray[1];
                    if (datesTimes.hasOwnProperty(surveyDate)) {
                        if (datesTimes[surveyDate].start > startTime) {
                            datesTimes[surveyDate].start = startTime;
                        }
                        if (datesTimes[surveyDate].end < endTime) {
                            datesTimes[surveyDate].end = endTime;
                        }
                    } else {
                        datesTimes[surveyDate] = {
                            start: startTime,
                            end: endTime
                        }
                    }

                } else {
                    // TODO: start and end time are on different dates, we should handle this somehow.
                }

            }

        });

        if(tableData["per interview, N"]>0) {
            averageSurveyTime = parseInt(totalSurveyTime/tableData["per interview, N"]);
            tableData["per interview, average"] = parseInt(averageSurveyTime/60000) + ':' + String('0'+parseInt(averageSurveyTime%60000/1000)).substr(-2);
        }

        _.each(datesTimes, function(surveyTimes) {
            var startTime = new Date('1970-01-01T'+surveyTimes.start).getTime(),
                endTime = new Date('1970-01-01T'+surveyTimes.end).getTime(),
                workTime = endTime - startTime,
                workTimeString = new Date(workTime).toISOString().split('T')[1].split('.')[0];
            totalStartTime += startTime;
            totalEndTime += endTime;
            if (tableData["daily collection, min"] > workTimeString || tableData["daily collection, min"]==='') {
                tableData["daily collection, min"] = workTimeString;
            }
            if (tableData["daily collection, max"] < workTimeString) {
                tableData["daily collection, max"] = workTimeString;
            }
            totalWorkTime += workTime;
            tableData["daily collection, N"]++;
            if (tableData["daily collection start, min"] > surveyTimes.start || tableData["daily collection start, min"]==='') {
                tableData["daily collection start, min"] = surveyTimes.start;
            }
            if (tableData["daily collection start, max"] < surveyTimes.start) {
                tableData["daily collection start, max"] = surveyTimes.start;
            }
            if (tableData["daily collection end, min"] > surveyTimes.end || tableData["daily collection end, min"]==='') {
                tableData["daily collection end, min"] = surveyTimes.end;
            }
            if (tableData["daily collection end, max"] < surveyTimes.end) {
                tableData["daily collection end, max"] = surveyTimes.end;
            }
        });
        if (tableData["daily collection, N"]>0) {
            tableData["daily collection, average"] = new Date(totalWorkTime/tableData["daily collection, N"]).toISOString().split('T')[1].split('.')[0];
            tableData["daily collection start, average"] = new Date(totalStartTime/tableData["daily collection, N"]).toISOString().split('T')[1].split('.')[0];
            tableData["daily collection end, average"] = new Date(totalEndTime/tableData["daily collection, N"]).toISOString().split('T')[1].split('.')[0];

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
                { "searchable": false, data: function(){return '';}, orderable: false},
                { name: 'per interview, N', data: 'per interview, N', orderable: false},
                { name: 'per interview, max', data: 'per interview, max', orderable: false},
                { name: 'per interview, average', data: 'per interview, average', orderable: false},
                { name: 'per interview, min', data: 'per interview, min', orderable: false},
                { name: 'daily collection, N', data: 'daily collection, N', orderable: false},
                { name: 'daily collection, max', data: 'daily collection, max', orderable: false},
                { name: 'daily collection, average', data: 'daily collection, average', orderable: false},
                { name: 'daily collection, min', data: 'daily collection, min', orderable: false},
                { name: 'daily collection start, max', data: 'daily collection start, max', orderable: false},
                { name: 'daily collection start, average', data: 'daily collection start, average', orderable: false},
                { name: 'daily collection start, min', data: 'daily collection start, min', orderable: false},
                { name: 'daily collection end, max', data: 'daily collection end, max', orderable: false},
                { name: 'daily collection end, average', data: 'daily collection end, average', orderable: false},
                { name: 'daily collection end, min', data: 'daily collection end, min', orderable: false}
            ],
            "order": [[ 1, "asc" ]]
        });
    }
};

timeOfDataCollection.initiate();
