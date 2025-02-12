import{o as Y,V as K,m as G,D as n,L as J,T as N,k as Q}from"./lf-core-C8T4tqs2.js";import{p as X,C as Z,c as ee,q as te,l as re,r as ae,n as ie,s as se,t as le,u as k}from"./theme.constants-7kSb6kn5.js";import{o as oe}from"./p-558ec216-rEbCTrf4.js";import"./preload-helper-C1FmrZbK.js";const F=(e,a,t)=>{const i={nodes:[]};for(let r=0;r<t.length;r++){const l=t[r],o=String(r).valueOf();i.nodes.push({icon:e===l&&a,id:o,value:`#${o}`})}return i},ne=e=>({...e,defaults:se()}),fe=e=>(a=>({changeView:()=>{const{controller:t,elements:i,handlers:r}=a(),{cyAttributes:l,isOverlay:o,manager:f,parts:h}=t.get,{refs:p}=i,{button:u}=r,{assignRef:c,theme:b}=f,{columns2:g,squareToggle:m}=b.get.icons();return n("lf-button",{"data-cy":l.button,id:k.changeView,lfIcon:m,lfIconOff:g,lfStyling:"icon",lfToggable:!0,lfValue:!o(),"onLf-button-event":u,part:h.changeView,ref:c(p,"changeView"),title:o()?"Click for split screen comparison.":"Click for overlay comparison"})},leftButton:()=>{const{controller:t,elements:i,handlers:r}=a(),{cyAttributes:l,isOverlay:o,manager:f,parts:h}=t.get,{refs:p}=i,{button:u}=r,{assignRef:c,theme:b}=f,g=b.get.icon("imageInPicture"),{"--lf-icon-clear":m}=b.get.current().variables;return n("lf-button",{"data-cy":l.button,id:k.leftButton,lfIcon:m,lfIconOff:g,lfStyling:"icon",lfToggable:!0,"onLf-button-event":u,part:h.leftButton,ref:c(p,"leftButton"),title:o()?"Click to open the left panel.":"Click to close the left panel."})},leftTree:()=>{const{controller:t,elements:i,handlers:r}=a(),{blocks:l,compInstance:o,lfAttributes:f,manager:h,parts:p,shapes:u}=t.get,{refs:c}=i,{tree:b}=r,{assignRef:g,theme:m}=h,{bemClass:z,get:x}=m,{"--lf-icon-success":S}=x.current().variables,T=o;return n("lf-tree",{class:z(l.toolbar._,l.toolbar.panel,{left:!0}),"data-lf":f.fadeIn,id:k.leftTree,lfDataset:F(T.leftShape,S,u()),lfFilter:!1,"onLf-tree-event":b,part:p.leftTree,ref:g(c,"leftTree")})},rightButton:()=>{const{controller:t,elements:i,handlers:r}=a(),{cyAttributes:l,isOverlay:o,manager:f,parts:h}=t.get,{refs:p}=i,{button:u}=r,{assignRef:c,theme:b}=f,g=b.get.icon("imageInPicture"),{"--lf-icon-clear":m}=b.get.current().variables;return n("lf-button",{"data-cy":l.button,id:k.rightButton,lfIcon:m,lfIconOff:g,lfStyling:"icon",lfToggable:!0,"onLf-button-event":u,part:h.rightButton,ref:c(p,"rightButton"),title:o()?"Click to open the right panel.":"Click to close the right panel."})},rightTree:()=>{const{controller:t,elements:i,handlers:r}=a(),{blocks:l,compInstance:o,lfAttributes:f,manager:h,parts:p,shapes:u}=t.get,{refs:c}=i,{tree:b}=r,{assignRef:g,theme:m}=h,{bemClass:z,get:x}=m,{"--lf-icon-success":S}=x.current().variables,T=o;return n("lf-tree",{class:z(l.toolbar._,l.toolbar.panel,{right:!0}),"data-lf":f.fadeIn,id:k.rightTree,lfDataset:F(T.rightShape,S,u()),lfFilter:!1,"onLf-tree-event":b,part:p.rightTree,ref:g(c,"rightTree")})}}))(e),ce=e=>(a=>({button:t=>{const{eventType:i,id:r,valueAsBoolean:l}=t.detail,{set:o}=a().controller,{leftButton:f,changeView:h,rightButton:p}=k;if(i==="click")switch(r){case f:o.leftPanelOpened(l);break;case h:o.splitView(l);break;case p:o.rightPanelOpened(l)}},tree:t=>{const{eventType:i,id:r,node:l}=t.detail,{get:o,set:f}=a().controller,{shapes:h}=o,{leftTree:p,rightTree:u}=k;if(i==="click"){const c=h()[parseInt(l.id)];switch(r){case p:f.leftShape(c);break;case u:f.rightShape(c)}}}}))(e);var v,d,y,C,O,L,P,I,R,_,A,B,j,M,H,$,U,E,s=function(e,a,t,i){if(t==="a"&&!i)throw new TypeError("Private accessor was defined without a getter");if(typeof a=="function"?e!==a||!i:!a.has(e))throw new TypeError("Cannot read private member from an object whose class did not declare it");return t==="m"?i:t==="a"?i.call(e):i?i.value:a.get(e)},q=function(e,a,t,i,r){if(typeof a=="function"?e!==a||!0:!a.has(e))throw new TypeError("Cannot write private member to an object whose class did not declare it");return a.set(e,t),t};const he=class{constructor(e){Y(this,e),this.lfEvent=K(this,"lf-compare-event"),v.add(this),this.isLeftPanelOpened=!1,this.isRightPanelOpened=!1,this.shapes={},this.lfDataset=null,this.lfShape="image",this.lfStyle="",this.lfView="main",d.set(this,void 0),y.set(this,X),C.set(this,Z),O.set(this,ee),L.set(this,te),P.set(this,re),I.set(this,ae),R.set(this,ie),_.set(this,void 0),A.set(this,()=>{var a,t,i;q(this,_,(a={blocks:s(this,y,"f"),compInstance:this,cyAttributes:s(this,C,"f"),isOverlay:()=>s(this,v,"m",M).call(this),lfAttributes:s(this,O,"f"),manager:s(this,d,"f"),parts:s(this,L,"f"),shapes:()=>s(this,v,"m",B).call(this)},t={leftPanelOpened:r=>{this.isLeftPanelOpened=r===void 0?!this.isLeftPanelOpened:r},leftShape:r=>this.leftShape=r,rightPanelOpened:r=>{this.isRightPanelOpened=r===void 0?!this.isRightPanelOpened:r},rightShape:r=>this.rightShape=r,splitView:r=>{this.lfView=r?"split":"main"}},i=()=>s(this,_,"f"),{controller:{get:ne(a),set:t},elements:{jsx:fe(i),refs:{changeView:null,leftButton:null,leftTree:null,rightButton:null,rightTree:null,slider:null}},handlers:ce(i)}))}),E.set(this,a=>{const{target:t}=a;if(t instanceof HTMLInputElement){const i=100-parseInt(t.value);this.rootElement.style.setProperty(s(this,I,"f").overlayWidth,`${i}%`)}})}onLfEvent(e,a){this.lfEvent.emit({comp:this,eventType:a,id:this.rootElement.id,originalEvent:e})}async updateShapes(){const{data:e,debug:a}=s(this,d,"f");try{this.shapes=e.cell.shapes.getAll(this.lfDataset);const t=s(this,v,"m",B).call(this);this.leftShape=t[0],this.rightShape=t[1]}catch(t){a.logs.new(this,"Error updating shapes: "+t,"error")}}async getDebugInfo(){return this.debugInfo}async getProps(){const e=le.map(a=>[a,this[a]]);return Object.fromEntries(e)}async refresh(){G(this)}async unmount(e=0){setTimeout(()=>{this.onLfEvent(new CustomEvent("unmount"),"unmount"),this.rootElement.remove()},e)}connectedCallback(){s(this,d,"f")&&s(this,d,"f").theme.register(this)}async componentWillLoad(){q(this,d,await oe(this)),s(this,A,"f").call(this),this.updateShapes()}componentDidLoad(){const{info:e}=s(this,d,"f").debug;this.onLfEvent(new CustomEvent("ready"),"ready"),e.update(this,"did-load")}componentWillRender(){const{info:e}=s(this,d,"f").debug;e.update(this,"will-render")}componentDidRender(){const{info:e}=s(this,d,"f").debug;e.update(this,"did-render")}render(){const{bemClass:e,setLfStyle:a}=s(this,d,"f").theme,{compare:t}=s(this,y,"f"),{lfStyle:i}=this;return n(J,{key:"b2ea2f15f483765c858cf5069a85320bb6bd2438"},i&&n("style",{key:"7f3ff98bb0504435c2dc91c28ea3847f3cacebe0",id:s(this,P,"f")},a(this)),n("div",{key:"1cbbaaa7641607d9836f236352f9a04e768823b9",id:s(this,R,"f")},n("div",{key:"dc8d45dbd35115d9b0c45b420d5f3546d0730476",class:e(t._),part:s(this,L,"f").compare},s(this,v,"m",H).call(this))))}disconnectedCallback(){var e;(e=s(this,d,"f"))==null||e.theme.unregister(this)}get rootElement(){return N(this)}static get watchers(){return{lfDataset:["updateShapes"],lfShape:["updateShapes"]}}};d=new WeakMap,y=new WeakMap,C=new WeakMap,O=new WeakMap,L=new WeakMap,P=new WeakMap,I=new WeakMap,R=new WeakMap,_=new WeakMap,A=new WeakMap,E=new WeakMap,v=new WeakSet,B=function(){var e;return((e=this.shapes)==null?void 0:e[this.lfShape])||[]},j=function(){var e;return!!((e=this.shapes)!=null&&e[this.lfShape])},M=function(){return this.lfView==="main"},H=function(){const{bemClass:e}=s(this,d,"f").theme,{compare:a}=s(this,y,"f");if(s(this,v,"m",j).call(this)){const t=this.shapes[this.lfShape];if((t==null?void 0:t.length)>1)return n("div",{class:e(a._,a.grid)},s(this,v,"m",U).call(this),s(this,v,"m",$).call(this))}return null},$=function(){const{bemClass:e}=s(this,d,"f").theme,{toolbar:a}=s(this,y,"f"),{changeView:t,leftButton:i,rightButton:r}=s(this,_,"f").elements.jsx;return n("div",{class:e(a._)},i(),t(),r())},U=function(){var W,D;const{data:e,sanitizeProps:a,theme:t}=s(this,d,"f"),{bemClass:i}=t,{view:r}=s(this,y,"f"),{left:l,right:o}=s(this,_,"f").controller.get.defaults,{leftTree:f,rightTree:h}=s(this,_,"f").elements.jsx,{isLeftPanelOpened:p,isRightPanelOpened:u,lfShape:c,lfView:b,leftShape:g,rightShape:m}=this,z=((W=l==null?void 0:l[c])==null?void 0:W.call(l))||[],x=[];for(let w=0;w<z.length;w++)x.push(a(z[w]));const S=((D=o==null?void 0:o[c])==null?void 0:D.call(o))||[],T=[];for(let w=0;w<S.length;w++)T.push(a(S[w]));const V=e.cell.shapes.decorate(c,[g,m],async w=>this.onLfEvent(w,"lf-event"),[...x,...T]);return n(Q,null,n("div",{class:i(r._,null,{[b]:!0})},n("div",{class:i(r._,r.left)},V[0]),p&&f(),u&&h(),s(this,v,"m",M).call(this)&&n("div",{class:i(r._,r.slider),onChange:s(this,E,"f"),onInput:s(this,E,"f")},n("input",{class:i(r._,r.input),"data-cy":s(this,C,"f").input,min:"0",max:"100",type:"range",value:"50"})),n("div",{class:i(r._,r.right)},V[1])))},he.style=`::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-compare-font-family, var(--lf-font-family-primary));font-size:var(--lf-compare-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(
        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)
      )}:host([lf-ui-size=medium]){font-size:calc(
        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)
      )}:host([lf-ui-size=small]){font-size:calc(
        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)
      )}:host([lf-ui-size=xlarge]){font-size:calc(
        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)
      )}:host([lf-ui-size=xsmall]){font-size:calc(
        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)
      )}:host([lf-ui-size=xxlarge]){font-size:calc(
        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)
      )}:host([lf-ui-size=xxsmall]){font-size:calc(
        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)
      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}.compare{width:100%;height:100%}.compare__grid{width:100%;height:100%;display:grid;grid-template-rows:var(--lf-comp-grid-template, 1fr auto);position:relative;user-select:none}.toolbar{border:0;border-style:solid;border-radius:var(--lf-compare-border-radius, var(--lf-ui-border-radius));border-top-left-radius:0;border-top-right-radius:0;background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-sizing:border-box;display:flex;justify-content:var(--lf-compare-toolbar-justify, space-between);padding:var(--lf-compare-toolbar-padding, 0.5em);width:var(--lf-compare-toolbar-width, 100%)}.toolbar__panel{border:0;border-style:solid;border-color:rgba(var(--lf-compare-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-compare-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-compare-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);bottom:0;height:var(--lf-compare-panel-height, auto);max-height:var(--lf-compare-panel-max-height, 50%);overflow:auto;position:absolute;width:var(--lf-compare-panel-width, 50%);z-index:var(--lf-compare-panel-z-index, var(--lf-ui-zindex-portal))}.toolbar__panel--left{left:0}.toolbar__panel--right{right:0}.view{width:100%;height:100%;position:relative}.view--main>:first-child{width:100%;height:100%;position:relative}.view--main>:last-child{width:100%;height:100%;clip-path:inset(0 var(--lf_compare_overlay_width, 50%) 0 0);left:0;overflow:hidden;position:absolute;top:0}.view--main>:last-child:after{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.5);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);content:"";height:100%;pointer-events:none;position:absolute;right:var(--lf_compare_overlay_width, 50%);top:0;width:var(--lf-compare-slider-thickness, 3px)}.view--split{display:grid;grid-template-columns:50% 50%;overflow:hidden}.view__slider{width:100%;height:100%;left:0;position:absolute;top:0;touch-action:pan-y;z-index:2}.view__input{width:100%;height:100%;appearance:none;background:transparent;cursor:grab;margin:0;pointer-events:all;z-index:1}.view__input::-webkit-slider-thumb{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);appearance:none;cursor:ew-resize;height:100%;margin:0;width:10px}.view__input::-moz-slider-thumb{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);appearance:none;cursor:ew-resize;height:100%;margin:0;width:10px}`;export{he as lf_compare};
