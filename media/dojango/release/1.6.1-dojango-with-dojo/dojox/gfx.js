/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.gfx"]){
dojo._hasResource["dojox.gfx"]=true;
dojo.provide("dojox.gfx");
dojo.require("dojox.gfx.matrix");
dojo.require("dojox.gfx._base");
dojo.loadInit(function(){
var _1=dojo.getObject("dojox.gfx",true),sl,_2,_3;
while(!_1.renderer){
if(dojo.config.forceGfxRenderer){
dojox.gfx.renderer=dojo.config.forceGfxRenderer;
break;
}
var _4=(typeof dojo.config.gfxRenderer=="string"?dojo.config.gfxRenderer:"svg,vml,canvas,silverlight").split(",");
for(var i=0;i<_4.length;++i){
switch(_4[i]){
case "svg":
if("SVGAngle" in dojo.global){
dojox.gfx.renderer="svg";
}
break;
case "vml":
if(dojo.isIE){
dojox.gfx.renderer="vml";
}
break;
case "silverlight":
try{
if(dojo.isIE){
sl=new ActiveXObject("AgControl.AgControl");
if(sl&&sl.IsVersionSupported("1.0")){
_2=true;
}
}else{
if(navigator.plugins["Silverlight Plug-In"]){
_2=true;
}
}
}
catch(e){
_2=false;
}
finally{
sl=null;
}
if(_2){
dojox.gfx.renderer="silverlight";
}
break;
case "canvas":
if(dojo.global.CanvasRenderingContext2D){
dojox.gfx.renderer="canvas";
}
break;
}
if(_1.renderer){
break;
}
}
break;
}
if(dojo.config.isDebug){
console.log("gfx renderer = "+_1.renderer);
}
if(_1[_1.renderer]){
_1.switchTo(_1.renderer);
}else{
_1.loadAndSwitch=_1.renderer;
dojo["require"]("dojox.gfx."+_1.renderer);
}
});
}
