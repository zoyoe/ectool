/** Quick html user interface to inspect the clips structure 


    It will require inspect.css to work properly.

    It only shows the standard callback of each clip track, it will not show clip actions at the moment.


    The main usage of this lib is the inspectClip function.

*/

zoyoe.game.clip.prototype.peekHTML = function(){
    var element = this.element();
    return element;
}

zoyoe.game.inspector = function(clip){

  /* initialize all the containers */
  var basic_info = $("#clip-basic");
  var frames_line = $("#clip-frames");
  var action_txt = $("#clip-action");
  var clip_render = $("#clip-preview");
  var object_list = $("#clip-objects");


  var action_code = CodeMirror(document.getElementById("clip-action")
    ,{mode:'javascript'});

  var track_code = CodeMirror(document.getElementById("clip-track")
    ,{mode:'javascript'});


  var curframe_idx = null;
  var curframe_ele =null;
  var curclip = clip;
  var curtrack = null;

  var render_mode = "preview";

  function inspectClip (clip){
    curclip = clip;
    basic_info.html("");
    frames_line.html("");
    clip_render.html("");
    object_list.html("");
    var clo = new Array();
    for (var i = 0;i<curclip.length();i++){
       var frame = curclip.getFrame(i);
       var frame_btn = $("<div></div>").addClass("inspect-frame-basic");
       if(frame.keyframe()){
         frame_btn.addClass("inspect-frame-key");
       }
       frames_line.append(frame_btn);
       if (i==0){
         curframe_ele = frame_btn;
       }
      /* No fun and luck here, this function might be buggy */
       clo[i] = new function(){
          this.ele = frame_btn;
          this.frame = frame;
          this.idx = i;
          var self = this;
          this.cb = function(){
            inspectFrame(self.frame,self.idx);
            curframe_ele.removeClass('inspect-frame-focus');
            self.ele.addClass('inspect-frame-focus');
            curframe_ele = self.ele;
            rendFrame();
          }
       }
       frame_btn.on('click',clo[i].cb);
    }
    frames_line.append($("<div style='clear:both;'></div>"));
    clo[0].cb();
    var b2p = $("#back-to-parent");

    /* clip always has a parent 
       if curclip.parent = curclip , then it is the top element */
    b2p.on('click',function(){
     inspectClip(curclip.getParent());
    });

    /* all clips must have at least 1 frame */
    prepareBasicInfo(curclip)
  }

  function rendFrame(){
    curclip.gotoAndStop(curframe_idx);
    curclip.step();
    clip_render.empty();
    if (render_mode == 'preview'){
      clip_render.append(curclip.element());
    }
    if (render_mode == 'html'){
      clip_render.append(curclip.peekHTML());
    }
  }

  function prepareBasicInfo (){
    basic_info.html("clipname : " + curclip.name());
  }


  function inspectFrame(frame,idx){
    var tracks = frame.getClips();
    curframe = frame;
    curframe_idx = idx;
    object_list.html("");
    var clo = {};
    for (t in tracks){
      var track = tracks[t];
      var libtn = $("<li>" + track.clip.name() + "</li>");
      object_list.append(libtn);
      /* No fun and luck here, this function might be buggy */
      clo[t] = new function(){
          this.track = track;
          var self = this;
          this.cb = function(){
            inspectTrack(self.track);
          }
      }
      libtn.on('click',clo[t].cb);
    }
    object_list.append($("<div style='clear:both;'></div>"));

    action_code.setValue(frame.action.toString());
  }

  function inspectTrack(track){
    curtrack = track;
    inspectClip(track.clip);
    track_code.setValue(track.action.toString());
  }

  inspectClip(curclip);

  this.switchRenderToHtml = function(){
    render_mode = 'html';
    rendFrame();
  }
  this.switchRenderToPreview = function(){
    render_mode = 'preview';
    rendFrame();
  }

}


/* To run the test function we need to make sure it is running under escape.game environement */
function inspectTest(){
   var clip = new zoyoe.game.clip('main stage',$("<div></div>").get(0));
   var inst = getScenario('basic',0);
   inst.initialize(clip);
   zoyoe.inspector = new zoyoe.game.inspector(clip);
}
function onBodyLoad(){
   inspectTest();
}
function switchToHtml(){
   zoyoe.inspector.switchRenderToHtml();
}

function switchToPreview(){
   zoyoe.inspector.switchRenderToPreview();
}
