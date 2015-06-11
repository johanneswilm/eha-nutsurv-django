/* Licensed as open source/free software (MIT license):

 Authors:
 Johannes Wilm, Adam Butler
 */

function lastDigitPreferenceScore(numbers) {
    var lastDigits;
    var maxDecimalPlaces;
    var N = numbers.length;
    var chisquare = 0;

    var decimalPlaces = function(number) {
        var decimals = (number + '').split('.')[1];
        return decimals && decimals.length;
    };

    var getLastDigit = function(number) {
        var numberAsString = number + '';
        return numberAsString.charAt(numberAsString.length - 1);
    };

    // there shouldn't be null values, but just in case
    numbers = _.filter(numbers, function(number) {
        return number;
    });

    // since javascript removes trailing zeroes, we need to find the maximum decimal places in this dataset
    maxDecimalPlaces = _.reduce(numbers, function(maxDP, number) {
        var dp = decimalPlaces(number);
        return dp > maxDP ? dp : maxDP;
    }, 0);

    lastDigits = _.reduce(numbers, function(lastDigitDistribution, number) {
        var lastDigit;
        if (maxDecimalPlaces > decimalPlaces(number)) {
            lastDigit = 0;
        } else {
            lastDigit = getLastDigit(number);
        }
        lastDigitDistribution[Number(lastDigit)]++;
        return lastDigitDistribution;
    }, [0,0,0,0,0,0,0,0,0,0]);

    _.each(lastDigits, function(lastDigit, index) {
        chisquare += Math.pow((lastDigit - (N/10)), 2) / (N/10);
    });

    // Calculate the DPS according to WHoMonica study http://www.thl.fi/publications/monica/bp/bpqa.htm
    return 100 * Math.sqrt( chisquare / (9 * N));
}
