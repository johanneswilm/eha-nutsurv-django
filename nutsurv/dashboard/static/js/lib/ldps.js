/* Licensed as open source/free software (MIT license):

 Authors:
 Johannes Wilm
 */

function lastDigitPreferenceScore(arrayOfNumbers) {
    var lastDigits = {},
        N = arrayOfNumbers.length,
        chisquare = 0,
        digitsAfterComma = 0,
        LDPS,
        i;

    for (i = 0; i < 10; i++) {
        lastDigits[i] = 0;
    }
    // We assume that all numbers have an equal amount of digits after the comma as jvascript removes trailing zeros by default.
    arrayOfNumbers.forEach(function(number) {
        var numbersAfterComma =  number.toString().split('.')[1];
        if (numbersAfterComma && numbersAfterComma.length > digitsAfterComma) {
                digisAfterComma = numbersAfterComma.length;
        }
    });

    // Record the last digit of each number in arrayOfNumbers
    arrayOfNumbers.forEach(function(number) {
        var numbersAfterComma =  number.toString().split('.')[1],
        lastDigit;
        if (digitsAfterComma===0) {
            lastDigit = parseInt(number.toString().split('').pop());
        } else if (digitsAfterComma===numbersAfterComma.length) {
            lastDigit = parseInt(number.toString().split('').pop());
        } else {
            lastDigit = 0;
        }
        lastDigits[lastDigit]++;
    });

    for (i = 0; i < 10; i++) {
        chisquare += Math.pow((lastDigits[i] - (N/10)), 2)/(N/10);
    }

    // Calculate the DPS according to WHoMonica study http://www.ktl.fi/publications/monica/bp/bpqa.htm
    LDPS = 100 * Math.sqrt( chisquare/ (9 * N));

    return LDPS;

}
