import{o as I,V as $,m as P,D as c,L as R,T as V}from"./lf-core-C8T4tqs2.js";import{aH as F,C as D,c as j,aI as O,l as U,aJ as G,n as H,aK as Y,aL as M}from"./theme.constants-7kSb6kn5.js";import{o as B}from"./p-558ec216-rEbCTrf4.js";import"./preload-helper-C1FmrZbK.js";var n,r,d,b,L,v,S,g,x,f,C,W,T,A,y,e=function(i,t,s,a){if(s==="a"&&!a)throw new TypeError("Private accessor was defined without a getter");if(typeof t=="function"?i!==t||!a:!t.has(i))throw new TypeError("Cannot read private member from an object whose class did not declare it");return s==="m"?a:s==="a"?a.call(i):a?a.value:t.get(i)},E=function(i,t,s,a,o){if(typeof t=="function"?i!==t||!0:!t.has(i))throw new TypeError("Cannot write private member to an object whose class did not declare it");return t.set(i,s),s};const X=class{constructor(i){I(this,i),this.lfEvent=$(this,"lf-image-event"),n.add(this),this.error=!1,this.isLoaded=!1,this.lfHtmlAttributes={},this.lfShowSpinner=!1,this.lfSizeX="100%",this.lfSizeY="100%",this.lfStyle="",this.lfUiState="primary",this.lfValue="",r.set(this,void 0),d.set(this,F),b.set(this,D),L.set(this,j),v.set(this,O),S.set(this,U),g.set(this,G),x.set(this,H),f.set(this,void 0),y.set(this,t=>{const{assets:s}=e(this,r,"f"),{mask:a}=s.get(`./assets/svg/${t}.svg`).style;E(this,f,a)})}onLfEvent(i,t){this.lfEvent.emit({comp:this,id:this.rootElement.id,originalEvent:i,eventType:t})}async resetState(){this.error=!1,this.isLoaded=!1}async getDebugInfo(){return this.debugInfo}async getProps(){const i=Y.map(t=>[t,this[t]]);return Object.fromEntries(i)}async refresh(){P(this)}async unmount(i=0){setTimeout(()=>{this.onLfEvent(new CustomEvent("unmount"),"unmount"),this.rootElement.remove()},i)}connectedCallback(){e(this,r,"f")&&e(this,r,"f").theme.register(this)}async componentWillLoad(){E(this,r,await B(this));const{logs:i}=e(this,r,"f").debug;if(!e(this,n,"m",T).call(this)&&this.lfValue)try{await e(this,n,"m",A).call(this,this.lfValue),this.isLoaded=!0}catch{i.new(this,"Failed to preload icon","warning"),this.error=!0}}componentDidLoad(){const{info:i}=e(this,r,"f").debug;this.onLfEvent(new CustomEvent("ready"),"ready"),i.update(this,"did-load")}componentWillRender(){const{info:i}=e(this,r,"f").debug;i.update(this,"will-render")}componentDidRender(){const{info:i}=e(this,r,"f").debug;i.update(this,"did-render")}render(){const{debug:i,theme:t}=e(this,r,"f"),{bemClass:s,get:a}=t,{variables:o}=a.current(),{image:w}=e(this,d,"f"),{error:u,isLoaded:h,lfSizeX:z,lfSizeY:k,lfStyle:_,lfValue:l}=this;if(!l)return void i.logs.new(this,"Empty image.");E(this,f,"");const p=e(this,n,"m",T).call(this);if(u){const{"--lf-icon-broken-image":m}=o;e(this,y,"f").call(this,m)}else if(!p){const m=l.indexOf(M)>-1?o[l]:l;e(this,y,"f").call(this,m)}return c(R,null,c("style",{id:e(this,S,"f")},`
          :host {
            ${e(this,g,"f").mask}: ${e(this,f,"f")?e(this,f,"f"):"none"};
            ${e(this,g,"f").height}: ${k||"100%"};
            ${e(this,g,"f").width}:  ${z||"100%"};
          }
          ${_&&t.setLfStyle(this)||""}`),c("div",{id:e(this,x,"f")},c("div",{class:s(w._,null),"data-lf":e(this,L,"f").fadeIn,onClick:m=>{this.onLfEvent(m,"click")},part:e(this,v,"f").image},u?e(this,n,"m",C).call(this):p?e(this,n,"m",W).call(this):h?e(this,n,"m",C).call(this):null)))}disconnectedCallback(){var i;(i=e(this,r,"f"))==null||i.theme.unregister(this)}get rootElement(){return V(this)}static get watchers(){return{lfValue:["resetState"]}}};r=new WeakMap,d=new WeakMap,b=new WeakMap,L=new WeakMap,v=new WeakMap,S=new WeakMap,g=new WeakMap,x=new WeakMap,f=new WeakMap,y=new WeakMap,n=new WeakSet,C=function(){const{sanitizeProps:i,theme:t}=e(this,r,"f"),{bemClass:s}=t,{image:a}=e(this,d,"f");return c("div",{...i(this.lfHtmlAttributes),class:s(a._,a.icon),"data-cy":e(this,b,"f").maskedSvg,"data-lf":this.lfUiState,part:e(this,v,"f").icon})},W=function(){const{sanitizeProps:i,theme:t}=e(this,r,"f"),{bemClass:s}=t,{image:a}=e(this,d,"f");return c("img",{...i(this.lfHtmlAttributes),class:s(a._,a.img),"data-cy":e(this,b,"f").image,onError:o=>{this.error=!0,this.isLoaded=!1,this.onLfEvent(o,"error")},onLoad:o=>{this.error=!1,this.isLoaded=!0,this.onLfEvent(o,"load")},part:e(this,v,"f").img,src:this.lfValue})},T=function(){const{lfValue:i}=this;return!(!i||typeof i!="string")&&/^(https?:\/\/|\/|\.{1,2}\/|[a-zA-Z]:\\|\\\\).+/.test(i)},A=async function(i){const{assets:t,theme:s}=e(this,r,"f"),{variables:a}=s.get.current(),{"--lf-icon-broken-image":o}=a,w=i.indexOf(M)>-1,u=t.get(`./assets/svg/${this.error?o:w?a[i]:i}.svg`),h=new Image,z=new URL(u.path,window.location.origin).href,k=new Promise((_,l)=>{h.onload=()=>_(),h.onerror=p=>l(p)});h.src=z,await k},X.style=`::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=danger]{--lf-image-color-primary:var(
    --lf-image-color-danger,
    var(--lf-color-danger)
  );--lf-image-color-on-primary:var(
    --lf-image-color-danger,
    var(--lf-color-on-danger)
  )}[data-lf=disabled]{opacity:var(--lf-image-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-image-color-primary:var(
    --lf-image-color-info,
    var(--lf-color-info)
  );--lf-image-color-on-primary:var(
    --lf-image-color-info,
    var(--lf-color-on-info)
  )}[data-lf=secondary]{--lf-image-color-primary:var(
    --lf-image-color-secondary,
    var(--lf-color-secondary)
  );--lf-image-color-on-primary:var(
    --lf-image-color-secondary,
    var(--lf-color-on-secondary)
  )}[data-lf=success]{--lf-image-color-primary:var(
    --lf-image-color-success,
    var(--lf-color-success)
  );--lf-image-color-on-primary:var(
    --lf-image-color-success,
    var(--lf-color-on-success)
  )}[data-lf=warning]{--lf-image-color-primary:var(
    --lf-image-color-warning,
    var(--lf-color-warning)
  );--lf-image-color-on-primary:var(
    --lf-image-color-warning,
    var(--lf-color-on-warning)
  )}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-image-font-family, var(--lf-font-family-primary));font-size:var(--lf-image-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(
        var(--lf-image-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)
      )}:host([lf-ui-size=medium]){font-size:calc(
        var(--lf-image-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)
      )}:host([lf-ui-size=small]){font-size:calc(
        var(--lf-image-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)
      )}:host([lf-ui-size=xlarge]){font-size:calc(
        var(--lf-image-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)
      )}:host([lf-ui-size=xsmall]){font-size:calc(
        var(--lf-image-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)
      )}:host([lf-ui-size=xxlarge]){font-size:calc(
        var(--lf-image-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)
      )}:host([lf-ui-size=xxsmall]){font-size:calc(
        var(--lf-image-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)
      )}#lf-component{width:100%;height:100%}:host,#lf-component,.image{height:var(--lf_image_height, 0);position:relative;width:var(--lf_image_width, 0)}.image__icon,.image__img{height:var(--lf_image_height, 0);margin:var(--lf-image-margin, auto);width:var(--lf_image_width, 0)}.image__icon{transition:all 150ms cubic-bezier(0.42, 0, 0.58, 1);background-color:rgba(var(--lf-image-color-primary, var(--lf-color-primary)), 0.775);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);aspect-ratio:var(--lf-comp-aspect-ratio, 1);mask:var(--lf_image_mask);-webkit-mask:var(--lf_image_mask)}.image__img{display:block;object-fit:var(--lf-image-object-fit, cover)}`;export{X as lf_image};
