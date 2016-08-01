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
  var e = document.getElementById('mytimeline');
  var ind = e.innerHTML;
  var d = [];
  function turnToDate(date) {
    var lst = date.split("-");
    return new Date(lst[0],lst[1],lst[2]);
  };

  function jsDateConvert(time) {
    var s = "";
    if (time) {
      var date = new Date(time);
      var year = date.getFullYear();
      var month = date.getMonth();
      var d = date.getDate();
      s = year + "-" + month + "-" + d;
    }
    else
      s = "N/A";
    return s;
  };
  var options = {
    "width":  "100%",
    "height": "200px",
    "style": "box", // optional
    "scale": links.Timeline.StepDate.SCALE.YEAR,
    "step": 1,
    "zoomMax": 1000 * 60 * 60 * 24 * 31 * 12 * 40,
    "zoomMin": 1000 * 60 * 60 * 24 * 31 * 12 * 10
  };
  if (ind == -1)
    options['editable'] = true;
  var timeline = new links.Timeline(e);

  function onselect() {
    var sel = timeline.getSelection();
    if (sel.length) {
      if (sel[0].row != undefined) {
        var row = sel[0].row;
        var info = document.getElementById('info');
        info.innerHTML = "Start : " + jsDateConvert(d[row].start) + "<br>End : " + jsDateConvert(d[row].end) + "<br>Content : " + d[row].content;
      }
    }
  };
  if (ind == -1)
    links.events.addListener(timeline,'select',onselect);
  $.ajax({
      type:"GET",
      url:"/timelinedata/",
      data:{},
      success: function(data) {
        var events = JSON.parse(data['events']);
        var details = JSON.parse(data['details']);

        for (var i = 0; i<events.length;i++) {
          var event = {};
          event['start'] = turnToDate(events[i].fields.start);
          if (events[i].fields.end != null) {
            event['end'] = turnToDate(events[i].fields.end);
          }
          event['content'] = details[i].fields.content;
          if (i==ind) {
            event['className'] = 'timeline-event-target';
          }
          d.push(event);
          timeline.draw(d, options);
          timeline.setSelection([{row:ind}]);
        }
      }
  });
  // Instantiate our timeline object.
  // Draw our timeline with the created data and options
}
