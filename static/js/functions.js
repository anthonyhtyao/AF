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
 // Create and populate a data table.
    var data = [];
    data.push(
      {
        'start': new Date(2014,3,18),  // 'end': new Date(2010, 8, 2),  // end is optional
        'content': '太陽花學運'
      },
      {
        'start': new Date(2013,8,3),
        'content': '八月雪運動'
      },
      {
        'start': new Date(1947,2,28),
        'content': '二二八事件'
      }
    );
 // specify options
 var options = {
   "width":  "100%",
   "height": "300px",
  //  "style": "box", // optional
   "scale": links.Timeline.StepDate.SCALE.YEAR,
   "step": 1,
   "zoomMax": 1000 * 60 * 60 * 24 * 31 * 12 * 20,
   "zoomMin": 1000 * 60 * 60 * 24 * 31 * 12 * 2
 };
 // Instantiate our timeline object.
 var timeline = new links.Timeline(document.getElementById('mytimeline'));
 // Draw our timeline with the created data and options
 timeline.draw(data, options);
}
