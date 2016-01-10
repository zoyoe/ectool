var zoyoe = document.zoyoe;
if(zoyoe == undefined){
  document.zoyoe = {};
  zoyoe = document.zoyoe
}
zoyoe.pdftable = new function(){
function n2px(n){
  return n+"px";
}

function px2n(px){
  parseInt(px);
}

function pt2r(pt){
  var r = parseFloat(pt);
  return r;
}

function n2pt(n){
  return n+"pt";
}

function roundpt(pt){
  return n2pt(Math.round(pt2r(pt)));
}

function Column(elements){
  this.putelement = function(ele){
    this.elements.push(ele);
    var left = Math.round(pt2r(ele.offsetLeft));
    var top = Math.round(pt2r(ele.offsetTop));
    var width = Math.round(pt2r(ele.offsetWidth));
    if (ele.attributes && ele.attributes['data-canvas-width']){
       width = Math.round(pt2r(ele.attributes['data-canvas-width'].value));
    }
    var right = left+width;
    var height = Math.round(pt2r(ele.offsetHeight));
    var bottom = top + height;
    if(this.left > left ){
      this.left = left;
    }
    if(this.right < right){
      this.right = right;
    }
  }
  this.absorb = function(elements){
    var ac = 0;
    for (e in elements){
      var ele = elements[e];
      var left = Math.round(pt2r(ele.offsetLeft));
      var top = Math.round(pt2r(ele.offsetTop));
      var width = Math.round(pt2r(ele.offsetWidth));
      if (ele.attributes && ele.attributes['data-canvas-width']){
         width = Math.round(pt2r(ele.attributes['data-canvas-width'].value));
      }
      var right = left+width;
      var height = Math.round(pt2r(ele.offsetHeight));
      var bottom = top + height;
      if(this.left >= left -3 && this.right <=right +3){
        /* Current within range */
        this.putelement(ele);
        ac += 1;
      }else{
        if(this.left <= left+3 && this.right >=right - 3){
          /* Current within range */
          this.putelement(ele);
          ac += 1;
        }
      }
    }
    if (ac > 0){
      if (ac == elements.length){
        return true;
      }else{
        alert("there is a bug here, analysing pdf table fail");
      }
    }else{
      return false; 
    }
  }
  this.elements = [];
  this.left = 9999999;
  this.right = 0;
  this.top = 9999999;
  this.bottom = 0;
  for (e in elements){
    this.putelement(elements[e]);
  }
}

this.load = function(){
  var doc = document.getElementById("pdf-viewer");
  doc.style.height = n2px(doc.offsetWidth * 1.5);
  if(doc.src!=""){
    doc.src = "/static/jslib/pdf/web/viewer.html";
  }
}

this.pick = function(idx){
    var coltotal = {};
    var rowtotal = {};
    var col = {}
    var doc = document.getElementById("pdf-viewer");
    var pc = doc.contentWindow.document.getElementById('pageContainer1');
    var selection = doc.contentWindow.getSelection();
    var elements = pc.getElementsByTagName("div");
    var topb = 10000000;
    var bottomb = 0;

    /* first scan 
       work out the top boundry and bottom boundry
    */
    for (var i = 0;i < elements.length; i++){
      var element = elements[i];
      if(element.children.length){
        continue;
      }
      var left = element.style.left;
      var top = element.style.top;
      if(!selection.containsNode(element,true)){
        continue;
      }
      if(topb >= pt2r(top)){
        topb = pt2r(top);
      }
      if(bottomb <= pt2r(top)){
        bottomb = pt2r(top);
      }
    }
    /* second scan */
    for (var i = 0;i < elements.length; i++){
      var element = elements[i];
      if(element.children.length){
        continue;
      }
      var left = element.style.left;
      var top = element.style.top;
      if(topb > pt2r(top) + 5){
        continue;
      }
      if(bottomb < pt2r(top) - 5){
        continue;
      }

      if (coltotal[roundpt(left)]){
       coltotal[roundpt(left)].push(element);
      }else{
       coltotal[roundpt(left)] = [element];
      }
      if (rowtotal[roundpt(left)]){
       rowtotal[roundpt(left)].push(element);
      }else{
       rowtotal[roundpt(left)] = [element];
      }
    }
    for (z in coltotal){
      var absorbed = false;
      for (key in col){
        if (col[key].absorb(coltotal[z])){
          delete coltotal[z];
          absorbed = true;
          break;
        }
      }
      if(!absorbed){
        col[z] = new Column(coltotal[z]);
        delete coltotal[z];
      }
    }
    var col_candidate = [];
    for (z in col){
      col_candidate.push(col[z]);
    }
    col_candidate.sort(function(a,b){
       return (a.left - b.left);
    });
    var rst = col_candidate[idx % col_candidate.length].elements;
    rst.sort(function(a,b){
     return (pt2r(a.style.top) - pt2r(b.style.top))
    });
    return rst;
  }

this.fill = function(ridx,ele){
  var table = document.getElementById("tbody-instance");
  var trs = table.getElementsByTagName("tr");
  for (idx in ele){
    if (idx < trs.length){
      var str = ele[idx].innerHTML.trim();
      str = str.replace(/\t\n/g,"").replace(/&nbsp;/g,"").replace(/\$/g," ");
      str = str.replace(/\s+/g,' ')
      trs[idx].getElementsByTagName("td")[ridx].innerHTML = str;
    }else{
      tr = document.createElement("tr");
      tr.innerHTML = ("<th onclick='this.parentElement.parentElement.removeChild(this.parentElement)' ><i class='fa fa-times'></i></th><td/><td/><td/><td/>");
      table.appendChild(tr);
      var str = ele[idx].innerHTML.trim();
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
  var values = zoyoe.pdftable.pick(ele.count);
  zoyoe.pdftable.fill(cidx,values);
  $('#table-edit').editableTableWidget({
  });
}
