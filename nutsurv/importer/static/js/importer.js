function importCSV(lineData) {
    lineData.forEach(function(line) {
        var fields = line.split(','), // Assumes simple CSV fields no tricks with escaped commas or alike.
            exportObject = {
                "endTime": fields[0],
                "startTime": fields[1],
                "created": fields[1021],
                "_rev": "1-48af81d4df6b9c3a898ab69106f81d5f", // Could not find in data sources. Does this field matter?
                "modified": fields[1021],
                "householdID": parseInt(fields[8]),
                "cluster": parseInt(fields[3]),
                "location": [
                    parseFloat(fields[10]),
                    parseFloat(fields[11])
                ],
                "members": [],
                "team": {
                    "uuid": fields[1020],
                    "created": "2015-01-29T09:30:36.337Z",
                    "_rev": "1-4db4c2ac9bc5f6e1ebf040e73de79b20",
                    "modified": "2015-01-29T09:30:36.337Z",
                    "teamID": parseInt(fields[4]),
                    "members": [{
                        "designation": "Team Leader",
                        "firstName": "Tom",
                        "mobile": "09087786655",
                        "lastName": "Vince",
                        "age": 23,
                        "memberID": 1,
                        "gender": "M",
                        "email": "tom@vince.com"
                    }, {
                        "designation": "Anthropometrist",
                        "firstName": "Jide",
                        "mobile": "0807876777876",
                        "lastName": "Ofomah",
                        "age": 23,
                        "memberID": 2,
                        "gender": "M",
                        "email": "jide@obi.com"
                    }, {
                        "designation": "Assistant",
                        "firstName": "Femi",
                        "mobile": "08065777898898",
                        "lastName": "Oni",
                        "age": 22,
                        "memberID": 3,
                        "gender": "M",
                        "email": "femi@oni.com"
                    }],
                    "_id": "d7f66324-f277-4f34-c994-5cf45c27b75c"
                },
                "_id": "4bba74eb-e30c-4fc9-ce4e-d2b744e945b3",
                "tools": {
                    "scale": {
                        "toolID": 23,
                        "measurement": 65
                    },
                    "uuid": "c42c4207-1f69-438c-8062-f832f54039c3",
                    "created": "2015-01-29T09:31:05.347Z",
                    "_rev": "1-5d3d061ca0f14b9a74ba1249b42cf2f3",
                    "childMUAC": {
                        "toolID": 45,
                        "measurement": 87
                    },
                    "modified": "2015-01-29T09:31:05.347Z",
                    "heightBoard": {
                        "toolID": 23,
                        "measurement": 43
                    },
                    "_id": "c42c4207-1f69-438c-8062-f832f54039c3",
                    "adultMUAC": {
                        "toolID": 94,
                        "measurement": 83
                    }
                },
                "uuid": "4bba74eb-e30c-4fc9-ce4e-d2b744e945b3"
            }
        /*
        TODO:
          * The data for the different women and children is not ordered the same every time, so this needs to be figured out.
          * Add code for findign child, household members and women data and send the finished json package to server.
          * Make sure that initiateRead() is first called when an entire aMB "package" of entries has been successfully sent to the server and saved to the database.
          * Add team data. (form where?)
          * Calculate z-scores (using z-scroe calculation code from mobile app)
        */



    });
}

var fileInput = document.getElementById('file_import');

fileInput.addEventListener('change', function(e) {
    /* Load the selected file, 1MB at a time. Then split into lines and unless at the very end of the file,
    discard the last line as it will likely only be a part of a line.
    Set instead the next 1MB to start at the start of the last line */

    var file = document.getElementById('file_import').files[0],
        reader = new FileReader(),
        offset = 0,
        counter = 0;



    reader.onload = function(e) {
        var data = e.target.result,
            lineData = data.split('\n');

        if (offset < file.size) {
            offset -= lineData[lineData.length - 1].length;
            //    console.log(lineData[0]);
            //    console.log(lineData[lineData.length-1]);
            //    console.log([offset,lineData.length]);
            lineData.pop(); // Throw away the last line as it was likely only a partial line.
            importCSV(lineData);
            initiateRead();
        } else {
            importCSV(lineData);
        }

    };

    function initiateRead() {
        if (counter < 20) {
            reader.readAsText(file.slice(offset, (1024 * 1024) + offset));
            offset += 1024 * 1024;
            counter++;
        }
    }
    initiateRead();
});
