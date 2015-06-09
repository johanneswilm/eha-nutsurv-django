/* Licensed as open source/free software (MIT license):

 Authors:
 Johannes Wilm, Adam Butler
 */

function lastDigitPreferenceScore(numbers) {
    var lastDigits = [0,0,0,0,0,0,0,0,0,0],
        N = numbers.length,
        chisquare = 0,
        LDPS,
        i;

    // find the last digit, and record it's occurrence in the lastDigits array
    _.each(numbers, function(number) {
        var lastDigit;
        var numberAsString;
        if (number) {
            numberAsString = number + '';
            lastDigit = numberAsString.charAt(numberAsString.length - 1);
            lastDigits[lastDigit]++;
        }
    });

    for (i = 0; i < lastDigits.length; i++) {
        chisquare += Math.pow((lastDigits[i] - (N/10)), 2)/(N/10);
    }

    // Calculate the DPS according to WHoMonica study http://www.ktl.fi/publications/monica/bp/bpqa.htm
    LDPS = 100 * Math.sqrt( chisquare/ (9 * N));

    return LDPS;

}
