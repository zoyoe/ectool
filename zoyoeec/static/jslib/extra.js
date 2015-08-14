function ebayGalleryAjax(){
var xmlhttp = new XMLHttpRequest();
var container = document.getElementById('zoyoe-ebayitemlist');
xmlhttp.onreadystatechange=function(){
  if(xmlhttp.readyState==4){
    if(xmlhttp.status==200){
      container.innerHTML=xmlhttp.responseText;
    }
  }
  document.getElementById('zoyoe-loading').style.display = "none";
};
var ref = 'http://' + document.zoyoe.host + '/ebay/?sellerid=';
ref += document.zoyoe.sellerid;
var method ='GET';
xmlhttp.open(method,ref,true);
xmlhttp.send();
}

ebayGalleryAjax();
