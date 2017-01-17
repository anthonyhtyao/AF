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
