var childAnthropometry = {
    urls: {
        survey: '/dashboard/aggregatesurveydatajsonview/'
    },
    initiate: function() {
        teamStrataSelectors.init(this.changeStratumOrTeam);

        childAnthropometry.drawCharts();
        childAnthropometry.drawTable();

        dataGetter.addNew(childAnthropometry.urls.survey, childAnthropometry.updateCharts, true);
        dataGetter.addNew(childAnthropometry.urls.survey, childAnthropometry.updateTable, true);
        dataGetter.addNew(childAnthropometry.urls.survey, childAnthropometry.updateList, true);
    },
    changeStratumOrTeam: function () {
        var data = dataGetter.downloads[childAnthropometry.urls.survey].data,
            team = jQuery('#team_lead_selector').val(),
            stratum = jQuery('#strata_selector').val();
        childAnthropometry.updateCharts(data,team,stratum);
        childAnthropometry.updateTable(data,team,stratum);
        childAnthropometry.updateList(data,team,stratum);
    },
    drawCharts: function() {
        var options = {
            yaxis: {
                min: 0,
                show: false
            },
            xaxis: {
                tickDecimals: 0,
                min: -6,
                max: 6
            }
        }, muacOptions = {
            yaxis: {
                show: false
            },
            xaxis: {
                tickDecimals: 0
            }
        };

        childAnthropometry.WHZDataQualityPlot = jQuery.plot('#child_anthropometry_whz_chart', [], options);
        childAnthropometry.HAZDataQualityPlot = jQuery.plot('#child_anthropometry_haz_chart', [], options);
        // Only hide tabs after canvases have been drawn on them.
        setTimeout(
            function() {
                jQuery('#child_anthropometry_chart_tabs_HAZ').addClass('tab-pane');
            },
            0
        );
        childAnthropometry.WAZDataQualityPlot = jQuery.plot('#child_anthropometry_waz_chart', [], options);
        setTimeout(
            function() {
                jQuery('#child_anthropometry_chart_tabs_WAZ').addClass('tab-pane');
            },
            0
        );
        childAnthropometry.MUACDataQualityPlot = jQuery.plot('#child_anthropometry_muac_chart', [], muacOptions);
        setTimeout(
            function() {
                jQuery('#child_anthropometry_chart_tabs_MUAC').addClass('tab-pane');
            },
            0
        );
    },
    updateCharts: function(data, team, stratum) {

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
            var childSurveys;

            if (team && team > -1 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && stratum != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }

            childSurveys = _.pluck(_.where(survey.members, {'surveyType': 'child'}), 'survey');

            _.each(childSurveys, function(child) {
                if (child.hasOwnProperty('muac')) {
                    MUACs.push(child.muac);
                }
                if (child.hasOwnProperty('zscores')) {
                    if (child.zscores.hasOwnProperty('WHZ')) {
                        WHZs.push(child.zscores.WHZ);
                    }
                    if (child.zscores.hasOwnProperty('HAZ')) {
                        HAZs.push(parseInt(child.zscores.HAZ*100)/100);
                    }
                    if (child.zscores.hasOwnProperty('WAZ')) {
                        WAZs.push(child.zscores.WAZ);
                    }
                }
            });

        });

        if (WHZs.length > 0) {
            WHZs.sort(function(a,b){return a - b});
            WHZkde.data = kde(WHZs).points(graphRange);
        } else {
            WHZkde.data = [];
        }
        if (WHZs.length > 0) {
            WAZs.sort(function(a,b){return a - b});
            WAZkde.data = kde(WAZs).points(graphRange);
        } else {
            WAZkde.data = [];
        }
        if (HAZs.length > 0) {
            HAZs.sort(function(a,b){return a - b});
            HAZkde.data = kde(HAZs).points(graphRange);
        } else {
            HAZkde.data = [];
        }

        childAnthropometry.WHZDataQualityPlot.setData([normalizedCurve,WHZkde]);
        childAnthropometry.WHZDataQualityPlot.setupGrid();
        childAnthropometry.WHZDataQualityPlot.draw();

        childAnthropometry.HAZDataQualityPlot.setData([normalizedCurve,HAZkde]);
        childAnthropometry.HAZDataQualityPlot.setupGrid();
        childAnthropometry.HAZDataQualityPlot.draw();

        childAnthropometry.WAZDataQualityPlot.setData([normalizedCurve,WAZkde]);
        childAnthropometry.WAZDataQualityPlot.setupGrid();
        childAnthropometry.WAZDataQualityPlot.draw();

        MUACs.sort(function(a,b){return a - b});

        muacMin = MUACs[0];
        muacMax = MUACs[MUACs.length-1];

        /* Muacs should be shown between the lowest and the highest available value*/
        muacGraphRange = Array.apply(null, {length: (muacMax-muacMin)*10}).map(Function.call, function(Number){return (Number/10+muacMin);}), /* muacMin to muacMax n .1 increments */

        MUACkde.data = kde(MUACs).points(muacGraphRange);

        muacAxes = childAnthropometry.MUACDataQualityPlot.getAxes();
        muacAxes.xaxis.options.min = muacMin;
        muacAxes.xaxis.options.max = muacMax;
        childAnthropometry.MUACDataQualityPlot.setData([MUACkde]);
        childAnthropometry.MUACDataQualityPlot.setupGrid();
        childAnthropometry.MUACDataQualityPlot.draw();

    },
    table: false,
    drawTable: function () {
        childAnthropometry.table = jQuery('#child_anthropometry_table').dataTable({
            paging: false,
            searching: false,
            info: false
        });
    },
    updateTable: function (data, team, stratum) {
        var muacMissing = 0, muacFlagged = 0, muacPresent = 0, muacN,
            whzMissing = 0, whzFlagged = 0, whzPresent = 0, whzN,
            wazMissing = 0, wazFlagged = 0, wazPresent = 0, wazN,
            hazMissing = 0, hazFlagged = 0, hazPresent = 0, hazN;

        _.each(data.survey_data, function(survey) {
            var childSurveys;

            if (team && team > -1 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && stratum != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }
            /* This assumes that one child survey is sent in for each child < 60 months,
            even if all fields of a particular child survey may be left blank. */

            childSurveys = _.pluck(_.where(survey.members, {'surveyType': 'child'}), 'survey');

            _.each(childSurveys, function(child) {
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
        if (childAnthropometry.table) {
            childAnthropometry.table.fnDestroy();
            childAnthropometry.drawTable();
        }
    },
    updateList: function (data, team, stratum) {
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

            var childMembers;

            if (team && team > -1 && team != survey.team) {
                return true;
            }
            if (stratum && stratum != 'All strata' && stratum != clusterInfo.findFirstAdminLevel(survey.cluster)) {
                return true;
            }

            childMembers = _.where(survey.members, {'surveyType': 'child'});

            _.each(childMembers, function(child) {
                if (child.hasOwnProperty('gender')) {
                    if (child.gender==='M') {
                        maleChildren++;
                    } else {
                        femaleChildren++;
                    }
                }
                if (child.hasOwnProperty('birthdate')) {
                    birthDate = new Date(child.birthdate);
                    monthAge =  currentDate.getMonth() -
                        birthDate.getMonth() +
                        (12 * (currentDate.getFullYear() - birthDate.getFullYear()));
                    if (monthAge <30) {
                        oldChildren++;
                    } else {
                        youngChildren++;
                    }
                }
                if (child.hasOwnProperty('survey')) {
                    if (child.survey.hasOwnProperty('weight')) {
                        weights.push(child.survey.weight);
                    }
                    if (child.survey.hasOwnProperty('height')) {
                        heights.push(child.survey.height);
                    }
                    if (child.survey.hasOwnProperty('muac')) {
                        MUACs.push(child.survey.muac);
                    }
                }

            });

        });

        jQuery('#child_anthropometry_sex_ratio').html(parseInt(maleChildren/femaleChildren*100)/100);
        jQuery('#child_anthropometry_age_ratio').html(parseInt(youngChildren/oldChildren*100)/100);
        jQuery('#child_anthropometry_ldps_weight').html(lastDigitPreferenceScore(weights));
        jQuery('#child_anthropometry_ldps_height').html(lastDigitPreferenceScore(heights));
        jQuery('#child_anthropometry_ldps_muac').html(lastDigitPreferenceScore(MUACs));
    }
};

childAnthropometry.initiate();
