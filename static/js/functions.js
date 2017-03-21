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
    $(".titleValided").hide();
    $(".titleError").hide();
    $('#authorSelect').multiSelect({
        selectableHeader: "<div class='custom-header'>Selectable Users</div>",
        selectionHeader: "<div class='custom-header'>Authors</div>",
        afterSelect: function () {getAuthorList();},
        afterDeselect: function () {getAuthorList();},
    });
    getAuthorList();
});

function getAuthorList() {
    var lst = document.getElementById("authorList");
    var select = document.getElementById("authorSelect");
    var result = "";
    var options = select && select.options;
    var opt;
    var n=0;
    for (var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];
        if (opt.selected) {
          if (n!=0)
              result += ", ";
          result += opt.text;
          n++;
        }
    }
    $("#authorList").html(result);
}

function checkTitleValidity(x) {
    var value = document.getElementById("title").value;
    // Check if input is blank
    if (value.replace(/^\s+|\s+$/g, "").length == 0) {
      $(".titleValided").hide();
      $("#titleInput").removeClass("has-success");
      $(".titleError").show();
      $("#titleInput").addClass("has-error");
      $("#titleErrorMsg").html("Title invalid");
    }
    else {
        preAjax();
        $.ajax({
            type:"GET",
            url:"checktitlevalidity",
            data:{title:value},
            success: function(v) {
                if (v==1) {
                    $(".titleValided").show();
                    $("#titleInput").addClass("has-success");
                    $(".titleError").hide();
                    $("#titleInput").removeClass("has-error");
                }
                else {
                  $(".titleValided").hide();
                  $("#titleInput").removeClass("has-success");
                  $(".titleError").show();
                  $("#titleInput").addClass("has-error");
                  $("#titleErrorMsg").html("Title has been used");
                }
            }
        });
    }
}

function tooltipArchiveImg(x) {
    var value = $(x).attr('value');
    $(x).tooltip({content:'<img width="100%" src=' + value + '/>'});
}

function closeTooltip(x) {
    $(x).tooltip("close");
}

function deleteArticle(type,id) {
  data={'type':type,'id':id};
  preAjax();
  $.ajax({
    type:"POST",
    url:"/article/delete",
    data:JSON.stringify(data),
    success: function() {
      location.href="/";
    }
  });
}

function setLanguage(language) {
  preAjax();
  $.ajax({
     type:"POST",
     url:"/session_language/",
     data: { language:language},
     success: function(){
       $("#loading").hide();
       document.location.reload();
     }
  });
}

function preAjax() {
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

// Delete event selected on timeline div, add event in timeline_data_changed
function deleteEvent(row) {
  var obj = timeline_data[row];
  if (obj.id != 'new') {
    obj['action'] = 'delete';
    timeline_data_changed.push(obj);
  }
  var data={'action':'delete','id':obj.id};
  preAjax();
  $.ajax({
    type:"POST",
    url:"/timeline/save",
    data:JSON.stringify(data),
    success: function() {
      timeline.deleteItem(row);
      var info = document.getElementById('info');
      info.innerHTML =
      "<span>Detail : </span> <span onclick='openTimelineDialog()' style='color:green' class='glyphicon glyphicon-plus'></span>";
    }
  });
}

function saveEvent(row=-1) {
  var range = timeline.getVisibleChartRange();
  var start = new Date(document.getElementById("timeline_start").value);
  var endValue = document.getElementById("timeline_end").value;
  var content = document.getElementById("timeline_content").value;
  $("#timelineDialog").dialog("close");
  preAjax();
  if (row==-1) {
    var item = {'start':start,'content':content,'className':'timeline-event-select','action':'add'};
    data={'action':'add','content':item.content,'start':jsDateConvert(item.start)};
    if (endValue) {
      item['end'] = new Date(endValue);
      data['end'] = endValue;
    }
    $.ajax({
      type:"POST",
      url:"/timeline/save",
      data:JSON.stringify(data),
      success: function(data) {
        item.id = JSON.parse(data['id']);
        timeline.addItem(item);
        row = timeline_data.length-1;
        timeline.setSelection([{
          'row': row
        }]);
        var info = document.getElementById('info');

        info.innerHTML =
        "<span>Detail : </span> <span onclick='openTimelineDialog()' style='color:green' class='glyphicon glyphicon-plus'></span>"
        + "<span onclick='deleteEvent(" + row + ")' style='color:red' class='glyphicon glyphicon-minus'></span>"
        + "<span onclick='openTimelineDialog(" + row + ")' class='glyphicon glyphicon-pencil'></span>"
        + "<br>ID : " + item.id
        + "<br>Start : " + jsDateConvert(item.start)
        + "<br>End : " + jsDateConvert(item.end)
        + "<br>Content : " + content;
      }
    });
  }
  else {
    var event = timeline_data[row];
    event.start = start;
    event.content = content;
    var data = {};
    data.id = event.id;
    data.content = event.content;
    data.action = 'edit';
    data.start = jsDateConvert(event.start);
    if (endValue) {
      event.end = new Date(endValue);
      data['end'] = endValue;
    }
    $.ajax({
      type:'POST',
      url:'/timeline/save',
      data:JSON.stringify(data),
      success: function(){
        timeline.redraw();
        timeline.setSelection([{'row': row}]);
        var info = document.getElementById('info');
        info.innerHTML =
        "<span>Detail : </span> <span onclick='openTimelineDialog()' style='color:green' class='glyphicon glyphicon-plus'></span>"
        + "<span onclick='deleteEvent(" + row + ")' style='color:red' class='glyphicon glyphicon-minus'></span>"
        + "<span onclick='openTimelineDialog(" + row + ")' class='glyphicon glyphicon-pencil'></span>"
        + "<br>ID : " + event.id
        + "<br>Start : " + jsDateConvert(event.start)
        + "<br>End : " + jsDateConvert(event.end)
        + "<br>Content : " + content;
      }
    });
  }
};

function jsDateConvert(time) {
  var s = "";
  if (time) {
    var date = new Date(time);
    var year = date.getFullYear();
    var month = date.getMonth()+1;
    var d = date.getDate();
    s = year + "-" + month + "-" + d;
  }
  return s;
};

function event_to_period(event) {
  var s = jsDateConvert(event.start);
  if (event.end) {
    s += " ~ ";
    s += jsDateConvert(event.end);
  }
  return s;
}

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
    return new Date(lst[0],lst[1]-1,lst[2]);
  };

  var options = {
    "width":  "100%",
    "height": "200px",
    "style": "dot", // optional
    //"scale": links.Timeline.StepDate.SCALE.YEAR,
    //"step": 1,
    "zoomMax": 1000 * 60 * 60 * 24 * 31 * 12 * 50,
    "zoomMin": 1000 * 60 * 60 * 24 * 31 * 12 * 5
  };
  timeline = new links.Timeline(e);

  function onSelectEdit() {
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
            + "<br>Content : " + eventSelected.content
	    + "<br><a href='/events/"+eventSelected.slg+"'>Go to event page</a>";
        }
        else if (action == "select") {
          e.setAttribute("data-value", eventSelected.id);
          var input = document.getElementById("timeline_event_input");
          input.value = eventSelected.id;
          var selected = document.getElementById("eventSelected");
          selected.innerHTML = jsDateConvert(eventSelected.start) + " " + eventSelected.content + "<sup style='color:red' onclick='cancelEventSelected()'> X </sup>";
        }
	else if (action == "read") {
	  var info = document.getElementById('info');
	  info.innerHTML = event_to_period(eventSelected)
            + " <a href='/events/"+eventSelected.slg+"'>"+eventSelected.content+"</a> : "
	    + eventSelected.abstract;
	}
      }
    }
  };
  links.events.addListener(timeline,'select',onSelectEdit);
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
          event['abstract'] = details[i].fields.abstract;
          event['slg'] = events[i].fields.slg;
          if (event.id==ind) {
            event['className'] = 'timeline-event-target';
            row=i;
	    var info = document.getElementById('info');
	    info.innerHTML = event_to_period(event)
              + " <a href='/events/"+event.slg+"'>"+event.content+"</a> : "
	      + event.abstract;
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
