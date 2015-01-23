function parseQSL(rawQSL) {
    var rawLines = rawQSL.split('\n'),
        cleanedLines = [],
        QSL = [],
        indentionLength = 0,
        error = false,
        i = 0;

    // Remove comments and empty lines
    rawLines.forEach(function(rawLine) {
        var lineWoComment = rawLine.split('#')[0].trimRight();
        if (lineWoComment.trim().length > 0) {
            cleanedLines.push(lineWoComment);
        }
    });

    // Find indention length
    while (indentionLength === 0 && i < cleanedLines.length) {
        if (cleanedLines[i].length - cleanedLines[i].trimLeft().length > 0) {
            indentionLength = cleanedLines[i].length - cleanedLines[i].trimLeft().length;
        }
        i++;
    }

    // Don't allow indentions of zero
    if (indentionLength === 0) {
        indentionLength = 1;
    }

    // Turn QSL into a construct of Arrays and Objects
    cleanedLines.forEach(function(cleanedLine) {
        var indentions = (cleanedLine.length - cleanedLine.trimLeft().length) / indentionLength,
            currentArray = QSL,
            j;


        if (indentions % 1 != 0) {
            // Indention characters do not correspond to a known indention level.
            error = true;
        }

        for (j = 0; j < indentions; j++) {
            if (currentArray.length === 0) {
                // The indentions tell us to go a place that it's not possible to go.
                error = true;
            } else {
                currentArray = currentArray[currentArray.length - 1]['children'];
            }
        }
        currentArray.push({
            key: cleanedLine.trimLeft(),
            children: []
        });
    });

    if (error) {
        console.warn('QSL formatting with errors!');
    }

    return QSL;
}
