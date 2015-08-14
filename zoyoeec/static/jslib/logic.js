/* A resuable frame based logic kernel that controls how we rendering all the objects */

/** The data structure is simple :

   Clip
   => [*][][][][*]    <=============     list of Frames while [] are noopFarmes and [*] are key frames

   frame
   => <clip1><clip2><clip3>   <=====     list of ClipProx. We use notation <> to specifiy a clipProx. For example <clipA> means a prox of clipA 

   Frame rate is usually 20 frames per second.

   The idea is simple if you are familiar Adobe flash. 

*/



var zoyoe = document.zoyoe;
if(zoyoe == undefined){
  zoyoe = {};
}
zoyoe.game = {};
zoyoe.game.MOTION = new function(){
  this.NULL = 0;
  this.TRANSLATION = 1;
};
zoyoe.game.PAUSE = 1;
zoyoe.game.RUN = 0;

function n2px(n){
  return n+"px";
}
function px2n(px){
  parseInt(px);
}

zoyoe.game.noopFrame = function(parent,idx){
    var index = idx;
    var clip = parent;
    var iskeyframe = false;
    var clips = {};
    var status = zoyoe.game.RUN;
    this.tracked = function(c){
      if(clips[c.name()]){
        return true;
      }else{
        return false;
      }
    }
    this.getTrack = function(name){
      return clips[name];
    }
    this.getIndex = function(){
        return index;
    };
    this.getClips = function(){
        return clips;
    };
    this.trackClip = function(clip){
        if(clips[clip.name()]!=undefined){
          return clips[clip.name()];
        }else{
          clips[clip.name()] = new zoyoe.game.clipprox(clip);
          iskeyframe = true;
          return clips[clip.name()];
        }
    };
    this.untrackClip = function(clip){
       if(clips[clip.clip.name()] == clip){
          delete clips[clip.clip.name()];
       }else{
          throw "Clip Not Found"
       }
    }
    this.keyframe = function (){
        return iskeyframe;
    };
    this.setKeyframe = function(b){
        iskeyframe = b;
    };
    this.clips = function(){
        return clips;
    }
    this.action = function(cb){
        return;
    }
    this.render = function(){
        if(iskeyframe){
          for(c in clips){
             var track = clips[c];
             track.clip.position(clips[c].top,clips[c].left);
             /* Since action might delete him self, so should preform action last */
             track.action();
          }
        }else{
        var pk = clip.getPreKey(index);
        var nk = clip.getNextKey(index);
        if(pk && nk){
            var pcs = pk.clips();
            var ncs = nk.clips();
            for (var key in pcs){
              var pc = pcs[key];
              var nc = ncs[key];
              if(nc){
                switch(pc.motion){
                case zoyoe.game.MOTION.TRANSLATION:
                  var lambda = (this.getIndex()-pk.getIndex())/(nk.getIndex()-pk.getIndex());
                  var top = pc.top*(1-lambda) + nc.top*lambda;
                  var left = pc.left*(1-lambda) + nc.left*lambda;
                  pc.clip.position(top,left);
                break;
                }
              }
            }
          }
        }
    /* It is not implemented well */
    };
};
zoyoe.game.clip = function (n,ele,top,left){

  /* ( relative_top , relative_left ) is the coordinates of the top-left point
      of the element of this clip */

  var relative_top = 0;
  var relative_left = 0;
  var center_top = 0;
  var center_left = 0;
  var element = ele;
  var clips = [];
  var frames = [new zoyoe.game.noopFrame(this,0)];
  var idx = 0;
  var name = n;
  var status = zoyoe.game.RUN;
  ele.id = n;
  var parent = this;
  var zidxlock = false;
  var stay = false;
  if(!isNaN(top)){
    relative_top = top;
  }
  if(!isNaN(left)){
    relative_left = left;
  }
  this.center = function(top,left){
    center_top = top;
    center_left = left;
  }
  this.centerTop = function(){
    return center_top;
  }
  this.centerLeft = function(){
    return center_left;
  }
  this.zidxLock = function(idx){
    zidxlock = true;
    element.style.zIndex = idx;
  }
  this.zidx = function(idx){
    if(!zidxlock){
      element.style.zIndex = idx;
    }
  }
  this.getParent = function(){
    return parent;
  }
  this.setParent = function(clip){
    parent = clip;
  }
  this.reset = function(){
    element.innerHTML = "";
    clips = [];
    frames = [new zoyoe.game.noopFrame(this,0)];
    idx = 0;
    status = zoyoe.game.RUN;
  }
  this.clips = function(){
      return clips;
  };
  this.element = function(){
    return element;
  }

  /* return the previous key frame */
  this.getPreKey = function(idx){
      for(var i = idx;0<=i;i--){
          if(frames[i].keyframe()){
              return frames[i];
          }
      };
      return null;
  };

  /* return the next key frame */
  this.getNextKey = function(idx){
      for(var i = idx+1;i<frames.length;i++){
          if(frames[i].keyframe()){
              return frames[i];
          }
      };
      return null;
  };

  /* return the top-left position of this clip */
  this.position = function(top,left){
      if((!isNaN(top))&&(!isNaN(left))){
          relative_top = top;
          relative_left = left;
      }
      return {top:relative_top,left:relative_left};
  };
  this.render = function(){
    var top = 0;
    var left = 0;
    var p = this;
    var current = this;
    do{
      current = p;
      top += p.top() + p.centerTop();
      left += p.left() + p.centerLeft();
      p = p.getParent();
    }while(current != p);
    element.style.top = n2px(top); 
    element.style.left = n2px(left); 
  };
  this.inc = function(){
      if(stay){
        stay = false;
        return;
      }
      idx = idx+1;
      if(idx == frames.length){
          idx = 0;
      }
  };
  this.setCallBack = function(frame_idx,callback){
      if(frame_idx<frames.length){
          throw "frame idx overflow";
      }else{
          this.frames[frame_idx.callbac = callback];
      }
  };
  this.step = function(){
    var display = element.style.display;
    element.style.display = "none";
    var frame = frames[idx];
    frame.render(this);
    var keyframe = this.getPreKey(idx);
    for(var c in clips){
      if(keyframe.tracked(clips[c])){
     clips[c].step();
        if(clips[c].element().parentNode == element){
          /* don know what to do here */
        }else{
          element.appendChild(clips[c].element());
        } 
      }else{
        try {
          element.removeChild(clips[c].element());
        }catch(exception) {
          /* pass silently here */
        }
      }
    }
    frame.action();
    this.render();
    if(status == zoyoe.game.RUN){
      this.inc();
    }else{
    }
    element.style.display = display;
  };
  this.play = function(){
    status = zoyoe.game.RUN;
  };
  this.stop = function(){
    status = zoyoe.game.PAUSE;
  };
  this.gotoAndStop = function(frame_number){
    idx = frame_number;
    status = zoyoe.game.PAUSE;
    return;
  };
  this.gotoAndPlay = function(frame_number){
    idx = frame_number;
    stay = true;
    status = zoyoe.game.RUN;
    /* not implemented */
  };
  this.insertClip = function(clip){
      this.clips().push(clip);
      clip.setParent(this);
  };
  this.name = function(){
    return name;
  };
  this.trackClip = function(keyframe,clip){
    return keyframe.trackClip(clip);
  };
  this.appendFrames = function(n){
    var start = frames.length;
    for(var i=0;i<n;i++){
      frames.push(new zoyoe.game.noopFrame(this,start+i));
    }
    return start;
  };
  this.getFrame = function(n){
    return frames[n];
  }
  this.length = function(){
    return frames.length;
  }
  this.top = function(){
    return relative_top;
  }
  this.left = function(){
    return relative_left;
  }
}

zoyoe.game.clipprox = function(clip){
    this.clip = clip;
    this.top = clip.top();
    this.left = clip.left();
    this.motion = zoyoe.game.MOTION.NULL;
    this.action = function(){
      return;
    }
}

zoyoe.game.newName = function(){
  if(!zoyoe.ninc){
    zoyoe.ninc = 0;
  }
  var name = "zoyoe_name_gen_"+zoyoe.ninc;
  zoyoe.ninc ++;
  return name;
}
 
zoyoe.game.env = function(ele,fps,top,left,inst){
  var delaywindow = 1000/fps;
  var status = zoyoe.game.PAUSE;
  var topclip = new zoyoe.game.clip('root',ele,top,left);
  var topele = ele;
  var self = this;
  var timer = null;
  var instance = inst;
  this.onMouseClick = function(top,left){
      if(status == zoyoe.game.RUN){
        inst.onMouseClick(top,left);
      };
  }
  this.step = function(force){
      if(status == zoyoe.game.RUN || force){
        topclip.step();
      }
  };
  this.root = function(){
      return topclip;
  };
  this.reset = function(){
      window.clearTimeout(timer);
      status = zoyoe.game.PAUSE;
      topclip.reset();
  };
  this.pause = function(){
    status = zoyoe.game.PAUSE
  }
  this.run = function(){
    status = zoyoe.game.RUN;
    this.step();
    timer = window.setTimeout(function(){
      if(status == zoyoe.game.RUN){
          self.run();
      }else{
          return;
      }        
    },delaywindow);    
  }
};
