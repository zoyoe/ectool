function ebayGalleryAjax(){
var xmlhttp = new XMLHttpRequest();
var container = document.getElementById('zoyoe-ebayitemlist');
xmlhttp.onreadystatechange=function(){
  if(xmlhttp.readyState==4){
    if(xmlhttp.status==200){
      var ret = xmlhttp.responseText;
      var info = ret.split(",")
      var items = document.querySelectorAll('div .item');
      for (var i = 0;i<12;i++){
         items[i].getElementsByTagName("a")[0].href = info[4*i+0]
         items[i].getElementsByTagName("img")[0].src = info[4*i+1];
         items[i].getElementsByTagName("div")[0].innerHTML = info[4*i+2]
         items[i].getElementsByTagName("div")[1].innerHTML = "AUD&nbsp;" + info[i*4+3];
      }
    }
  }
  document.getElementById('zoyoe-loading').style.display = "none";
};
var ref = 'http://' + document.zoyoe.host + '/ebayjson/?sellerid=';
ref += document.zoyoe.sellerid;
var method ='GET';
xmlhttp.open(method,ref,true);
xmlhttp.send();
}

ebayGalleryAjax();
