var personnel = {
    urls : {
        personnel: '/dashboard/teammembers/'
    },
    initiate: function () {
        dataGetter.addNew(personnel.urls.personnel, personnel.drawTable, false);
    },
    downloadData: function () {
        if (!dataGetter.downloads[personnel.urls.personnel].data) {
            return false;
        }

        // FIXME: 
        console.log(dataGetter.downloads[personnel.urls.personnel].data);

        saveAs(
            new Blob( [output], {type : 'text/csv'}),
            'personnel.csv'
        );
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
            var position = 'Unknown';
            var location = 'Unknown';

            // Has lastSurvey object
            if (person.lastSurvey) {

              _.each(person.lastSurvey, function(item, key) {
                if (item == person.url) {
                  position = positionNames[key];
                }
              });

              surveyDate = person.lastSurvey.endTime.split('T')[0];

              // Location
              location = person.lastSurvey.clusterName + ' #' + person.lastSurvey.cluster + '<br> <a href="#" data-mermberID="' + person.memberID + '" class="personnel-last-survey">View Details</a>';
            }

            var personnelObject = {
                name: genderIcon[person.gender] + '<div class="personnel-name"><strong>' + name + '</strong><br> ' + age + ' years</div>',
                memberID: person.memberID,
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
                            return '<tr class="was-ist-das">'+
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
                { name: 'personnel_id', data: 'memberID' },
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

        $('.personnel-last-survey').on('click', function() {
          alert('This will show alert detail about place lastSurvey happened. Perhaps a map');
        });

        // Download Button Action
        $('#personnel_download').on('click', function () {
            personnel.downloadData();
        });

    },
};

personnel.initiate();