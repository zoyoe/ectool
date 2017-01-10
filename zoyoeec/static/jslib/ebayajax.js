var zoyoe = document.zoyoe;
if(zoyoe == undefined){
  document.zoyoe = {};
  zoyoe = document.zoyoe
}

zoyoe.ebay = {};
zoyoe.cart = {};
zoyoe.order = {};
zoyoe.image = {};
zoyoe.config = {};
zoyoe.deliver = {};
zoyoe.ajax = {forms:{}};

zoyoe.config.urls = {
  api: "/admin/config/api/",
  info: "/admin/config/info/"
};

zoyoe.config.data = {};
zoyoe.config.formdata = {lock:{},input:{},error:{}};


zoyoe.config.angular = function(app, controller_name){
  app.controller(controller_name, function($scope,config) {
    $scope.data = zoyoe.config.data;
    $scope.alter = function(title, category){
      var attr = $scope.data[category][title];
      config.formdata.input.title = title;
      config.formdata.lock.title = true;
      config.formdata.input.category = attr.category;
      config.formdata.lock.category = true;
      config.formdata.input.datatype = attr.datatype;
      config.formdata.input.content = attr.content;
      config.formdata.input.api = attr.api;
      config.formdata.lock.content = false;
      config.formdata.input.command = "alter";
      zoyoe.config.alter(function(data){
        $scope.data[data.category][data.title].content = data.content;
      });
    }
    $scope.delete = function(title, category){
      var attr = $scope.data[category][title];
      config.formdata.input.title = title;
      config.formdata.lock.title = true;
      config.formdata.input.category = attr.category;
      config.formdata.lock.category = true;
      config.formdata.input.datatype = attr.datatype;
      config.formdata.input.content = attr.content;
      config.formdata.lock.content = true;
      config.formdata.input.command = "delete";
      zoyoe.config.delete(function(data){
        delete $scope.data[attr.category][title];
      });
    }
    $scope.add = function(category,datatype){
      config.formdata.input.title = "";
      config.formdata.lock.title = false;
      config.formdata.input.category = category;
      config.formdata.lock.category = true;
      config.formdata.input.content = "";
      config.formdata.lock.content = false;
      config.formdata.input.datatype = datatype;
      config.formdata.input.command = "add"; 
      zoyoe.config.add(function(data){
        data.datatype = "text"; /* Added info must be text at the moment */
        $scope.data[category][data.title] = data;
      });
    }
  });
}


zoyoe.ajax.result = function(data,cb,attacher){
  var info = JSON.parse(data);
  if(info.reply){/* success */
    cb(info.data);
    zoyoe.ajax.digest();
    zoyoe.ajax.dialog.close();
  }else{
    attacher.error = info.data;
    zoyoe.ajax.digest();
  }
}

zoyoe.ajax.open = function(title,cb,url,formid,attacher){
  var formobj = $(formid);
  if(zoyoe.ajax.forms[formid] == undefined){
    formobj.detach();
    formobj.show();
    zoyoe.ajax.forms[formid] = formobj;
  }
  zoyoe.ajax.formobj = zoyoe.ajax.forms[formid];
  zoyoe.ajax.dialog = new BootstrapDialog({
      title: title,
      message: zoyoe.ajax.formobj,
      buttons: [{
        label: 'Confirm',
        cssClass: 'btn-primary',
        action: function(dialogRef){
          $.ajax({
            type: "POST",
            url: url,
            data: zoyoe.ajax.formobj.serialize(),
          }).done(function(data){
              zoyoe.ajax.result(data, cb, attacher);
          });
        }},{
        label: 'Cancel',
        cssClass: 'btn-warning',
        action: function(dialogRef){
          zoyoe.ajax.dialog.close();
        }
      }]
    });
  zoyoe.ajax.dialog.open();
}

zoyoe.config.preloadform = function(fid){
  if(!this.formid){
    this.formid = fid;
  }
}

/* 
  This should be as general as possible and should know nothing about the underlining forms.
  The forms are supposed to be managed by a angular block.
  fid: formid
  dtitle: dialog title
  cb: callback function
*/

zoyoe.config.delete = function(cb){
  zoyoe.ajax.open("Delete Config",cb,this.urls.api,this.formid,this.formdata);
}

zoyoe.config.alter = function(cb){
  zoyoe.ajax.open("Modify Config",cb,this.urls.api,this.formid,this.formdata);
}

zoyoe.config.add = function(cb){
  zoyoe.ajax.open("Add Config",cb,this.urls.api,this.formid,this.formdata);
}

zoyoe.image.rotate = function(shop,key,idx,cid){
   var url = "/admin/rotateimage/"+shop+"/"+key+"/";
   url = url+idx +"/"
   $.ajax({
      url: url
   }).done(function (data){
      var src = $(cid + ' img').attr('src');
      $(cid + ' img').attr('src', src+"&rand="+Math.random());
   });
 
}

zoyoe.supplier = {data:{},formdata:{lock:{},input:{},error:{}}};
zoyoe.supplier.preloadform = function(fid){
  if(!this.formid){
    this.formid = fid;
  }
}

zoyoe.supplier.urls = {
  api: "/admin/supplier/api/",
  info: "/admin/config/info/"
};
zoyoe.supplier.data = {};
zoyoe.supplier.formdata= {lock:{},input:{},error:{}};
zoyoe.supplier.angular = function(app, controller_name){
  app.controller(controller_name, function($scope,supplier) {
    $scope.data = zoyoe.supplier.data;
    $scope.alter = function(name){
      var attr = $scope.data[name];
      supplier.formdata.input.name = name;
      supplier.formdata.lock.name = true;
      supplier.formdata.input.data = JSON.stringify(attr.data);
      supplier.formdata.lock.data= true;
      supplier.formdata.input.command = "alter";
      supplier.formdata.error = {};
      zoyoe.supplier.alter(function(data){
        $scope.data[name] = data;
      });
    };
    $scope.edit = function(key,data){
      data.edit = data.name;
    }
    $scope.blur = function(key,data){
      data.name = data.edit;
      delete(data.edit);
    }
    $scope.delete = function(name){
      var attr = $scope.data[name];
      supplier.formdata.input.name = name;
      supplier.formdata.lock.name = true;
      supplier.formdata.input.data = JSON.stringify(attr.data);
      supplier.formdata.lock.data= true;
      supplier.formdata.input.command = "delete"; 
      supplier.formdata.error = {};
      zoyoe.supplier.delete(function(data){
        delete(key);
      });
    }
    $scope.addrootcategory = function(supplier){
      var timeStamp = Math.floor(Date.now() / 1000);
      supplier.data["ts" + timeStamp] = {name:"new category", children:{}};
    }

    $scope.addcategory = function(category){
      var timeStamp = Math.floor(Date.now() / 1000);
      if(category.children == undefined){
        category.children= {};
      }
      category.children["ts" + timeStamp] = {name:"new category", children:{}};
    }
    $scope.deletecategory = function(supplier,key){
      function findanddelete(data, key){
        if(data[key]!=undefined){
          delete data[key];
        }else{
          for(nkey in data){
            if(data[nkey].children){
              findanddelete(data[nkey].children,key);
            }
          }
        }
      }
      findanddelete(supplier.data,key);
    }

    $scope.add = function(){
      supplier.formdata.input.name= "";
      supplier.formdata.lock.name= false;
      supplier.formdata.input.command = "add"; 
      supplier.formdata.error = {};
      supplier.formdata.input.data = "{}";
      supplier.formdata.lock.data= true;
      zoyoe.supplier.add(function(data){
        $scope.data[data.name] = data;
      });
    }
  });
};
zoyoe.supplier.alter = function(cb){
  zoyoe.ajax.open("Alter Supplier",cb,this.urls.api,this.formid,this.formdata);
}

zoyoe.supplier.add = function(cb){
  zoyoe.ajax.open("Add Supplier",cb,this.urls.api,this.formid,this.formdata);
}


zoyoe.supplier.delete = function(cb){
  zoyoe.ajax.open("Delete Supplier",cb,this.urls.api,this.formid,this.formdata);
}

zoyoe.order.submit = function(form,table){
   var values = [];
   $(table + " tr").each(function(){
      row = [];
      $(this).find("td").each(function(){
        row.push($(this).text());
      });
      values.push(row);
   });
   $(form + " textarea.zoyoe-table-data").val(JSON.stringify(values));
   $(form).submit();
}

zoyoe.cart.pos = function(cell){
}

zoyoe.cart.paybycredit = function(formid){
  $(formid).submit();
}

zoyoe.cart.save = function(){
   $.ajax({
      url: "/retail/savecart/"
    }).done(function (data){
      $("#content .inner").html(zoyoe.ebay.xml2Str(data));
    });

}

/* FIXME: This is not implemented */
zoyoe.cart.editreceipt = function(cell,key){
   $.ajax({
      url: "/retail/editreceipt/" + key + "/"
    }).done(function (data){
      $("#content .inner").html(zoyoe.ebay.xml2Str(data));
    });
}

zoyoe.cart.checkout = function(key){
   $.ajax({
      url: "/retail/checkout/" + key + "/"
    }).done(function (data){
      if(data.documentElement.tagName == "ZoyoeError"){
        BootstrapDialog.alert({
           title: 'Error',
           message: zoyoe.ebay.xml2Str(data)
        });
      }else{
        $("#content .inner").html(zoyoe.ebay.xml2Str(data));
      }
    });

}

zoyoe.cart.showed = false;
zoyoe.cart.show = function(){
  zoyoe.cart.showed = !zoyoe.cart.showed;
  if (zoyoe.cart.showed){
     $.ajax({
       url: "/retail/get/",
     }).done(function (data){
       if(data.documentElement.tagName == "ZoyoeError"){
         BootstrapDialog.alert({
           title: 'Error',
           message: zoyoe.ebay.xml2Str(data)
         });
       }else{ /* success */
         if($("#cartdisplay")){
           $("#cartdisplay").html(zoyoe.ebay.xml2Str(data));
           $("#cartdisplay").show();
         } 
       }
    });
  }else{
    $("#cartdisplay").hide();
  } 
}
zoyoe.cart.deletereceipt = function(cell,id){
   var ele = cell;
   $.ajax({
      url: "/retail/deletereceipt/"+id+"/"
    }).done(function (data){
      if(data.documentElement.tagName == "ZoyoeSuccess"){
        container = ele.parentElement.parentElement;
        parent = container.parentElement;
        parent.removeChild(container);
      }else{
        BootstrapDialog.alert({
           title: 'Error',
           message: zoyoe.ebay.xml2Str(data)
       });
      }
    });

}

zoyoe.cart.loadreceipt = function(cell,id){
   var ele = cell;
   $.ajax({
      url: "/retail/receipt/"+id+"/"
    }).done(function (data){
       ele.onclick="";
       var p = $("#"+id);
       p.html(zoyoe.ebay.xml2Str(data));
       p.removeClass("collapse");
       $(ele).children('.fa').removeClass("fa-plus");
       $(ele).children('.fa').addClass("fa-minus");
       var display = true;
       $(ele).click(function(){
         if(display){
           $(ele).children('.fa').removeClass("fa-minus");
           $(ele).children('.fa').addClass("fa-plus");
           p.addClass("collapse");
         }else{
           $(ele).children('.fa').removeClass("fa-plus");
           $(ele).children('.fa').addClass("fa-minus");
           p.removeClass("collapse");
         }
         display = !display;
       });
    });
}

/* Adding something to your cart */
/* This is something not safe at the moment, 
   because the value of the item is generated from front-end 
*/
zoyoe.cart.add = function(id,dscp,value){
   $.jGrowl("Adding item to your cart ...",{theme:'growl-warning'});
   $.ajax({
      url: "/retail/add/",
      data: {'id':id,'value':value,'description':dscp}
    }).done(function (data){
      if(data.documentElement.tagName == "ZoyoeError"){
        BootstrapDialog.alert({
          title: 'Error',
          message: zoyoe.ebay.xml2Str(data)
        });
      }else{ /* success */
        if($("#cart-result")){
          $("#cart-result").html(zoyoe.ebay.xml2Str(data));
        } 
        /* This is only for debuging purpose, we will using jGrow instead 
        */
        zoyoe.cart.dialog = new BootstrapDialog({
         title: "<i class='fa fa-shopping-cart'></i>&nbsp;Item added to Shopping cart",
         message: zoyoe.ebay.xml2Str(data),
         buttons: [{
                label: 'Ok',action: function(dialogRef){dialogRef.close();}
            }]
         });
         zoyoe.cart.dialog.open(); 
         $.jGrowl("Item " + id + " added into cart.",{theme:'growl-success',sticky:true});
      }

    });
}
zoyoe.cart.posadd = function(form){
   var itemid = $('#search-item')[0].value;
   $.ajax({
      url: "/retail/add/",
      data: {'id':itemid},
      error:function (xhr, ajaxOptions, thrownError){
        console.log("AJAX Error: " + url + " " + xhr.status);
      }
    }).done(function (data){
      $("#cart-result").html(zoyoe.ebay.xml2Str(data));
    });
}
zoyoe.cart.remove = function(cell,id){
   $.jGrowl("Removing item from cart ...",{theme:'growl-warning'});
   $.ajax({
      url: "/retail/remove/"+id+"/"
    }).done(function (data){
      if(zoyoe.cart.dialog){
        zoyoe.cart.dialog.setMessage(zoyoe.ebay.xml2Str(data));
      }
      if($("#cart-result")){
        $("#cart-result").html(zoyoe.ebay.xml2Str(data));
      }
    });
}

zoyoe.ebay.lock = false;

zoyoe.ebay.result = function(cell,data){
  var ns = "urn:ebay:apis:eBLBaseComponents";
  var ack = data.getElementsByTagNameNS(ns,"Ack");
  if (ack.length == 0){
    $(cell).html("<button type='button' class='btn btn-danger btn-sm'>Error</button>");
    $(cell + " button").click(function(){
       BootstrapDialog.alert({
         title: 'Error',
         message: new XMLSerializer().serializeToString(data)
       });
    });
    return; /* FIXME: early return here, not nice */
  }
  ack = ack[0].textContent;
  if( ack == "Failure"){
    $(cell).html("<button type='button' class='btn btn-danger btn-sm'>Error</button>");
    var errors = data.getElementsByTagNameNS(ns,"Errors")[0];
    var shortmsg = errors.getElementsByTagNameNS(ns,"ShortMessage")[0].textContent;
    var longmsg = errors.getElementsByTagNameNS(ns,"LongMessage")[0].textContent;
    longmsg = longmsg.replace(/</g,"[");
    longmsg = longmsg.replace(/>/g,"]");
    var msg = "<h4>" + shortmsg + "</h4><p>" + longmsg + "</p>";
    var msg = "<h4>" + shortmsg + "</h4><p>" + longmsg + "</p>";
    $(cell + " button").click(function(){
       BootstrapDialog.alert({
         title: 'Error',
         message: msg
       });
    });
  }else{
    if( ack == "Warning"){
      $(cell).html("<button type='button' class='btn btn-success btn-sm'>Warning</button>");
      var errors = data.getElementsByTagNameNS(ns,"Errors")[0];
      var shortmsg = errors.getElementsByTagNameNS(ns,"ShortMessage")[0].textContent;
      var longmsg = errors.getElementsByTagNameNS(ns,"LongMessage")[0].textContent;
      longmsg = longmsg.replace(/</g,"[");
      longmsg = longmsg.replace(/>/g,"]");
      var msg = "<h4>" + shortmsg + "</h4><p>" + longmsg + "</p>";
      var fees = data.getElementsByTagNameNS(ns,"Fees")[0];
      msg += "<ul class='list-group'>";
      for (var a = fees.firstChild;a;a = a.nextSibling){
        var name = a.getElementsByTagNameNS(ns,"Name")[0].textContent;
        var fee = a.getElementsByTagNameNS(ns,"Fee")[0].textContent;
        msg += "<li class='list-group-item'>" + name + ":" + fee + "</li>";
      }
      msg += "</ul>";
      $(cell + " button").click(function(){
         BootstrapDialog.alert({
         title: 'Warning',
         message: msg
         });
      });
    }
    else{
      $(cell).html("<button type='button' class='btn btn-success btn-sm'>Success</button>");
      var fees = data.getElementsByTagNameNS(ns,"Fees")[0];
      var msg = "<ul class='list-group'>";
      for (var a = fees.firstChild;a;a = a.nextSibling){
        var name = a.getElementsByTagNameNS(ns,"Name")[0].textContent;
        var fee = a.getElementsByTagNameNS(ns,"Fee")[0].textContent;
        msg += "<li class='list-group-item'>" + name + ":" + fee + "</li>";
      }
      msg += "</ul>";

      $(cell + " button").click(function(){
        /* Should be successful if no ZoyoeError was returned*/
        BootstrapDialog.alert({
          title: 'Success',
          message: msg
        });
      });
    }
  }
}

zoyoe.ebay.syncToCell = function(shop,id,cell){
   $(cell).html("<button type='button' class='btn btn-primary btn-sm'><i class='fa fa-refresh'></i>loading...</button>");
   $(cell).addClass('loadingbg');
   $.ajax({
      url: "/admin/syncwithebay/"+shop+"/" + id +"/"
     }).done(function (data){
        zoyoe.ebay.result(cell,data);
     });
}

/* EBay Integration
   relistToCell: Relist an zoyoe item to ebay
   calling rest api: admin/relisttoebay/shop/id/
*/
zoyoe.ebay.relistToCell = function(shop,id,cell){
   $(cell).html("<button type='button' class='btn btn-primary btn-sm'><i class='fa fa-refresh'></i>loading...</button>");
   $(cell).addClass('loadingbg');
   $.ajax({
      url: "/admin/relisttoebay/"+shop+"/" + id +"/"
     }).done(function (data){
        zoyoe.ebay.result(cell,data);
     });
}

zoyoe.ebay.saveItem = function(shop,id,table){
  zoyoe.ebay.fitspec($(table));
  document.getElementById('item-info').submit();
}

zoyoe.ebay.exportToCell = function(shop,id,cell){
   $(cell).html("<button type='button' class='btn btn-primary btn-sm'><i class='fa fa-refresh'></i>loading...</button>");
   $(cell).addClass('loadingbg');
   $.ajax({
      url: "/admin/exporttoebay/"+shop+"/" + id +"/"
     }).done(function (data){
        zoyoe.ebay.result(cell,data);
     });

}

zoyoe.ebay.formatCell = function(cell){
   var name = cell.name;
   $('#'+name).html("<button type='button' class='btn btn-primary btn-sm'><i class='fa fa-refresh'></i>loading...</button>");
   $.ajax({
      url: "/format/"+name+"/"
     }).done(function (data){
       var id = "#"+name;
       zoyoe.ebay.result(id,data);
     });
}
zoyoe.ebay.relistCell = function(cell){
   var name = cell.name;
   $('#'+name).html("<button type='button' class='btn btn-primary btn-sm'><i class='fa fa-refresh'></i>loading...</button>");
   $.ajax({
      url: "/relist/"+name+"/"
     }).done(function (data){
       var id = "#"+name;
       zoyoe.ebay.result(id,data);
     });
}

zoyoe.order.testCell = function(cell){
  var path = cell.dataset.path.replace(/\s/g,"-");
  var url = "/json/item/" + path + "/";
  var warning = "";
  $.ajax({
    url: url
  }).done(function (data){
    var value = 10;
    var info = JSON.parse(data);
    var imgurl = info.galleryurl;
    var infourl = info.infourl;
    var img = $("<img style='position:fixed;top:-1000px;left:-1000px;width:1px;height:1px'>"); //Equivalent: $(document.createElement('img'))
    img.appendTo(cell);
    img.load(function(){
        value = value + 20;
        $(cell).progressbar( "option", "value", value );
    });
    img.attr('src',imgurl);
    var href = $("<a>edit</a>");
    href.attr("href",infourl);
    href.appendTo(cell);
    if(info.description && info.description.length > 200){
      value = value + 20;
    }
    if(info.specification.length > 20){
      value = value + 20;
    }
    $(cell).progressbar( "option", "value", value );
  });

}

zoyoe.ebay.xml2Str = function(xmlNode) {
  try {
      // Gecko- and Webkit-based browsers (Firefox, Chrome), Opera.
      return (new XMLSerializer()).serializeToString(xmlNode).trim();
  }
  catch (e) {
     try {
        // Internet Explorer.
        return xmlNode.xml;
     }
     catch (e) {  
        //Other browsers without XML Serializer
        alert('Xmlserializer not supported');
     }
   }
   return false;
}

zoyoe.ebay.fitspec = function(table) {
  var spec = {};
  table.find('tr').each(function(i){
      var th = this.getElementsByTagName("th")[0];
      var td = this.getElementsByTagName("td")[0];
      spec[th.innerHTML] = td.innerHTML;
    });
    document.getElementById("spec-dscp").value = JSON.stringify(spec);
}

zoyoe.ebay.parsespec = function(table,value){
  var spec = {};
  try{ 
      var spec = JSON.parse(value);
  }catch(err){
      zoyoe.error.show("illegale item specification");
  }
  table.find('tr').each(function(i){
      var th = this.getElementsByTagName("th")[0];
      var td = this.getElementsByTagName("td")[0];
      td.innerHTML = spec[th.innerHTML]
    });
    document.getElementById("spec-dscp").value = JSON.stringify(spec);
}

zoyoe.ebay.format = function(){
   zoyoe.ebay.lock = true;
   var inputlist = document.forms["quickinsert"].getElementsByTagName("input");
   for (var i = 0;i<inputlist.length;i++){
     if(inputlist[i].type != "checkbox"){continue;}
     if(inputlist[i].checked == false){continue;}
     this.formatCell(inputlist[i]);
   }
}
zoyoe.ebay.formatall = function(){
   zoyoe.ebay.lock = true;
   var inputlist = document.forms["quickinsert"].getElementsByTagName("input");
   for (var i = 0;i<inputlist.length;i++){
     if(inputlist[i].type != "checkbox"){continue;}
     this.formatCell(inputlist[i]);
   }
}


zoyoe.ebay.relist = function(){
   zoyoe.ebay.lock = true;
   var inputlist = document.forms["quickinsert"].getElementsByTagName("input");
   for (var i = 0;i<inputlist.length;i++){
     if(inputlist[i].type != "checkbox"){continue;}
     if(inputlist[i].checked == false){continue;}
     this.relistCell(inputlist[i]);
   }
}
zoyoe.ebay.relistall = function(){
   zoyoe.ebay.lock = true;
   var inputlist = document.forms["quickinsert"].getElementsByTagName("input");
   for (var i = 0;i<inputlist.length;i++){
     if(inputlist[i].type != "checkbox"){continue;}
     this.relistCell(inputlist[i]);
   }
}

/* following functions are not used at the moment */
zoyoe.item = function (iid, centre_top, centre_left, radius) {
    this.centre_top = centre_top;
    this.centre_left = centre_left;
    this.radius = radius;
    this.rid = iid;
    this.display = false;
    this.dirty = false;
    this.path = function (ctx) {
        ctx.arc(this.centre_left, this.centre_top, this.radius, 0, 2 * Math.PI);
    }
    this.contains = function (top, left) {
        return (Math.sqrt((top - this.centre_top) * (top - this.centre_top) + (left - this.centre_left) * (left - this.centre_left)) < this.radius);
    }
    this.paint = function (ctx) {
        if (this.display) {
            ctx.fillStyle = "rgba(255,255,255,0.2)";
            ctx.beginPath();
            ctx.arc(this.centre_left, this.centre_top, this.radius, 0, 2 * Math.PI);
            ctx.rect(ctx.canvas.width, 0, -1 * ctx.canvas.width, ctx.canvas.height);
            ctx.fill();
        }
        this.dirty = false;
    }
    this.show = function () {
        if (!this.display) {
            this.display = true;
            this.dirty = true;
        }
        return this.dirty;
    }
    this.hide = function () {
        if (this.display) {
            this.display = false;
            this.dirty = true;
        }
        return this.dirty;
    }
}

zoyoe.gallery = function (gal, picker) {
    var gal = gal;
    var picker = picker;
    var ctx = $(gal + ' canvas').get(0).getContext('2d');
    this.ctx = ctx;
    this.resize = function(){
      var height = $(gal + " img").height();
      var width = $(gal + " img").width();
      $(gal + " canvas").height(height).width(width);
      this.ctx.canvas.width = width;
      this.ctx.canvas.height = height;
    }
    this.resize();
    this.items = [];
    this.focus = null;
    this.freeze = false;
    this.dirty = true;
    this.addItem = function (iid, centre_top, centre_left, radius) {
        this.items.push(new zoyoe.item(iid, centre_top, centre_left, radius));
    }
    var self = this;
    $(picker + " span.pick-save").click(function () {
        self.saveitem();
    });
    this.hover = function (top, left) {
        if (this.freeze) {
            return;
        }
        var selected = null;
        for (item in this.items) {
            if (!this.items[item].contains(top, left)) {
                this.dirty = this.dirty || this.items[item].hide(this.ctx);
            }
        }
        for (item in this.items) {
            if (this.items[item].contains(top, left)) {
                this.dirty = this.dirty || this.items[item].show(this.ctx);
                selected = this.items[item];
                break; /* So far we only allow 1 item to be selected */
            }
        }

        this.paint();
        /* Not used at the moment
        if (!selected && this.dirty) {
            this.ctx.fillStyle = "rgba(255,255,255,0.1)";
            this.ctx.beginPath();
            for (item in this.items) {
                this.items[item].path(this.ctx);
            }
            this.clean();

            this.ctx.rect(this.ctx.canvas.width, 0, -1 * this.ctx.canvas.width, this.ctx.canvas.height);
            this.ctx.fill();
            this.dirty = false;
        }
        */
        return selected;
    }
    this.paint = function () {
        if (this.dirty) {
            this.clean();
            for (item in this.items) {
                this.items[item].paint(this.ctx);
            }
            this.dirty = false;
        }
    }
    this.clean = function () {
        var ctx = this.ctx;
        ctx.clearRect(ctx.canvas.width, 0, -1 * ctx.canvas.width, ctx.canvas.height);
    }
    this.click = function (top, left) {
        this.melt();
        var select = this.hover(top, left);
        if (select) {
            this.focus = select;
            this.freeze = true;
            $(picker + " .pick-refid").val(select.rid);
            $(picker + " .pick-radius").val(select.radius);
            $(picker + " .pick-left").val(select.centre_left);
            $(picker + " .pick-top").val(select.centre_top);
        } else {
            this.focus = null;
            this.freeze = false;
            this.hover();
        }
    }
    this.saveitem = function () {
        if (this.focus) {
            this.focus.rid = $(picker + " .pick-refid").val();
            this.focus.radius = $(picker + " .pick-radius").val();
            this.focus.centre_left = $(picker + " .pick-left").val();
            this.focus.centre_top = $(picker + " .pick-top").val();
            this.dirty = true;
            this.paint();
        }
    }
    this.melt = function () {
        this.freeze = false;
        this.dirty = true;
    }
}
