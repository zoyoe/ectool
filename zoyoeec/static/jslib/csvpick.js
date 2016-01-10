var zoyoe = document.zoyoe;
if(zoyoe == undefined){
  document.zoyoe = {};
  zoyoe = document.zoyoe
}

/* csv table should not exists together with pdf table when handling orders 
*/
zoyoe.csvtable = new function(){

/* same api like pdf Column but easiler implementation
*/
function Column(elements){
  this.putelement = function(ele){
    this.elements.push(ele);
  }
  this.absorb = function(elements){
    false;
  }
  this.elements = [];
  for (e in elements){
    this.putelement(elements[e]);
  }
}
this.columns = [];

this.load = function(wb_json){
  this.columns = [];
  var out = document.getElementById("csv-viewer");
  var output = wb_json;
  out.innerHTML = JSON.stringify(output);
  if (wb_json.length ==0){
    return;
  }
  for (key in wb_json[0]){
    var values = [];
    for (idx in wb_json){
       values.push(wb_json[idx][key]);
    }
    this.columns.push(values);
  }
}

this.pick = function(idx){
  return this.columns[idx % this.columns.length];
}

this.fill = function(ridx,values){
  var table = document.getElementById("tbody-instance");
  var trs = table.getElementsByTagName("tr");
  for (idx in values){
    if (idx < trs.length){
      var str = values[idx].trim();
      str = str.replace(/\t\n/g,"").replace(/&nbsp;/g,"").replace(/\$/g," ");
      str = str.replace(/\s+/g,' ')
      trs[idx].getElementsByTagName("td")[ridx].innerHTML = str;
    }else{
      tr = document.createElement("tr");
      tr.innerHTML = ("<th onclick='this.parentElement.parentElement.removeChild(this.parentElement)' ><i class='fa fa-times'></i></th><td/><td/><td/><td/>");
      table.appendChild(tr);
      var str = values[idx].trim();
      str = str.replace(/\t\n/g,"").replace(/&nbsp;/g,"").replace(/\$/g," ");
      str = str.replace(/\s+/g,' ')
      tr.getElementsByTagName("td")[ridx].innerHTML = str;
    }
  }
  $('#table-edit td').on('change',function(evt,newvalue){
     this.style.backgroundColor = 'green';
  });
}

}/* zoyoe.pdftable */

function pick(ele,cidx){
  if(!ele.count){
    ele.count = 1;
  }else{
    ele.count += 1;
  }
  var values = zoyoe.csvtable.pick(ele.count);
  zoyoe.csvtable.fill(cidx,values);
  $('#table-edit').editableTableWidget({
  });
}
