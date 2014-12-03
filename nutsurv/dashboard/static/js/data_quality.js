var dataQuality = {
    urls: {
        survey: '/static/sample_data/survey.json',
        teams: '/static/sample_data/teams.json',
        states: '/static/sample_data/states.json'
    },
    initiate: function() {
        jQuery('#data_quality_teams,#data_quality_states').selectmenu({
            change: dataQuality.changeStateOrTeam
        });
        jQuery('#data_quality_chart_tabs').tabs();
        dataQuality.drawDataQualityPlots();
        dataGetter.addNew(dataQuality.urls.teams, dataQuality.fillTeamsList, false);
        dataGetter.addNew(dataQuality.urls.states, dataQuality.fillStatesList, false);
        dataGetter.addNew(dataQuality.urls.survey, dataQuality.updateDataQualityPlots, true);
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
        dataQuality.updateTable(data,team,state);
    },
    fillStatesList: function(data) {
        _.each(data.states.sort(), function(state) {
            jQuery('#data_quality_states').append(dataQuality.stateOptionTmp({
                state: state
            }));
        });
    },
    stateOptionTmp: _.template('<option value="<%- state %>" ><%- state %></option>'),
    drawDataQualityPlots: function() {
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
        };
        dataQuality.WHZDataQualityPlot = jQuery.plot('#data_quality_whz_chart', [], options);
        dataQuality.HAZDataQualityPlot = jQuery.plot('#data_quality_haz_chart', [], options);
        dataQuality.WAZDataQualityPlot = jQuery.plot('#data_quality_waz_chart', [], options);
        dataQuality.MUACDataQualityPlot = jQuery.plot('#data_quality_muac_chart', [], options);
    },
    updateDataQualityPlots: function(data, team, state) {
        var WHZs = [],
            HAZs = [],
            WAZs = [],
            MUACs = [],
            normalizedCurve = {color: '#83F52C', data: []},
            graphRange = Array.apply(null, {length: 120}).map(Function.call, function(Number){return (Number-60)/10;}), /* -6 to 6 n .1 increments */,
            WHZkde = {color:'#D94545'},
            HAZkde = {color:'#D94545'},
            WAZkde = {color:'#D94545'},
            MUACkde = {color:'#D94545'},
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
        MUACs.sort();
        MUACkde.data = kde(MUACs).scale(20).points(graphRange);
        WHZs.sort();
        WHZkde.data = kde(WHZs).scale(20).points(graphRange);
        WAZs.sort();
        WAZkde.data = kde(WAZs).scale(20).points(graphRange);
        HAZs.sort();
        HAZkde.data = kde(HAZs).scale(20).points(graphRange);

    /*    dataQuality.WHZDataQualityPlot.setData([normalizedCurve,WHZkde]);
        dataQuality.WHZDataQualityPlot.setupGrid();
        dataQuality.WHZDataQualityPlot.draw();

        dataQuality.HAZDataQualityPlot.setData([normalizedCurve,HAZkde]);
        dataQuality.HAZDataQualityPlot.setupGrid();
        dataQuality.HAZDataQualityPlot.draw();

        dataQuality.WAZDataQualityPlot.setData([normalizedCurve,WAZkde]);
        dataQuality.WAZDataQualityPlot.setupGrid();
        dataQuality.WAZDataQualityPlot.draw();

        dataQuality.MUACDataQualityPlot.setData([MUACkde]);
        dataQuality.MUACDataQualityPlot.setupGrid();
        dataQuality.MUACDataQualityPlot.draw();*/
    },
};

dataQuality.initiate();
