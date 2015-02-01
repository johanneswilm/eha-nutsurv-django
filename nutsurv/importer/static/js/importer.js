var fileInput = document.getElementById('file_import'),
    importStatus = document.getElementById('import_status'),
    exportErrors=[];


fileInput.addEventListener('change', function(e) {
    /* Load the selected file, 1MB at a time. Then split into lines and unless at the very end of the file,
    discard the last line as it will likely only be a part of a line.
    Set instead the next 1MB to start at the start of the last line */

    var file = document.getElementById('file_import').files[0],
        reader = new FileReader(),
        offset = 0,
        fieldDefinitions = false;


    reader.onload = function(e) {
        var data = e.target.result,
            lineData = data.split('\n');

        if (!fieldDefinitions) {
            fieldDefinitions = lineData.shift().split(',');
        }
        if (offset < file.size) {
            offset -= lineData[lineData.length - 1].length;
            lineData.pop(); // Throw away the last line as it was likely only a partial line.
        }
        importCSV(lineData);

    };

    function initiateRead() {
        if (offset < file.size) {
            reader.readAsText(file.slice(offset, (1024 * 1024) + offset));
            offset += 1024 * 1024;
            importStatus.innerHTML = 'Importing: ' + parseInt((offset/file.size) * 100) + '%';
        } else {
            importStatus.innerHTML = 'Done!';
        }
    }

    function importCSV(lineData) {
        var saveCounter = 0;

        lineData.forEach(function(line) {
            var fields = line.split(','), // Assumes simple CSV fields no tricks with escaped commas or alike.
                exportObject = {},
                xhr;

            if (fields.length === 1) { // Encountered an empty line
                saveCounter++;
                if (saveCounter===lineData.length) {
                    // This 1MB block of data has been saves succesfully to the database. Now initiate another block.
                    initiateRead();
                }
                return false;
            }
            fieldDefinitions.forEach(function(fieldName, counter){
                var value = fields[counter],
                    fieldDefinition;
                if (value!='n/a') {
                    if (fieldName.indexOf('[')===-1) { // A simple field
                        exportObject[fieldName] = value;
                    } else { // An array of fields. These are not necessarily in order (7 can come before 6, etc.)
                        fieldDefinition = fieldName.split(/[\[\]]/);
                        if (fieldDefinition.length===3) {// We are only dealing with a single array of values. Not an array inside of an array.TODO: Deal with arrays inside of arrays.
                            if (!exportObject.hasOwnProperty(fieldDefinition[0])) {
                                exportObject[fieldDefinition[0]] = [];
                            }
                            while (exportObject[fieldDefinition[0]].length < parseInt(fieldDefinition[1])) {
                                exportObject[fieldDefinition[0]].push({});
                            }
                            exportObject[fieldDefinition[0]][parseInt(fieldDefinition[1])-1][fieldDefinition[0]+fieldDefinition[2]] = value;
                        }
                    }
                }

            });

            // Send exportObject as json via ajax to formhub import webhook. The structure should be the same as other data coming directly from formhub. TODO: Handle optional post keyfor extra security.
            xhr = new XMLHttpRequest();
            xhr.open("POST", '/importer/register_formhub_data', true);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && (xhr.status == 200 || xhr.status == 201)) {
                    saveCounter++;
                    if (saveCounter===lineData.length) {
                        // This 1MB block of data has been saves succesfully to the database. Now initiate another block.
                        initiateRead();
                    }
                } else  if (xhr.readyState == 4 &! (xhr.status == 200 || xhr.status == 201)) {
                    console.log(exportObject);
                    exportErrors.push(exportObject);
                }
            }

            xhr.send(JSON.stringify(exportObject));

        });
    }

    initiateRead();
});
