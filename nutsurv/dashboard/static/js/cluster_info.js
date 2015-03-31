if (!window.clusterInfo) { // This file may be included by various tabs, so only define it if this is the first time the file is included.
    var clusterInfo = {
        urls: {
            clusters: '/dashboard/clustersjsonview/'
        },
        initiate: function () {
            dataGetter.addNew(clusterInfo.urls.clusters, clusterInfo.receivedClusterData, false);
        },
        dataAvailable: false,
        receivedClusterData: function (data) {
            clusterInfo.dataAvailable = true;
        },
        findState: function (cluster) {
            if (!clusterInfo.dataAvailable) {
                return false;
            }
            var clusterData = dataGetter.downloads[clusterInfo.urls.clusters].data;
            if (!clusterData.clusters.hasOwnProperty(cluster)) {
                return false;
            }
            return clusterData.clusters[cluster].state_name;
        },
        findSecondAdminLevel: function (cluster) {
            if (!clusterInfo.dataAvailable) {
                return false;
            }
            var clusterData = dataGetter.downloads[clusterInfo.urls.clusters].data;
            if (!clusterData.clusters.hasOwnProperty(cluster)) {
                return false;
            }
            return clusterData.clusters[cluster].second_admin_level_name;
        },
        findName: function (cluster) {
            if (!clusterInfo.dataAvailable) {
                return false;
            }
            var clusterData = dataGetter.downloads[clusterInfo.urls.clusters].data;
            if (!clusterData.clusters.hasOwnProperty(cluster)) {
                return false;
            }
            return clusterData.clusters[cluster].cluster_name;
        }
    };
    clusterInfo.initiate();
}
