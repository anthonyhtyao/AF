var searchData = {'email':'','family_name':'','name':''};

$(document).ready( function() {
  console.log(123456);
});

function searchClient(t) {
  var boolLst = ['info','payment'];
  var key = $(t).data('value');
  if (boolLst.indexOf(key)>=0)
      var val = $(t).is(':checked')?1:0;
  else
      var val = $(t).val();
  searchData[key] = val;
  url = 'search_client'
  var i = 0;
  for (var key in searchData) {
    if (searchData[key]) {
      if (i)
        url += "&";
      else
        url += "?";
        url = url + key +"=" + searchData[key];
      i++;
    }
  }
    
    $(".indTable").html('').load(url);

}

function genAdressPDF() {
    console.log("gen adress buttom clicked");
    
    var idLst = [];
    $("#clientsTable tr").each(function() {
        var id = $(this).find("td:first").text();
        if (id)
            idLst.push(parseInt(id));
    });
    data = {'clientsLst':idLst}
    console.log(idLst);
    $("#clientsIDInput").val(JSON.stringify(data));
    $("#genAdressPDFForm").submit();
    /*$.ajax({
        type:'POST',
        url:'/abo/adress_pdf',
        data:JSON.stringify(data),
        success: function(data) {
            console.log(data);
            var blob=new Blob([data]);
            var link=document.createElement('a');
            link.href=window.URL.createObjectURL(blob);
            link.download="Dossier_"+new Date()+".pdf";
            link.click();
        }
    });
*/
}
