var dataGetter = {
    urls: {},
    /* All the urls to get data from in the format  'http://.../': {triggerFunctions:[triggerFunctions], updatable: true/false},
    where triggerFunctions is a list of functions to be called if the data has changed since the last update and updatable specifies
    whether the data may be updated. */
    data: {}, // Latest data obtained from urls by url
    updatedSources: 0,
    updatableSources: 0,

    addNew: function(url, triggerFunction, updatable) { // A function to be called when registring a new trigegrFunction for a given url.
        // TODO: What if certain data is seen as being updateable by one tab and constant by another?
        if (url in dataGetter.urls) {
            // The url has been registered already. Add the trigegr fucntion to this datagetter and call the trigegr function with the latest data obtained from the url.
            dataGetter.urls[url].triggerFunctions.push(triggerFunction);
            triggerFunction(dataGetter.data[url]);
        } else {
            dataGetter.urls[url] = {triggerFunctions:[triggerFunction], updatable: updatable};
            dataGetter.getData(url);
            if (updatable) {
                dataGetter.updatableSources++;
            }
        }
    },

    getData: function(url) { // Get new data from a specific url.
        jQuery.get(url, function(response) {
            if (!_.isEqual(dataGetter.data[url], response)) { // Only if the data is different than what was obtained from the same URL previously, call the trigger functions.
                dataGetter.data[url] = response;
                _.each(dataGetter.urls[url],function(triggerFunction){
                    triggerFunction(dataGetter.data[url]);
                })
            } else {
                console.log('no change for '+url);
            }
            dataGetter.updatedSources++;
            if (dataGetter.updatedSources===dataGetter.updatableSources) {
                dataGetter.lastUpdate = new Date();
                dataGetter.setTimer();
            }
        });
    },

    getAll: function() {// Function to iniate getting data from all registered urls.
        dataGetter.updatedSources = 0;
        _.each(_.keys(dataGetter.urls), dataGetter.getData);
    },
    lastUpdate: false,
    drawTimer : function () {
        if (dataGetter.lastUpdate) {
          var totalSeconds = parseInt((new Date()-dataGetter.lastUpdate)/1000),
            minutes = Math.floor(totalSeconds / 60),
            seconds = totalSeconds - minutes * 60;
          if (seconds<10) {
            seconds = '0'+seconds;
          }
          jQuery('#last_update span.ui-button-text').html(minutes+':'+seconds);
       }
    },
    getterInterval: false,
    timerInterval: false,
    setTimer: function () {// Set the timer to get data from URLs every X minutes;
        clearInterval(dataGetter.getterInterval);
        dataGetter.getterInterval = setInterval(dataGetter.getAll,5*60000); // Timer set to X*60000 milliseconds (X is minutes)
        clearInterval(dataGetter.timerInterval);
        dataGetter.timerInterval = setInterval(dataGetter.drawTimer,1000); // Redraw timer every second
    }

};

dataGetter.getAll();
