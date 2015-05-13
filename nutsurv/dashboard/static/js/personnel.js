var personnel = {
    urls : {
        personnel: '/dashboard/teammembers/'
    },
    initiate: function () {
        dataGetter.addNew(personnel.urls.personnel, personnel.drawTable, false);
    },
    downloadData: function () {

        // Fail if no data
        if (!dataGetter.downloads[personnel.urls.personnel].data) {
            return false;
        }

        // Trim Keys
        var trimSurvey = ['members', 'point', 'teamAnthropometrist', 'teamAssistant', 'teamLead', 'uuid', 'url'];

        // Flatten & Get Keys
        var lastSurvey = _.omit(dataGetter.downloads[personnel.urls.personnel].data[0].lastSurvey, trimSurvey);
        var surveyKeys = _.keys(lastSurvey);
        var personKeys = _.keys(dataGetter.downloads[personnel.urls.personnel].data[0]);
        var allKeys = _.without(personKeys, 'url', 'lastSurvey').concat(surveyKeys);

        // Start CSV Output
        var output = allKeys.join(',') + '\n';

        // Get Data
        _.each(dataGetter.downloads[personnel.urls.personnel].data, function(person, id) {

            var thisSurvey = _.omit(person.lastSurvey, trimSurvey);
            var surveyValues = _.values(thisSurvey);
            var personValues = _.values(_.omit(person, ['url', 'lastSurvey']));
            var allValues = personValues.concat(surveyValues);

            // Add to CSV
            output += allValues.join(',') + '\n';
        });

        // Save
        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'personnel.csv'
        );
    },
    surveyDetails: function(memberid) {

        var memberDetails = _.findWhere(dataGetter.downloads[personnel.urls.personnel].data, { 'id': memberid.toString() });

        if (memberDetails !== undefined) {
            var modal_template = _.template($('#template-personnel-details').html());
            $('#personnel-modal').find('h3.modal-title').html('<i class="fa fa-user"></i> ' + memberDetails.firstName + ' ' + memberDetails.lastName + '\'s Last Survey');
            $('#personnel-modal').find('div.modal-body').html(modal_template(memberDetails.lastSurvey));
            $('#personnel-modal').modal();
        } else {
          alert('No survey data exists');
        }
    },
    table: false,
    drawTable: function (data) {

        // Check that all relevant data has been downloaded, else cancel
        if (!dataGetter.checkAll([personnel.urls.personnel])) {
            return false;
        }

        var perPersonnelData = [];

        var genderIcon = {
            M: '<i class="fa fa-male"></i> ',
            F: '<i class="fa fa-female"></i> '
        }

        var positionNames = {
            teamLead: "Team Lead",
            teamAssistant: "Assistant",
            teamAnthropometrist: "Anthropometrist"
        }

        var currentYear = moment().format('YYYY');

        // Make Results for Output
        _.each(dataGetter.downloads[personnel.urls.personnel].data, function(person, id) {

            var name = person.firstName + person.lastName;
            var age = currentYear - person.birthYear;
            var surveyDate = moment().format('MMM D, YYYY');
            var position = 'Unknown Role';
            var location = 'Unknown Cluster';

            // Has lastSurvey object
            if (person.lastSurvey) {

              _.each(person.lastSurvey, function(item, key) {
                if (item == person.url) {
                  position = positionNames[key];
                }
              });

              surveyDate = person.lastSurvey.endTime.split('T')[0];

              // Location
              location = person.lastSurvey.clusterName + ' #' + person.lastSurvey.cluster + '<br> <a href="#" data-mermberID="' + person.id + '" class="personnel-last-survey">View Details</a>';
            }

            var personnelObject = {
                name: genderIcon[person.gender] + '<div class="personnel-name"><strong>' + name + '</strong><br> ' + age + ' years</div>',
                id: person.id,
                contact: '<a href="mailto:' + person.email + '">' + person.email + '</a><br>' + person.mobile,
                position: position + '<br>' + moment(surveyDate).format('MMM D, YYYY'),
                date: 'Team Leader<br>' + moment(surveyDate).format('MMM D YYYY'),
                location: location
            };

            perPersonnelData.push(personnelObject);
        });

        // If the table exists already, we destroy it
        if (personnel.table) {
            personnel.table.fnDestroy();
        }

        personnel.table = jQuery('#personnel_table').dataTable({
            paging: true,
            ordering: true,
            searching: true,
            dom: '<"#personnel_data" <"page-header"fr<"clear">><t><"bottom">ip<"clear">>',
            data: perPersonnelData,
            responsive: {
                details: {
                    renderer: function(api, rowIdx) {
                        // Select hidden columns for the given row
                        var data = api.cells(rowIdx, ':hidden').eq(0).map( function(cell) {
                            var header = jQuery( api.column( cell.column ).header() );
                            return '<tr>'+
                                    '<td>'+ header.attr('data-column-name')+':'+'</td> '+
                                    '<td>'+ api.cell(cell).data()+'</td>'+
                                '</tr>';
                        }).toArray().join('');

                        return data ? $('<table/>').append(data) : false;
                    },
                }
            },
            columns: [
                { name: 'name', data: 'name' },
                { name: 'personnel_id', data: 'id' },
                { name: 'contact', data: 'contact' },
                { name: 'position', data: 'position' },
                { name: 'location', data: 'location' },
                { "searchable": false, data: function() { return ''; }, orderable: false }
            ],
            "order": [[ 1, "asc" ]]
        });

        // Add UI Items
        $('.page-header').append('<h1><i class="fa fa-user"></i> Personnel</h1>');
        $('#personnel_table_filter').addClass('pull-right');
        $('.page-header').prepend('<button id="personnel_download" class="pull-right btn btn-default dataTables_extra_button">Download CSV</button>');

        $('.personnel-last-survey').on('click', function(e) {
            personnel.surveyDetails($(e.target).data('mermberid'));
        });

        // Download Button Action
        $('#personnel_download').on('click', function () {
            personnel.downloadData();
        });

    },
};

personnel.initiate();
