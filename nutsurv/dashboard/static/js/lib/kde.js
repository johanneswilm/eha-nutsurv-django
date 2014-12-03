/* based on http://bl.ocks.org/jfirebaugh/900762 */

function kde(sample) {
  /* Epanechnikov kernel */
  function epanechnikov(u) {
    return Math.abs(u) <= 1 ? 0.75 * (1 - u*u) : 0;
  };

  var kernel = epanechnikov;
  return {
    scale: function(h) {
      kernel = function (u) { return epanechnikov(u / h) / h; };
      return this;
    },

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
