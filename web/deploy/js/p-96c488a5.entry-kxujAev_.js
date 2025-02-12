import{o as y,V as z,m as w,D as n,L as k,T as E}from"./lf-core-C8T4tqs2.js";import{aj as L,c as x,ak as _,l as P,n as S,al as T}from"./theme.constants-7kSb6kn5.js";import{o as D}from"./p-558ec216-rEbCTrf4.js";import"./preload-helper-C1FmrZbK.js";var r,c,d,i,g,b,o=function(e,a,t,l){if(typeof a=="function"?e!==a||!0:!a.has(e))throw new TypeError("Cannot read private member from an object whose class did not declare it");return a.get(e)};const C=class{constructor(e){y(this,e),this.lfEvent=z(this,"lf-badge-event"),this.lfImageProps=null,this.lfLabel="",this.lfPosition="top-left",this.lfStyle="",this.lfUiSize="medium",this.lfUiState="primary",r.set(this,void 0),c.set(this,L),d.set(this,x),i.set(this,_),g.set(this,P),b.set(this,S)}onLfEvent(e,a){this.lfEvent.emit({comp:this,eventType:a,id:this.rootElement.id,originalEvent:e})}async getDebugInfo(){return this.debugInfo}async getProps(){const e=T.map(a=>[a,this[a]]);return Object.fromEntries(e)}async refresh(){w(this)}async unmount(e=0){setTimeout(()=>{this.onLfEvent(new CustomEvent("unmount"),"unmount"),this.rootElement.remove()},e)}connectedCallback(){o(this,r)&&o(this,r).theme.register(this)}async componentWillLoad(){(function(e,a,t,l,s){if(typeof a=="function"?e!==a||!0:!a.has(e))throw new TypeError("Cannot write private member to an object whose class did not declare it");a.set(e,t)})(this,r,await D(this))}componentDidLoad(){const{info:e}=o(this,r).debug;this.onLfEvent(new CustomEvent("ready"),"ready"),e.update(this,"did-load")}componentWillRender(){const{info:e}=o(this,r).debug;e.update(this,"will-render")}componentDidRender(){const{info:e}=o(this,r).debug;e.update(this,"did-render")}render(){const{sanitizeProps:e,theme:a}=o(this,r),{bemClass:t,setLfStyle:l}=a,{lfImageProps:s,lfLabel:v,lfStyle:p}=this,[m,h]=this.lfPosition.split("-"),{badge:f}=o(this,c);return n(k,{key:"12975a3c55775f4f5dc6afa342b9b84c935fd245"},n("style",{key:"8efabcaac9994c9cff13f3859621f9416b7bdc7c",id:o(this,g)},`
          :host {
          ${m||"top"}: 0;
          ${h||"left"}: 0;
          transform: translate(
          ${h==="right"?"50%":"-50%"},
          ${m==="bottom"?"50%":"-50%"}
          );
          }
          ${p&&l(this)||""}`),n("div",{key:"759d08a6a3217b8fceb884d98cea0f817976a743",id:o(this,b)},n("div",{key:"c018ee5c4c1cc2870eb643cde88c7a0a7f006767",class:t(f._),"data-lf":o(this,d)[this.lfUiState],onClick:u=>this.onLfEvent(u,"click"),part:o(this,i).badge},v||s&&n("lf-image",{key:"e5d517e29ca7e1e46a567f661b233e7f4cd03a3c",class:t(f._,f.image),part:o(this,i).image,...e(s,"LfImage")})||null)))}disconnectedCallback(){var e;(e=o(this,r))==null||e.theme.unregister(this)}get rootElement(){return E(this)}};r=new WeakMap,c=new WeakMap,d=new WeakMap,i=new WeakMap,g=new WeakMap,b=new WeakMap,C.style=`::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=danger]{--lf-badge-color-primary:var(
    --lf-badge-color-danger,
    var(--lf-color-danger)
  );--lf-badge-color-on-primary:var(
    --lf-badge-color-danger,
    var(--lf-color-on-danger)
  )}[data-lf=disabled]{opacity:var(--lf-badge-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-badge-color-primary:var(
    --lf-badge-color-info,
    var(--lf-color-info)
  );--lf-badge-color-on-primary:var(
    --lf-badge-color-info,
    var(--lf-color-on-info)
  )}[data-lf=secondary]{--lf-badge-color-primary:var(
    --lf-badge-color-secondary,
    var(--lf-color-secondary)
  );--lf-badge-color-on-primary:var(
    --lf-badge-color-secondary,
    var(--lf-color-on-secondary)
  )}[data-lf=success]{--lf-badge-color-primary:var(
    --lf-badge-color-success,
    var(--lf-color-success)
  );--lf-badge-color-on-primary:var(
    --lf-badge-color-success,
    var(--lf-color-on-success)
  )}[data-lf=warning]{--lf-badge-color-primary:var(
    --lf-badge-color-warning,
    var(--lf-color-warning)
  );--lf-badge-color-on-primary:var(
    --lf-badge-color-warning,
    var(--lf-color-on-warning)
  )}:host{display:block;font-family:var(--lf-badge-font-family, var(--lf-font-family-primary));font-size:var(--lf-badge-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(
        var(--lf-badge-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)
      )}:host([lf-ui-size=medium]){font-size:calc(
        var(--lf-badge-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)
      )}:host([lf-ui-size=small]){font-size:calc(
        var(--lf-badge-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)
      )}:host([lf-ui-size=xlarge]){font-size:calc(
        var(--lf-badge-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)
      )}:host([lf-ui-size=xsmall]){font-size:calc(
        var(--lf-badge-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)
      )}:host([lf-ui-size=xxlarge]){font-size:calc(
        var(--lf-badge-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)
      )}:host([lf-ui-size=xxsmall]){font-size:calc(
        var(--lf-badge-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)
      )}#lf-component{width:100%;height:100%}:host{position:absolute}.badge{background-color:rgba(var(--lf-badge-color-primary, var(--lf-color-primary)), 1);color:rgb(var(--lf-badge-color-on-primary, var(--lf-color-on-primary)));overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;border-radius:var(--lf-badge-border-radius, 50%);height:var(--lf-badge-height, 1.5em);padding:var(--lf-badge-padding, 0.25em);place-content:var(--lf-comp-place-content, center);text-align:center;width:var(--lf-badge-width, 1.5em)}.badge__image{--lf-image-color-primary:var(
    --lf-badge-color-on-primary,
    var(--lf-color-on-primary)
  );left:50%;position:absolute;top:50%;transform:translate(-50%, -50%)}`;export{C as lf_badge};
