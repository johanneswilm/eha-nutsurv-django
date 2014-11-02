var dataGetter = {
    urls: {}, // All the urls to get data from in the format  'http://.../': [triggerFunctions], where triggerFunctions is a list of functions to be called IF the data has changed since the last update.
    data: {}, // Latest data obtained from urls by url

    addNew: function(url,triggerFunction) { // A function to be called when registring a new trigegrFunction for a given url.
        if (url in dataGetter.urls) {
            // The url has been registered already. Add the trigegr fucntion to this datagetter and call the trigegr function with the latest data obtained from the url.
            dataGetter.urls[url].push(triggerFunction);
            triggerFunction(dataGetter.data[url]);
        } else {
            dataGetter.urls[url] = [triggerFunction];
            dataGetter.getData(url);
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
        })
    },

    getAll: function() {// Function to iniate getting data from all registered urls.
        _.each(_.keys(dataGetter.urls), dataGetter.getData);
    },

    setTimer: function () {// Set the timer to get data from URLs every X minutes;
        setInterval(dataGetter.getAll,5*60000); // Timer set to X*60000 milliseconds (X is minutes)
    }

};

dataGetter.setTimer();
