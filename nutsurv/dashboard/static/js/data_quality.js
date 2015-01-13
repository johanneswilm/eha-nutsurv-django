var dataQuality = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        states: '/static/sample_data/states.json'
    },
    initiate: function() {
        var selectors = jQuery('#data_quality_teams,#data_quality_states');
        selectors.selectpicker();
        selectors.on('change', dataQuality.changeStateOrTeam);

        dataQuality.drawCharts();
        dataQuality.drawTable();

        dataGetter.addNew(dataQuality.urls.teams, dataQuality.fillTeamsList, false);
        dataGetter.addNew(dataQuality.urls.states, dataQuality.fillStatesList, false);
        dataGetter.addNew(dataQuality.urls.survey, dataQuality.updateCharts, true);
        dataGetter.addNew(dataQuality.urls.survey, dataQuality.updateTable, true);
        dataGetter.addNew(dataQuality.urls.survey, dataQuality.updateList, true);
    },
    fillTeamsList: function(data) {
        var selector = jQuery('#data_quality_teams');
        _.each(data.teams, function(names, id) {
            selector.append(dataQuality.teamOptionTmp({
                id: id,
                names: names
            }));
        });
        selector.selectpicker('refresh');
    },
    teamOptionTmp: _.template('<option value="<%- id %>"><%- names %></option>'),
    fillStatesList: function(data) {
        var selector = jQuery('#data_quality_states');
        _.each(data.states.sort(), function(state) {
            selector.append(dataQuality.stateOptionTmp({
                state: state
            }));
        });
        selector.selectpicker('refresh');
    },
    stateOptionTmp: _.template('<option value="<%- state %>" ><%- state %></option>'),
    changeStateOrTeam: function () {
        var data = dataGetter.downloads[dataQuality.urls.survey].data,
            team = jQuery('#data_quality_teams').val(),
            state = jQuery('#data_quality_states').val();
        dataQuality.updateCharts(data,team,state);
        dataQuality.updateTable(data,team,state);
        dataQuality.updateList(data,team,state);
    },
    drawCharts: function() {
        var options = {
            yaxis: {
                tickDecimals: 0,
                min: 0
            },
            xaxis: {
                tickDecimals: 0,
                min: -6,
                max: 6
            }
        }, muacOptions = {
            yaxis: {
                tickDecimals: 0,
            },
            xaxis: {
                tickDecimals: 0,
            }
        };

        dataQuality.WHZDataQualityPlot = jQuery.plot('#data_quality_whz_chart', [], options);
        dataQuality.HAZDataQualityPlot = jQuery.plot('#data_quality_haz_chart', [], options);
        // Only hide tabs after canvases have been drawn on them.
        setTimeout(
            function() {
                jQuery('#data_quality_chart_tabs_HAZ').addClass('tab-pane');
            },
            0
        );
        dataQuality.WAZDataQualityPlot = jQuery.plot('#data_quality_waz_chart', [], options);
        setTimeout(
            function() {
                jQuery('#data_quality_chart_tabs_WAZ').addClass('tab-pane');
            },
            0
        );
        dataQuality.MUACDataQualityPlot = jQuery.plot('#data_quality_muac_chart', [], muacOptions);
        setTimeout(
            function() {
                jQuery('#data_quality_chart_tabs_MUAC').addClass('tab-pane');
            },
            0
        );
    },
    updateCharts: function(data, team, state) {

        var WHZs = [],
            HAZs = [],
            WAZs = [],
            MUACs = [],
            normalizedCurve = {color: '#83F52C', data: []},
            graphRange = Array.apply(null, {length: 120}).map(Function.call, function(Number){return (Number-60)/10;}), /* -6 to 6 n .1 increments */
            WHZkde = {color:'#D94545'},
            HAZkde = {color:'#D94545'},
            WAZkde = {color:'#D94545'},
            MUACkde = {color:'#D94545'},
            muacGraphRange, muacMin, muacMax, muacAxes,
            i;

        for (i = -6; i < 6.1; i += 0.1) {
            normalizedCurve.data.push([i, NormalDensityZx(i,0,1)]);
        }


        _.each(data.survey_data, function(survey) {
            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }
            if (survey.hasOwnProperty('child_surveys')) {
                _.each(survey.child_surveys, function(child) {
                    if (child.hasOwnProperty('muac')) {
                        MUACs.push(child.muac);
                    }
                    if (child.hasOwnProperty('zscores')) {
                        if (child.zscores.hasOwnProperty('WHZ')) {
                            WHZs.push(child.zscores.WHZ);
                        }
                        if (child.zscores.hasOwnProperty('HAZ')) {
                            HAZs.push(child.zscores.HAZ);
                        }
                        if (child.zscores.hasOwnProperty('WAZ')) {
                            WAZs.push(child.zscores.WAZ);
                        }
                    }
                });
            }
        });

        if (WHZs.length > 0) {
            WHZs.sort();
            WHZkde.data = kde(WHZs).points(graphRange);
        } else {
            WHZkde.data = [];
        }
        if (WHZs.length > 0) {
            WAZs.sort();
            WAZkde.data = kde(WAZs).points(graphRange);
        } else {
            WAZkde.data = [];
        }
        if (HAZs.length > 0) {
            HAZs.sort();
            HAZkde.data = kde(HAZs).points(graphRange);
        } else {
            HAZkde.data = [];
        }

        dataQuality.WHZDataQualityPlot.setData([normalizedCurve,WHZkde]);
        dataQuality.WHZDataQualityPlot.setupGrid();
        dataQuality.WHZDataQualityPlot.draw();

        dataQuality.HAZDataQualityPlot.setData([normalizedCurve,HAZkde]);
        dataQuality.HAZDataQualityPlot.setupGrid();
        dataQuality.HAZDataQualityPlot.draw();

        dataQuality.WAZDataQualityPlot.setData([normalizedCurve,WAZkde]);
        dataQuality.WAZDataQualityPlot.setupGrid();
        dataQuality.WAZDataQualityPlot.draw();

        MUACs.sort();
        muacMin = MUACs[0];
        muacMax = MUACs[MUACs.length-1];

        /* Muacs should be shown between the lowest and the highest available value*/
        muacGraphRange = Array.apply(null, {length: (muacMax-muacMin)*10}).map(Function.call, function(Number){return (Number/10+muacMin);}), /* muacMin to muacMax n .1 increments */
        MUACkde.data = kde(MUACs).points(muacGraphRange);

        muacAxes = dataQuality.MUACDataQualityPlot.getAxes();
        muacAxes.xaxis.options.min = muacMin;
        muacAxes.xaxis.options.max = muacMax;
        dataQuality.MUACDataQualityPlot.setData([MUACkde]);
        dataQuality.MUACDataQualityPlot.setupGrid();
        dataQuality.MUACDataQualityPlot.draw();
    },
    table: false,
    drawTable: function () {
        dataQuality.table = jQuery('#data_quality_table').dataTable({
            paging: false,
            searching: false,
            info: false
        });
    },
    updateTable: function (data, team, state) {
        var muacMissing = 0, muacFlagged = 0, muacPresent = 0, muacN,
            whzMissing = 0, whzFlagged = 0, whzPresent = 0, whzN,
            wazMissing = 0, wazFlagged = 0, wazPresent = 0, wazN,
            hazMissing = 0, hazFlagged = 0, hazPresent = 0, hazN;

        _.each(data.survey_data, function(survey) {
            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }
            /* This assumes that one child survey is sent in for each child < 60 months,
            even if all fields of a particular child survey may be left blank. */
            if (survey.hasOwnProperty('child_surveys')) {

                _.each(survey.child_surveys, function(child) {
                    if (child.hasOwnProperty('muac')) {
                        muacPresent++;
                    } else {
                        muacMissing++;
                    }
                    if (child.hasOwnProperty('zscores')) {
                        if (child.zscores.hasOwnProperty('WHZ')) {
                            whzPresent++;
                            if (child.zscores.WHZ < -5 || child.zscores.WHZ > 5) {
                                whzFlagged++;
                            }
                        } else {
                            whzMissing++;
                        }
                        if (child.zscores.hasOwnProperty('HAZ')) {
                            hazPresent++;
                            if (child.zscores.HAZ < -6 || child.zscores.HAZ > 6) {
                                hazFlagged++;
                            }
                        } else {
                            hazMissing++;
                        }
                        if (child.zscores.hasOwnProperty('WAZ')) {
                            wazPresent++;
                            if (child.zscores.WAZ < -6 || child.zscores.WAZ > 6) {
                                wazFlagged++;
                            }
                        } else {
                            wazMissing++;
                        }
                    } else {
                        whzMissing++;
                        hazMissing++;
                        wazMissing++;
                    }
                });
            }

        });

        muacN = muacMissing + muacPresent;
        whzN = whzMissing + whzPresent;
        hazN = hazMissing + hazPresent;
        wazN = wazMissing + wazPresent;

        jQuery('#muac_n').html(muacN);
        jQuery('#whz_n').html(whzN);
        jQuery('#haz_n').html(hazN);
        jQuery('#waz_n').html(wazN);

        jQuery('#muac_total').html(parseInt(muacPresent/muacN*100));
        jQuery('#whz_total').html(parseInt(whzPresent/whzN*100));
        jQuery('#waz_total').html(parseInt(wazPresent/wazN*100));
        jQuery('#haz_total').html(parseInt(hazPresent/hazN*100));

        jQuery('#muac_missing').html(parseInt(muacMissing/muacN*100));
        jQuery('#whz_missing').html(parseInt(whzMissing/whzN*100));
        jQuery('#haz_missing').html(parseInt(hazMissing/hazN*100));
        jQuery('#waz_missing').html(parseInt(wazMissing/wazN*100));

        jQuery('#muac_flagged').html(parseInt(muacFlagged/muacN*100)); /* There are currently no circumstances under which MUAC values ae flagged */
        jQuery('#whz_flagged').html(parseInt(whzFlagged/whzN*100));
        jQuery('#haz_flagged').html(parseInt(hazFlagged/hazN*100));
        jQuery('#waz_flagged').html(parseInt(wazFlagged/wazN*100));
        if (dataQuality.table) {
            dataQuality.table.fnDestroy();
            dataQuality.drawTable();
        }
    },
    updateList: function (data, team, state) {
        var femaleChildren = 0,
            maleChildren = 0,
            oldChildren = 0,
            youngChildren = 0,
            currentDate = new Date(),
            weights = [],
            heights = [],
            MUACs = [],
            birthDate,
            monthAge;

        _.each(data.survey_data, function(survey) {


            if (team && team > 0 && team != survey.team) {
                return true;
            }
            if (state && state != 'All states' && state != clusterInfo.findState(survey.cluster)) {
                return true;
            }

            if (survey.hasOwnProperty('child_surveys')) {

                _.each(survey.child_surveys, function(child) {
                    if (child.hasOwnProperty('gender')) {
                        if (child.gender==='M') {
                            maleChildren++;
                        } else {
                            femaleChildren++;
                        }
                    }
                    if (child.hasOwnProperty('birthDate')) {
                        birthDate = new Date(child.birthDate);
                        monthAge =  currentDate.getMonth() -
                            birthDate.getMonth() +
                            (12 * (currentDate.getFullYear() - birthDate.getFullYear()));
                        if (monthAge <30) {
                            oldChildren++;
                        } else {
                            youngChildren++;
                        }
                    }
                    if (child.hasOwnProperty('weight')) {
                        weights.push(child.weight);
                    }
                    if (child.hasOwnProperty('height')) {
                        heights.push(child.height);
                    }
                    if (child.hasOwnProperty('muac')) {
                        MUACs.push(child.muac);
                    }
                });
            }

        });

        jQuery('#data_quality_gender_ratio').html(parseInt(maleChildren/femaleChildren*100)/100);
        jQuery('#data_quality_age_ratio').html(parseInt(youngChildren/oldChildren*100)/100);
        jQuery('#data_quality_ldps_weight').html(lastDigitPreferenceScore(weights));
        jQuery('#data_quality_ldps_height').html(lastDigitPreferenceScore(heights));
        jQuery('#data_quality_ldps_muac').html(lastDigitPreferenceScore(MUACs));
    }
};

dataQuality.initiate();
