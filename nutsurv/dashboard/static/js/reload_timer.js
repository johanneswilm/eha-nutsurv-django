var lastUpdate = parseInt((new Date)/1000);

function drawTimer() {
  var totalSeconds = parseInt((new Date)/1000) - lastUpdate;
  var minutes = Math.floor(totalSeconds / 60);
  var seconds = totalSeconds - minutes * 60;

  if (seconds < 10) { seconds = '0'+seconds; }

  jQuery('#last_update .button_label').html(minutes+':'+seconds);
}

function setTimer() {

  // Timer set to X*60000 milliseconds (X is minutes)
  setInterval(function() { window.location.reload(); }, 5*60000);

  // Redraw timer every second
  setInterval(drawTimer, 1000);

}

setTimer()
