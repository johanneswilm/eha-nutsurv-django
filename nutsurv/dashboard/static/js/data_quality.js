var dataQuality = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/',
        teams: '/dashboard/teamsjsonview/',
        states: '/static/sample_data/states.json'
    },
    initiate: function() {
        jQuery('#data_quality_teams,#data_quality_states').selectmenu({
            change: dataQuality.changeStateOrTeam
        });
        dataQuality.drawCharts();
        // Set timeout so that charts can be drawn before tabs are created as else labels of Y-axis are overwritten.
        setTimeout(
            function() {
            jQuery('#data_quality_chart_tabs').tabs();},
            0
        );
        dataGetter.addNew(dataQuality.urls.teams, dataQuality.fillTeamsList, false);
        dataGetter.addNew(dataQuality.urls.states, dataQuality.fillStatesList, false);
        dataGetter.addNew(dataQuality.urls.survey, dataQuality.updateCharts, true);
    },
    fillTeamsList: function(data) {
        _.each(data.teams, function(names, id) {
            jQuery('#data_quality_teams').append(dataQuality.teamOptionTmp({
                id: id,
                names: names
            }));
        });
    },
    teamOptionTmp: _.template('<option value="<%- id %>"><%- names %></option>'),
    changeStateOrTeam: function () {
        var data = dataGetter.downloads[dataQuality.urls.survey].data,
            team = jQuery('#data_quality_teams').val(),
            state = jQuery('#data_quality_states').val();
        dataQuality.updateCharts(data,team,state);
    //    dataQuality.updateTable(data,team,state);
    },
    fillStatesList: function(data) {
        _.each(data.states.sort(), function(state) {
            jQuery('#data_quality_states').append(dataQuality.stateOptionTmp({
                state: state
            }));
        });
    },
    stateOptionTmp: _.template('<option value="<%- state %>" ><%- state %></option>'),
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
        dataQuality.WAZDataQualityPlot = jQuery.plot('#data_quality_waz_chart', [], options);
        dataQuality.MUACDataQualityPlot = jQuery.plot('#data_quality_muac_chart', [], muacOptions);
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
    }
};

dataQuality.initiate();
