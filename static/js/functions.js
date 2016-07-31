$(document).ready( function() {

    $("#login-btn").click( function (event) {
	    $("#dialog").dialog("open");
	    return false;
	});
    $("#dialog").dialog({autoOpen : false, modal : true, show : "blind", hide : "blind"});
    $("#loginErrorDialog").dialog();

    $("#login_form").submit(function (event) {
        $.ajax({
            type:"POST",
            url:"/login/",
            data:$("#login_form").serialize(),
        });
    });
});

function tooltipArchiveImg(x) {
    var value = $(x).attr('value');
    $(x).tooltip({content:'<img width="100%" src=' + value + '/>'});
}
function closeTooltip(x) {
    $(x).tooltip("close");
}



// Called when the Visualization API is loaded.
function drawVisualization() {

  function turnToDate(date) {
    var lst = date.split("-");
    return new Date(lst[0],lst[1],lst[2]);
  };
  $.ajax({
      type:"GET",
      url:"/timelinedata/",
      data:{},
      success: function(data) {
        var events = JSON.parse(data['events']);
        var details = JSON.parse(data['details']);
        var d = [];
        for (var i = 0; i<events.length;i++) {
          var event = {};
          event['start'] = turnToDate(events[i].fields.start);
          if (events[i].fields.end != null) {
            event['end'] = turnToDate(events[i].fields.end);
          }
          event['content'] = details[i].fields.content;
          d.push(event);

        }
        var options = {
          "width":  "100%",
          "height": "200px",
          "style": "box", // optional
          "scale": links.Timeline.StepDate.SCALE.YEAR,
          "step": 1,
          "zoomMax": 1000 * 60 * 60 * 24 * 31 * 12 * 20,
          "zoomMin": 1000 * 60 * 60 * 24 * 31 * 12 * 2
        };
        // Instantiate our timeline object.
        var timeline = new links.Timeline(document.getElementById('mytimeline'));
        // Draw our timeline with the created data and options
        timeline.draw(d, options);
        timeline.setSelection([{row:0}]);
      }
  });
}
