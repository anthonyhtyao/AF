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
