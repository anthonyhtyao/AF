var timeline;
var timeline_data;
var timeline_data_changed;
$(document).ready( function() {

    $("#login-btn").click( function (event) {
	    $("#dialog").dialog("open");
	    return false;
	});
    $("#dialog").dialog({autoOpen : false, modal : true, show : "blind", hide : "blind"});
    $("#timelineDialog").dialog({autoOpen : false, modal : true, show : "blind", hide : "blind"});
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

//---------- Here is function for timeline -----------
// Jump up timeline event edit dialog
function openTimelineDialog(row=-1) {
  if (row>=0) {
    var event = timeline_data[row];
    document.getElementById("timeline_start").value = jsDateConvert(event.start);
    document.getElementById("timeline_end").value = jsDateConvert(event.end);
    document.getElementById("timeline_content").value = event.content;
  }
  document.getElementById("timeline_save").setAttribute("onclick","saveEvent(" + row + ")");
  $("#timelineDialog").dialog("open");
}

// Send timeline_data_changed to djangos views
function updateTimelineData() {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');
  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
  for (var i=0; i<timeline_data.length; i++) {
    var obj = timeline_data[i];
    if (obj.id == "new") {
      var tmp = obj;
      tmp.start = jsDateConvert(obj.start);
      var end = jsDateConvert(obj.end);
      if (end != 'N/A') {
        tmp.end = end;
      }
      timeline_data_changed.push(tmp);
    }
  }
  $.ajax({
    type:"POST",
    url:"/timeline/save",
    data:JSON.stringify(timeline_data_changed)
  });
}

// Delete event selected on timeline div, add event in timeline_data_changed
function deleteEvent(row) {
  var obj = timeline_data[row];
  if (obj.id != 'new') {
    obj['action'] = 'delete';
    timeline_data_changed.push(obj);
  }
  timeline.deleteItem(row);
  var info = document.getElementById('info');
  info.innerHTML =
    "<span>Detail : </span> <span onclick='openTimelineDialog()' style='color:green' class='glyphicon glyphicon-plus'></span>";
}

function saveEvent(row=-1) {
  var range = timeline.getVisibleChartRange();
  var start = new Date(document.getElementById("timeline_start").value);
  var endValue = document.getElementById("timeline_end").value;
  var content = document.getElementById("timeline_content").value;
  $("#timelineDialog").dialog("close");

  if (row==-1) {
    var item = {'id':'new','start':start,'content':content,'className':'timeline-event-select','action':'edit'};
    if (endValue) {
      item['end'] = new Date(endValue);
    }
    timeline.addItem(item);
    row = timeline_data.length-1;
    timeline.setSelection([{
      'row': row
    }]);
    var info = document.getElementById('info');
    console.log("open info");
    info.innerHTML =
      "<span>Detail : </span> <span onclick='openTimelineDialog()' style='color:green' class='glyphicon glyphicon-plus'></span>"
      + "<span onclick='deleteEvent(" + row + ")' style='color:red' class='glyphicon glyphicon-minus'></span>"
      + "<span onclick='openTimelineDialog(" + row + ")' class='glyphicon glyphicon-pencil'></span>"
      + "<br>ID : new"
      + "<br>Start : " + jsDateConvert(item.start)
      + "<br>End : " + jsDateConvert(item.end)
      + "<br>Content : " + content;
  }
  else {
    var event = timeline_data[row];
    event.start = start;
    event.content = content;
    var tmp = {};
    tmp.id = event.id;
    tmp.content = event.content;
    tmp.action = 'edit';
    tmp.start = jsDateConvert(event.start);
    timeline_data_changed.push(tmp);
    timeline.redraw();
    timeline.setSelection([{'row': row}]);
  }
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

function cancelEventSelected() {
  var e = document.getElementById('mytimeline');
  e.setAttribute("data-value",0);
  var selected = document.getElementById("eventSelected");
  selected.innerHTML = "";
  var input = document.getElementById("timeline_event_input");
  input.value=0;
  timeline.redraw();
}

// Called when the Visualization API is loaded.
function drawVisualization() {
  var e = document.getElementById('mytimeline');
  var action = e.getAttribute("data-action");
  var ind = e.getAttribute("data-value");
  timeline_data = [];
  timeline_data_changed = [];
  function turnToDate(date) {
    var lst = date.split("-");
    return new Date(lst[0],lst[1],lst[2]);
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
  timeline = new links.Timeline(e);

  function onselect() {
    var sel = timeline.getSelection();
    if (sel.length) {
      if (sel[0].row != undefined) {
        var row = sel[0].row;
        var eventSelected = timeline_data[row];
        if (action == "edit") {
          var info = document.getElementById('info');
          info.innerHTML =
            "<span>Detail : </span> <span onclick='openTimelineDialog()' style='color:green' class='glyphicon glyphicon-plus'></span>"
            + "<span onclick='deleteEvent(" + row + ")' style='color:red' class='glyphicon glyphicon-minus'></span>"
            + "<span onclick='openTimelineDialog(" + row + ")' class='glyphicon glyphicon-pencil'></span>"
            + "<br>ID : " + eventSelected.id
            + "<br>Start : " + jsDateConvert(eventSelected.start)
            + "<br>End : " + jsDateConvert(eventSelected.end)
            + "<br>Content : " + eventSelected.content;
        }
        else if (action == "select") {
          e.setAttribute("data-value", eventSelected.id);
          var input = document.getElementById("timeline_event_input");
          input.value = eventSelected.id;
          var selected = document.getElementById("eventSelected");
          selected.innerHTML = jsDateConvert(eventSelected.start) + " " + eventSelected.content + "<sup style='color:red' onclick='cancelEventSelected()'> X </sup>";
        }
      }
    }
  };
  if (action != "read")
    links.events.addListener(timeline,'select',onselect);
  $.ajax({
      type:"GET",
      url:"/timelinedata/",
      data:{},
      success: function(data) {
        var events = JSON.parse(data['events']);
        var details = JSON.parse(data['details']);
        var row;
        for (var i = 0; i<events.length;i++) {
          var event = {};
          event['id'] = events[i].pk;
          event['start'] = turnToDate(events[i].fields.start);
          if (events[i].fields.end != null) {
            event['end'] = turnToDate(events[i].fields.end);
          }
          event['content'] = details[i].fields.content;
          if (event.id==ind) {
            event['className'] = 'timeline-event-target';
            row=i;
          }
          timeline_data.push(event);
          timeline.draw(timeline_data, options);
          timeline.setSelection([{row:row}]);
        }
      }
  });
  // Instantiate our timeline object.
  // Draw our timeline with the created data and options
}
