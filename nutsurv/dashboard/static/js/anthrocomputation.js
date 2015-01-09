function NotImplementedException() {}


function isUnknownOrNaN(value) {
    return isNaN(parseFloat(value)) || !isFinite(value)
}


function roundFloat(number, decimalPlaces) {
    if(isUnknownOrNaN(decimalPlaces))
        decimalPlaces = 2;
    else if(decimalPlaces < 0)
        decimalPlaces = 0;
    else
        decimalPlaces = parseInt(decimalPlaces);
    var p = Math.pow(10, decimalPlaces);
    return Math.round(number * p) / p;
}


// Lists all the 'logical' indicators, i.e. considering W4L and W4H to
// be one indicator.
var Indicator = {
    Weight4LengthOrHeight: 0,
    Weight4Age: 1,
    LengthOrHeight4Age: 2,
    BMI4Age: 3,
    HC4Age: 4,
    MUAC4Age: 5,
    TSF4Age: 6,
    SSF4Age: 7
};

// Lists all the 'physical' indicators, i.e. separately considering W4L and W4H.
var GraphIndicator = {
    Weight4Height: -1,
    Weight4Length: Indicator.Weight4LengthOrHeight,
    Weight4Age: Indicator.Weight4Age,
    LengthOrHeight4Age: Indicator.LengthOrHeight4Age,
    BMI4Age: Indicator.BMI4Age,
    HC4Age: Indicator.HC4Age,
    MUAC4Age: Indicator.MUAC4Age,
    TSF4Age: Indicator.TSF4Age,
    SSF4Age: Indicator.SSF4Age
};

// The different anthro z-score flags.
var Flag = {
    Flag_None: 0,
    W4LHZ: 1,
    LH4AZ: 2,
    W4AZ: 3,
    W4LHZ_LH4AZ: 4,
    W4LHZ_W4AZ: 5,
    LH4AZ_W4AZ: 6,
    W4LHZ_LH4AZ_W4AZ: 7,
    BMI4AZ: 8
};


//PYTHON #import databasereader

//PYTHON class AnthropometricResult(object):
//PYTHON     pass  # fields will be dynamically assigned in Python
function AnthropometricResult() {
}


// #region Constants

//Boundaries for input values, checked on the UI and data import sides

// The min weight for a child, in kg.
const INPUT_MINWEIGHT = 0.9;

// The max weight for a child, in kg.
const INPUT_MAXWEIGHT = 58.0;

// The min length/height for a child, in cm.
const INPUT_MINLENGTHORHEIGHT = 38.0;

// The max length/height for a child, in cm.
const INPUT_MAXLENGTHORHEIGHT = 150.0;

// The max possible value for a record's weighting factor.
const INPUT_MAXWEIGHTINGFACTOR = Number.MAX_VALUE;

// The min HC for a child, in cm.
const INPUT_MINHC = 25.0;

// The max HC for a child, in cm.
const INPUT_MAXHC = 64.0;

// The min MUAC for a child, in cm.
const INPUT_MINMUAC = 6.0;

// The max MUAC for a child, in cm.
const INPUT_MAXMUAC = 35.0;

// The min TSF for a child, in mm.
const INPUT_MINTSF = 1.8;

// The max TSF for a child, in mm.
const INPUT_MAXTSF = 40.0;

// The min SSF for a child, in mm.
const INPUT_MINSSF = 1.8;

// The max SSF for a child, in mm.
const INPUT_MAXSSF = 40.0;

/* The exact number of days in one months, for converting between days and
 months.  Fixed according to WHO instructions.*/
const DAYSINMONTH = 30.4375;

// Fixed factor used for computing NCHS z-scores.
const NCHSFACTOR = 1.8807936;

/* The 'cut-off' age when determining whether length or height should be
 used.*/
const HEIGHT_MINDAYS = 731;

/* The 'cut-off' value when determining whether length or height should be
 used (WHO standard). */
const LENGTH_LIMIT = 87;

/* The 'cut-off' value when determining whether length or height should be
 used (NCHS reference).
  */
const NCHSLENGTH_LIMIT = 85;

// The min age for a child.
const MINDAYS = 0;

// The max age for a child to be considered in calculations.
const MAXDAYS = 1856;

// The min length, in cm (WHO standard).
const MINLENGTH = 45;

// The max length, in cm (WHO standard).
const MAXLENGTH = 110;

// The min height, in cm (WHO standard).
const MINHEIGHT = 65;

// The max height, in cm (WHO standard).
const MAXHEIGHT = 120;

// The min length/height for males, in cm (NCHS reference).
const NCHSMINLENGTHORHEIGHT_MALE = 49;

// The min length/height for females, in cm (NCHS reference).
const NCHSMINLENGTHORHEIGHT_FEMALE = 49;

// The max length/height for males, in cm (NCHS reference).
const NCHSMAXLENGTHORHEIGHT_MALE = 145;

// The max length/height for females, in cm (NCHS reference).
const NCHSMAXLENGTHORHEIGHT_FEMALE = 137;

/* The amount in cm to add/subtract when correcting from height to length
 and vice-versa. */
const HEIGHTCORRECTION = 0.7;

// Default number of decimals for measurements.
//PYTHON NotImplemented
const DEFAULTPRECISION_MEASURE = 2;

// Default number of decimals for z-scores.
//PYTHON NotImplemented
const DEFAULTPRECISION_ZSCORE = 2;

// Default number of decimals for percentiles.
//PYTHON NotImplemented
const DEFAULTPRECISION_PERCENTILE = 1;

// Default number of decimals for BMI values.
//PYTHON NotImplemented
const DEFAULTPRECISION_BMI = 1;

// Contains the default min bounds of the indicators.
const MINZSCOREBOUNDS = [-5, -6, -6, -5, -5, -5, -5, -5];

// Contains the default min bounds of the indicators in NCHS mode.
// Missing in the Python code.
const MINZSCOREBOUNDS_NCHS = [-4, -6, -6, -5, -5, -5, -5, -5];

// Contains the default max bounds of the indicators.
const MAXZSCOREBOUNDS = [5, 5, 6, 5, 5, 5, 5, 5];

// Contains the default max bounds of the indicators in NCHS mode.
// Missing in the Python code.
const MAXZSCOREBOUNDS_NCHS = [6, 6, 6, 5, 5, 5, 5, 5];

// #region Public fields
//C#        /// The current standards (WHO, NCHS) used for IA computations.
//C#        public static AnthroMode IACurrentStandards = AnthroMode.WHO;
//C#
//C#        /// The current standards (WHO, NCHS) used for NS computations.
//C#        public static AnthroMode NSCurrentStandards = AnthroMode.WHO;
//C#
//C#        #region Private fields - reference tables cache
//C#
/* Whether to use the pre-loaded reference tables, instead of accessing the
DB for each calculation.  Set via InitReferenceTablesCache().
PYTHON [Vernon] WHO did not use cache on mobiles, we will follow that lead,
for now. */
const _useReferenceTablesCache = false;
//C#
//C#        /// The pre-loaded reference tables (used if enabled).
//C#        /// The key to populate/access each table's items is obtained via GetHashKey().
//C#        private static Dictionary<GraphIndicator, Hashtable> _referenceTablesCache;
//C#
//C#        #endregion


// region Private struct ReferenceData
// Used for storing data points from the indicator reference tables.
//PYTHON     def __init__(self, x=NotImplemented, y=NaN, el=NaN, m=NaN, s=NaN):
function ReferenceData(x, y, l, m, s) {
    // References the X-axis value: age, height or weight
    // X NotImplemented in Python
    this.X =  x;
    // References the Y-Axis value: BMI, weight, height, HC, MUAC, TSF, SSF
    this.Y = y;
    // References the L value corresponding to X value from the standard table
    this.L = l;
    // References the M value corresponding to X value from the standard table
    this.M = m;
    // References the S value corresponding to X value from the standard table
    this.S = s;

    // Sets the point values to 'unknown'(i.e. undefined).
    //PYTHON SetExtreme = ReferenceData(None, NaN, NaN, NaN, NaN)
    this.setExtreme = function() {
        this.X = undefined;
        this.Y = undefined;
        this.L = undefined;
        this.M = undefined;
        this.S = undefined;
    }
}


// Structure that contains the pair-value {Z-score, Percentile}
// Creates a new indicator value, setting Z and P to 'undefined' unless given.
function IndicatorValue(p, z) {
    // The percentile value. (C# public decimal P; unused in the Python code)
    this.P = p;
    // The z-score value. (C# public decimal Z)
    this.Z = z;
}


// Computes the percentile based on the z-score value.
function centile(zScoreValue) {
    if(zScoreValue < -3 || zScoreValue > 3)
        return NaN;

    var absVal = Math.abs(zScoreValue);
    // try to approximate with a 5-degree polynomial function
    var P1 = (
        1 - 1 / Math.sqrt(2 * Math.PI) * Math.exp(-Math.pow(absVal, 2) / 2)
        * (
            0.31938 * (1 / (1 + 0.2316419 * absVal))
            - 0.356563782 * Math.pow(1 / (1 + 0.2316419 * absVal), 2)
            + 1.781477937 * Math.pow(1 / (1 + 0.2316419 * absVal), 3)
            - 1.82125 * Math.pow(1 / (1 + 0.2316419 * absVal), 4)
            + 1.330274429 * Math.pow(1 / (1 + 0.2316419 * absVal), 5)
        )
    );
    P1 *= 100;
    if(zScoreValue < 0)
        P1 = 100 - P1;
    if(0 <= P1 && P1 <= 100)
        return P1
    else
        return NaN
}


// Returns the adjusted length/height.
function getAdjustedLengthOrHeight(ageInDays, lengthOrHeight, isRecumbent) {
    var output = {
        lengthOrHeight: NaN,
        // true if the returned value is a length, not a height
        isLength: undefined
    };

    if(ageInDays < 0) {
        output.isLength = isRecumbent;
        output.lengthOrHeight = lengthOrHeight;
    } else {
        if(ageInDays < HEIGHT_MINDAYS) {
            output.isLength = true;
            if(isRecumbent)
                output.lengthOrHeight = lengthOrHeight;
            else
                output.lengthOrHeight = lengthOrHeight + HEIGHTCORRECTION;
        } else {
            output.isLength = false;
            if(isRecumbent)
                output.lengthOrHeight = lengthOrHeight - HEIGHTCORRECTION;
            else
                output.lengthOrHeight = lengthOrHeight;
        }
    }
    return output;
}


/* This function assumes access to function get4AgeIndicatorRefData(ind, sex,
   ageInDays) which provides L, M, S for a given age and sex from whatever
   database they are stored in (see databasereader.py in the old kivy app code).
   This function assumes that the data it gets from the aforementioned function
   is exactly in the same format as the data the Python implementation used to
   get (i.e. a table with the values of interest in row 0 and columns
   addressable by their name (i.e. 'L', 'M' or 'S')).
*/
function get4AgeIndicatorReference(ind, sex, ageInDays) {
    if(!_useReferenceTablesCache) {
        var data = get4AgeIndicatorRefData(ind, sex, ageInDays);
        if(data.length > 0)
            return new ReferenceData(ageInDays, undefined,
                data[0]['L'], data[0]['M'], data[0]['S']);
        else
            // if no data have been found from the DB, we return extreme values
            return new ReferenceData();
    }
    else
        throw new NotImplementedException();
}


// Crops a value to a defined precision.
// If the value is too large for truncation to the specified number of decimal
// places, the method simply truncates the value to an integer.
// Precision set to 2 by default in case invalid value or no value passed.
// Warning: this function does its job for small values of 'value' and precision
// as intended but leads to the loss of precision in case of large numbers so
// please do not use it as a general-purpose symetric crop function for
// different data sets.
function symetricCrop(value, precision) {
    if(isUnknownOrNaN(value))
        return value;
    if(isUnknownOrNaN(precision))
        precision = 2;
    else if(precision < 0)
        precision = 0;
    else
        precision = parseInt(precision);

    var output = parseInt(value);
    var ten_to_precision = Math.pow(10, precision);
    if(!isFinite(ten_to_precision))
        return output;
    var step = value * ten_to_precision;
    if(!isFinite(step) || isNaN(step))
        return output;
    step = parseInt(step) / ten_to_precision;
    if(!isFinite(step) || isNaN(step))
        return output;
    else
        return step;
}


/* This function assumes access to function get4LengthOrHeightRefData(ind, sex,
   lengthOrHeight, interpolate) which provides L, M, S for a given sex,
   'lengthOrHeight' and 'interpolate' from whatever database they are stored in.
   This function and the function it assumes access to are analogous to
   functions used to provide similar functionality for age-related indicators so
   please see comment preceding function get4AgeIndicatorReference() above to
   understand how to write get4LengthOrHeightRefData()).
*/
function get4LengthOrHeightIndicatorReference(ind, sex, lengthOrHeight) {
    var croppedLH = symetricCrop(lengthOrHeight, 1);
    var interpolate = (croppedLH != lengthOrHeight);
    if(!_useReferenceTablesCache) {
        var data = get4LengthOrHeightRefData(ind, sex, lengthOrHeight,
            interpolate);
        if(data.length > 0)
            return new ReferenceData(lengthOrHeight, undefined,
                data[0]['L'], data[0]['M'], data[0]['S']);
        else
            // if no data have been found from the DB, we return extreme values
            return new ReferenceData();
    }
    else
        throw new NotImplementedException();
}


/* Given a ReferenceData structure, this method returns a result with the
correct P and Z.
 Arguments: ReferenceData refDat,
            boolean computeFinalZScore - specifies if final z-score must be
                                         computed. False for HC4A and H4A
 Returns: IndicatorValue
 */
function calculateZandP(refDat, computeFinalZScore) {
    /* Create IV containing an "invalid" value (undefined, undefined) before we
    know if it can be computed.
     */
    var output = new IndicatorValue()

    if(refDat.Y === undefined || refDat.M === undefined || refDat.L === undefined)
        return output; // returns an "invalid" value (undefined, undefined)

    /* The following block of code (till the except/catch below) was enclosed
     in a try in python and c#.  The conditionals above and below have been
     modified to avoid using them to control the flow (which is standard in
     python but a bad practice in C# and most other languages. */
    if(refDat.L != 0 && refDat.S != 0) {
        if(refDat.S === undefined)
            return output; // returns an "invalid" value (undefined, undefined)
        else
            output.Z = (
                Math.pow((refDat.Y / refDat.M), refDat.L) - 1.0
            ) / (refDat.L * refDat.S);
    }
    else
        output.Z = Math.pow((refDat.Y / refDat.M), refDat.L);

    if(computeFinalZScore) {
        // The following assigns Z-score = +-3SD to Z-scores > 3SD - 2SD or < -2SD - -3SD
        if(output.Z < -3) {
            var SD2neg = refDat.M * Math.pow((1 + refDat.L * refDat.S * -2),
                    (1 / refDat.L));
            var SD3neg = refDat.M * Math.pow((1 + refDat.L * refDat.S * -3),
                    (1 / refDat.L));
            output.Z = -3 - (SD3neg - refDat.Y) / (SD2neg - SD3neg);

        }
        if(output.Z > 3) {
            var SD2pos = refDat.M * Math.pow((1 + refDat.L * refDat.S * 2),
                (1 / refDat.L));
            var SD3pos = refDat.M * Math.pow((1 + refDat.L * refDat.S * 3),
                    (1 / refDat.L));
            output.Z = 3 + (refDat.Y - SD3pos) / (SD3pos - SD2pos);
        }
    }

    //#C#                catch (Exception)
    //except FloatingPointError:  # V.Cole: using more specific trap. WHO was too liberal.
    //#C#                {
    //#C#                    //reset Z and P
    //#C#                    output = new IndicatorValue(true);
    // the exception handling code used to end at the above line

    // Compute the associated percentile
    output.P = centile(output.Z);
    return output
}


// Computes the weight-for-age indicator (aka WAZ) result based on the Python
// code.
// Compared to the Python code, the C# implementation had one more argument -
// AnthroMode currentStandards - used to choose between the WHO and NCHS
// reference data.
function computeWeight4Age(ageInDays, weight, sex, hasOedema) {
    if(hasOedema || ageInDays < 0 || ageInDays > MAXDAYS ||
       !(weight >= INPUT_MINWEIGHT))
        return new IndicatorValue();
    //Getting WHO reference data
    var rd = get4AgeIndicatorReference(GraphIndicator.Weight4Age, sex,
        Math.round(ageInDays));
    //Set the current weight value
    rd.Y = weight;

    return calculateZandP(rd, true);
}


// Computes the length/height-for-age indicator result (aka HAZ).
// Compared to the Python code, the C# implementation had one more argument -
// AnthroMode currentStandards - used to choose between the WHO and NCHS
// reference data.
function computeLengthOrHeight4Age(ageInDays, lengthOrHeight, sex) {
    if (ageInDays < 0 || ageInDays > MAXDAYS || !(lengthOrHeight >= 1))
        return new IndicatorValue();
    // The Python code did not follow the C# implementation and did not round
    // the ageInDays but it did that in function computeWeight4Age() above so
    // I am going to keep the original (i.e. C#) behaviour.
    var rd = get4AgeIndicatorReference(GraphIndicator.LengthOrHeight4Age, sex,
        Math.round(ageInDays));
    rd.Y = lengthOrHeight;

    return calculateZandP(rd, false);
}


// Computes the weight-for-length/height indicator result (aka WHZ).
// Compared to the Python code, the C# implementation had one more argument -
// AnthroMode currentStandards - used to choose between the WHO and NCHS
// reference data.
// <param name="weight">In kg.</param>
// <param name="lengthOrHeight">In cm.</param>
// <param name="sex"></param>
// <param name="useLength">true if the value passed for lengthOrHeight is a
//      length, not a height.</param>
// <param name="hasOedema">true or false</param>
function computeWeight4LengthOrHeight(weight, lengthOrHeight, sex, useLength,
                                      hasOedema) {
    if(hasOedema || !(weight >= INPUT_MINWEIGHT))
        return new IndicatorValue();

    var rd;
    if(useLength) {
        if(lengthOrHeight >= MINLENGTH && lengthOrHeight <= MAXLENGTH)
            rd = get4LengthOrHeightIndicatorReference(
                GraphIndicator.Weight4Length, sex, lengthOrHeight);
        else
            return new IndicatorValue();
    }
    else {
        if(lengthOrHeight >= MINHEIGHT && lengthOrHeight <= MAXHEIGHT)
            rd = get4LengthOrHeightIndicatorReference(
                GraphIndicator.Weight4Height, sex, lengthOrHeight);
        else
            return new IndicatorValue();
    }

    rd.Y = weight;
    return calculateZandP(rd, true);
}


// Computes the anthro result for the given raw data values.
//C#        /// Unknown argument values must be passed with null (e.g. do NOT use
//C#        /// funny values like -1 to specify an unknown weight - just pass null).
function getAnthroResult(ageInDays, sex, weight, height, isRecumbent,
                         hasOedema, hc, muac, tsf, ssf) {
    //PYTHON I am ignoring this rounding -- floating calculations don't need it.
    //C# // AS this value is checked several times, we crop it here only
    //C# if (height != null)
    //C# {
    //C#     height = Round(height.Value, 2);
    //C# }
    //C# AnthropometricResult ar = new AnthropometricResult();
    //PYTHON     ar = AnthropometricResult()
    var ar = new AnthropometricResult();
    ar.sex = sex;
    //check if we have enough data to compute at least one indicator
    ar.ageUnknown = isUnknownOrNaN(ageInDays);
    ar.heightUnknown = isUnknownOrNaN(height);

    if(sex === undefined || sex === null ||
        (isUnknownOrNaN(ageInDays) && isUnknownOrNaN(height)))
        return ar; // not enough data to compute any indicator

    // check weight
    if(isUnknownOrNaN(weight))
        ar.weight = NaN;
    else
        ar.weight = weight;

    // prepare for length/height adjustment
    ar.lengthOrHeightAdjusted = NaN;
    ar.isLength = isRecumbent;
    if(!isUnknownOrNaN(ageInDays)) {
        ar.ageInDays = ageInDays;

        // first: check & adjust length/height
        if(!isUnknownOrNaN(height)) {
            var adjusted = getAdjustedLengthOrHeight(Math.round(ar.ageInDays),
                height, isRecumbent);
            ar.lengthOrHeightAdjusted = adjusted.lengthOrHeight;
            ar.isLength = adjusted.isLength;
        }

        // WAZ
        var ivw = computeWeight4Age(ar.ageInDays, ar.weight, ar.sex, hasOedema);
        ar.PW4A = ivw.P;
        ar.ZW4A = ivw.Z;

        // length/height-for-age aka HAZ
        var ivh = computeLengthOrHeight4Age(ar.ageInDays,
            ar.lengthOrHeightAdjusted, ar.sex);
        ar.ZLH4A = ivh.Z;
        ar.PLH4A = ivh.P;
    }

    // check if height known and age not above 60 completed months
    var ageAbove60CompletedMonths = false;
    if(!isUnknownOrNaN(ageInDays))
        ageAbove60CompletedMonths = ageInDays > MAXDAYS;
    // check if WHZ can be calculated, if not set as undefined
    if(!isUnknownOrNaN(height) && !ageAbove60CompletedMonths) {
        ar.lengthOrHeight = height;
        if(isUnknownOrNaN(ar.lengthOrHeightAdjusted)) {
            var adjusted_height_mindays = ar.isLength ? HEIGHT_MINDAYS - 1 : HEIGHT_MINDAYS;
            ar.lengthOrHeight = getAdjustedLengthOrHeight(
                adjusted_height_mindays, height, isRecumbent);
            ar.lengthOrHeightAdjusted = ar.lengthOrHeight;
        }

        // weight-for-length/height aka WHZ
        var ivwhz = computeWeight4LengthOrHeight(
            ar.weight, ar.lengthOrHeightAdjusted, ar.sex, ar.isLength,
            hasOedema
        );
        ar.ZW4LH = roundFloat(ivwhz.Z, DEFAULTPRECISION_ZSCORE);
        ar.PW4LH = roundFloat(ivwhz.P, DEFAULTPRECISION_PERCENTILE);
    } else {
        ar.lengthOrHeight = undefined;
        ar.lengthOrHeightAdjusted = undefined;
        ar.ZW4LH = undefined;
        ar.PW4LH = undefined;
    }
    return ar;
}

