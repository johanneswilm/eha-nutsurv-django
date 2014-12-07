/* Licensed as open source/free software (MIT license) based on:
 http://bl.ocks.org/jfirebaugh/900762
 http://www.endmemo.com/program/js/jstatistics.php
 https://github.com/compute-io/iqr
 https://github.com/compute-io/quantile

 Authors:
 Johannes Wilm (composition)
 Athan Reines. (iqr + quantile)
 John Firebaugh (kde)


 */

function kde(sample) {
  /* Epanechnikov kernel */
  function epanechnikov(u) {
    return Math.abs(u) <= 1 ? 0.75 * (1 - u*u) : 0;
  }

  function variance(arr) {
    var len = 0, sum = 0, v = 0, mean, i;
    var sum=0;
    for(i=0;i<arr.length;i++) {
        len = len + 1;
        sum = sum + parseFloat(arr[i]);
    }

    if (len > 1) {
        mean = sum / len;
        for(i=0;i<arr.length;i++) {
            v = v + (arr[i] - mean) * (arr[i] - mean);
        }
        return v / len;
    }
    else {
         return 0;
    }
  }

  function iqr( arr, opts ) {

    function quantile( arr, p, opts ) {
	if ( !Array.isArray( arr ) ) {
		throw new TypeError( 'quantile()::invalid input argument. First argument must be an array.' );
	}
	if ( typeof p !== 'number' || p !== p ) {
		throw new TypeError( 'quantile()::invalid input argument. Quantile probability must be numeric.' );
	}
	if ( p < 0 || p > 1 ) {
		throw new TypeError( 'quantile()::invalid input argument. Quantile probability must be on the interval [0,1].' );
	}
	if ( arguments.length === 2 ) {
		opts = {};
	}
	var len = arr.length,
		id;

	if ( !opts.sorted ) {
		arr = arr.slice();
		arr.sort();
	}

	// Cases...

	// [0] 0th percentile is the minimum value...
	if ( p === 0.0 ) {
		return arr[ 0 ];
	}
	// [1] 100th percentile is the maximum value...
	if ( p === 1.0 ) {
		return arr[ len-1 ];
	}
	// Calculate the vector index marking the quantile:
	id = ( len*p ) - 1;

	// [2] Is the index an integer?
	if ( id === Math.floor( id ) ) {
		// Value is the average between the value at id and id+1:
		return ( arr[ id ] + arr[ id+1 ] ) / 2.0;
	}
	// [3] Round up to the next index:
	id = Math.ceil( id );
	return arr[ id ];
}

if ( arguments.length === 1 ) {
    opts = {
        'sorted': false
    };
}
if ( !opts.sorted ) {
    arr = arr.slice();
    arr.sort();
    opts.sorted = true;
}
return quantile( arr, 0.75, opts ) - quantile( arr, 0.25, opts );
}

  /* Automatically calculating bandwidth (h) based on calculations on top of page 1010 in www.stata.com/manuals13/r.pdf */
  var h = (0.9 * Math.min(Math.sqrt(variance(sample)),iqr(sample)/1.349)) / (Math.pow(sample.length, 1/5)),
  kernel = function (u) { return epanechnikov(u / h) / h; };

  return {
    points: function(points) {


      return points.map(function(x) {
        var y = sample.map(function (v) {
          return kernel(x - v);
      }).reduce(function(a, b) {
          return a + b;
      }) / sample.length;
        return [x, y];
      });
    }
  }
}
