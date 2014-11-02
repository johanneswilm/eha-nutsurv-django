var home = {
    initiate: function () {
        dataGetter.addNew('/static/sample_data/survey.json', home.drawMap);
        dataGetter.addNew('/static/sample_data/alerts.json', home.drawAlerts);
    },
    drawMap: function (data) {
        console.log(data);
        console.log('het')
    },
    drawAlerts: function (data) {
        console.log(data);
    },

};

home.initiate();
