import{o as k,V as w,D as r,m as z,L as _,T as x}from"./lf-core-C8T4tqs2.js";import{b9 as T,C,c as S,ba as E,l as I,bb as L,n as W,bc as M}from"./theme.constants-7kSb6kn5.js";import{o as A}from"./p-558ec216-rEbCTrf4.js";import"./preload-helper-C1FmrZbK.js";var e,d,u,m,v,p,g,y,h,o=function(t,a,i,s){if(typeof a=="function"?t!==a||!0:!a.has(t))throw new TypeError("Cannot read private member from an object whose class did not declare it");return a.get(t)};const R=class{constructor(t){k(this,t),this.lfEvent=w(this,"lf-toast-event"),this.lfCloseIcon="",this.lfCloseCallback=()=>{this.unmount()},this.lfTimer=null,this.lfMessage="",this.lfStyle="",this.lfUiSize="medium",this.lfUiState="primary",e.set(this,void 0),d.set(this,T),u.set(this,C),m.set(this,S),v.set(this,E),p.set(this,I),g.set(this,L),y.set(this,W),h.set(this,(a=!1)=>{const{assets:i,theme:s}=o(this,e),{get:l}=i,{bemClass:n}=s,{toast:f}=o(this,d),{style:b}=l(`./assets/svg/${a?this.lfCloseIcon:this.lfIcon}.svg`);return r("div",{class:n(f._,f.icon,{"has-actions":a}),"data-cy":o(this,u).maskedSvg,onPointerDown:a?c=>this.lfCloseCallback(this,c):null,part:o(this,v).icon,style:b,tabIndex:a&&0})})}onLfEvent(t,a){this.lfEvent.emit({comp:this,eventType:a,id:this.rootElement.id,originalEvent:t})}async getDebugInfo(){return this.debugInfo}async getProps(){const t=M.map(a=>[a,this[a]]);return Object.fromEntries(t)}async refresh(){z(this)}async unmount(t=0){setTimeout(()=>{this.onLfEvent(new CustomEvent("unmount"),"unmount"),this.rootElement.remove()},t)}connectedCallback(){o(this,e)&&o(this,e).theme.register(this)}async componentWillLoad(){if(function(t,a,i,s,l){if(typeof a=="function"?t!==a||!0:!a.has(t))throw new TypeError("Cannot write private member to an object whose class did not declare it");a.set(t,i)}(this,e,await A(this)),this.lfCloseIcon===""){const{"--lf-icon-delete":t}=o(this,e).theme.get.current().variables;this.lfCloseIcon=t}}componentDidLoad(){const{info:t}=o(this,e).debug;this.onLfEvent(new CustomEvent("ready"),"ready"),t.update(this,"did-load")}componentWillRender(){const{info:t}=o(this,e).debug;t.update(this,"will-render")}componentDidRender(){const{info:t}=o(this,e).debug,{lfTimer:a}=this;a&&setTimeout(()=>{this.lfCloseCallback?this.lfCloseCallback(this,null):this.unmount()},a),t.update(this,"did-render")}render(){const{theme:t}=o(this,e),{bemClass:a,setLfStyle:i}=t,{toast:s}=o(this,d),{lfCloseIcon:l,lfIcon:n,lfMessage:f,lfStyle:b,lfTimer:c}=this;return r(_,{key:"316c535819de4d0069553d13546a1f265d6324d3"},r("style",{key:"a60526ef82abf64a499bebd7dc0f27ccb79258b7",id:o(this,p)},`
          :host {
            ${c?`--${o(this,g).timer}: ${c}ms;`:""}
          }
        ${b&&i(this)||""}`),r("div",{key:"0bb339c3762a0cabec2a2970508faa35264e5fb8",id:o(this,y),"data-lf":o(this,m).fadeIn},r("div",{key:"ff4ed6998d5be73afbee6fa3d72659ca18ea024d",class:a(s._),"data-lf":o(this,m)[this.lfUiState]},r("div",{key:"0692bba3e047c9a5defdd7feb089f82b9ba0c8e0",class:a(s._,s.accent,{temporary:!!c})}),r("div",{key:"287303638535fe6070ba9d17d4247d97816a9f5b",class:a(s._,s.messageWrapper,{full:!!n&&!!l,"has-actions":!!l,"has-icon":!!n})},n&&o(this,h).call(this),f&&r("div",{key:"fcb2dbae067fdfc54d8379a0c32102750f008a2c",class:a(s._,s.message)},f),l&&o(this,h).call(this,!0)))))}disconnectedCallback(){var t;(t=o(this,e))==null||t.theme.unregister(this)}get rootElement(){return x(this)}};e=new WeakMap,d=new WeakMap,u=new WeakMap,m=new WeakMap,v=new WeakMap,p=new WeakMap,g=new WeakMap,y=new WeakMap,h=new WeakMap,R.style=`::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=danger]{--lf-toast-color-primary:var(
    --lf-toast-color-danger,
    var(--lf-color-danger)
  );--lf-toast-color-on-primary:var(
    --lf-toast-color-danger,
    var(--lf-color-on-danger)
  )}[data-lf=disabled]{opacity:var(--lf-toast-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-toast-color-primary:var(
    --lf-toast-color-info,
    var(--lf-color-info)
  );--lf-toast-color-on-primary:var(
    --lf-toast-color-info,
    var(--lf-color-on-info)
  )}[data-lf=secondary]{--lf-toast-color-primary:var(
    --lf-toast-color-secondary,
    var(--lf-color-secondary)
  );--lf-toast-color-on-primary:var(
    --lf-toast-color-secondary,
    var(--lf-color-on-secondary)
  )}[data-lf=success]{--lf-toast-color-primary:var(
    --lf-toast-color-success,
    var(--lf-color-success)
  );--lf-toast-color-on-primary:var(
    --lf-toast-color-success,
    var(--lf-color-on-success)
  )}[data-lf=warning]{--lf-toast-color-primary:var(
    --lf-toast-color-warning,
    var(--lf-color-warning)
  );--lf-toast-color-on-primary:var(
    --lf-toast-color-warning,
    var(--lf-color-on-warning)
  )}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-toast-font-family, var(--lf-font-family-primary));font-size:var(--lf-toast-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(
        var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)
      )}:host([lf-ui-size=medium]){font-size:calc(
        var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)
      )}:host([lf-ui-size=small]){font-size:calc(
        var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)
      )}:host([lf-ui-size=xlarge]){font-size:calc(
        var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)
      )}:host([lf-ui-size=xsmall]){font-size:calc(
        var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)
      )}:host([lf-ui-size=xxlarge]){font-size:calc(
        var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)
      )}:host([lf-ui-size=xxsmall]){font-size:calc(
        var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)
      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%;animation:slideIn 250ms ease-out;box-sizing:border-box;z-index:var(--lf-ui-zindex-toast, 998)}.toast{border:0;border-style:solid;border-radius:var(--lf-toast-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-toast-color-surface, var(--lf-color-surface)), 0.675);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);width:100%;height:100%;box-shadow:var(--lf-ui-box-shadow-modal);display:grid;grid-template-rows:auto 1fr;overflow:hidden}.toast__accent{background-color:rgba(var(--lf-toast-color-primary, var(--lf-color-primary)), 0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);height:var(--lf-toast-accent-height, 0.25em);width:100%}.toast__accent--temporary{animation:reduceWidthToZero linear var(--lf_toast_timer, 5000ms) forwards}.toast__message-wrapper{align-content:var(--lf-toast-message-align-content, center);box-sizing:border-box;display:grid;gap:1em;grid-template-columns:1fr;height:100%;overflow:auto;padding:var(--lf-toast-padding, 0.75em)}.toast__message-wrapper--has-icon{grid-template-columns:auto 1fr}.toast__message-wrapper--has-actions{grid-template-columns:1fr auto}.toast__message-wrapper--full{grid-template-columns:auto 1fr auto}.toast__icon{background-color:rgba(var(--lf-comp-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin:var(--lf-toast-icon-margin, auto 0.5em);opacity:var(--lf-toast-icon-opacity, 1)}.toast__icon--has-actions{-webkit-mask:var(--lf-icon-clear);mask:var(--lf-icon-clear);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-toast-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);cursor:pointer;margin:auto 0.5em auto auto;position:relative}.toast__icon--has-actions:hover{opacity:0.75}.toast__message{color:rgb(var(--lf-toast-color-on-bg, var(--lf-color-on-bg)));overflow:auto;padding:var(--lf-toast-message-padding, 0.75em 0.75em 0.75em 0)}@media only screen and (max-width: 600px){:host{animation:slideUp 250ms ease-out}}@keyframes reduceWidthToZero{0%{width:100%}100%{width:0}}@keyframes slideIn{0%{transform:var(--lf-toast-slidein-from, translateX(100%))}100%{transform:var(--lf-toast-slidein-to, translateX(0))}}@keyframes slideUp{0%{transform:var(--lf-toast-slideup-from, translateY(100%))}100%{transform:var(--lf-toast-slideup-to, translateY(0))}}`;export{R as lf_toast};
