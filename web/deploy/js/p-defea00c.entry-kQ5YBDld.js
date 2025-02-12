import{o as R,V as W,m as P,D as a,L as I,T as M}from"./lf-core-C8T4tqs2.js";import{bd as c,be as T,l as F,n as A,bf as j,c as $,C as v,bg as B}from"./theme.constants-7kSb6kn5.js";import{o as O}from"./p-558ec216-rEbCTrf4.js";import"./preload-helper-C1FmrZbK.js";const w=({depth:e,expanded:t=!1,manager:o,node:r,onClickExpand:s,type:n})=>{const{get:p}=o.assets,{bemClass:h}=o.theme;switch(n){case"dropdown":return a("div",{class:h(c.node._,c.node.dropdown,{expanded:t}),"data-cy":v.maskedSvg});case"expand":return a("div",{class:h(c.node._,c.node.expand,{expanded:t}),"data-cy":v.maskedSvg,onClick:s});case"icon":const{style:l}=p(`./assets/svg/${r.icon}.svg`);return a("div",{class:h(c.node._,c.node.icon),"data-cy":v.maskedSvg,style:l});case"padding":return a("div",{class:h(c.node._,c.node.padding),style:{[B.multiplier]:e.toString()}});default:return a("div",{class:h(c.node._,c.node.expand,{hidden:!0})})}},U=e=>{var u,L;const{manager:t}=e,{bemClass:o}=t.theme,{accordionLayout:r,depth:s,elements:n,events:p,expanded:h,node:l,selected:b}=e||{},d=a(w,l.icon?{manager:t,node:l,type:"icon"}:{manager:t,type:"placeholder"});return r?a("div",{class:o(c.node._,null,{expanded:h,selected:b}),"data-cy":v.node,"data-depth":s.toString(),key:l.id,onClick:p.onClickExpand,onPointerDown:p.onPointerDown,part:T.node,title:l.description},a("div",{class:o(c.node._,c.node.content)},n.ripple,d,n.value,a(w,(u=l.children)!=null&&u.length?{expanded:h,manager:t,node:l,type:"dropdown"}:{manager:t,type:"placeholder"}))):a("div",{class:o(c.node._,null,{expanded:h,selected:b}),"data-cy":v.node,"data-depth":s.toString(),key:l.id,onClick:p.onClick,onPointerDown:p.onPointerDown,title:l.description},a("div",{class:"node__content"},n.ripple,a(w,{depth:s,manager:t,type:"padding"}),a(w,(L=l.children)!=null&&L.length?{expanded:h,manager:t,node:l,onClickExpand:p.onClickExpand,type:"expand"}:{manager:t,type:"placeholder"}),d,n.value))};var g,f,y,_,E,S,k,x,m,D,N,C,i=function(e,t,o,r){if(o==="a"&&!r)throw new TypeError("Private accessor was defined without a getter");if(typeof t=="function"?e!==t||!r:!t.has(e))throw new TypeError("Cannot read private member from an object whose class did not declare it");return o==="m"?r:o==="a"?r.call(e):r?r.value:t.get(e)},z=function(e,t,o,r,s){if(typeof t=="function"?e!==t||!0:!t.has(e))throw new TypeError("Cannot write private member to an object whose class did not declare it");return t.set(e,o),o};const V=class{constructor(e){R(this,e),this.lfEvent=W(this,"lf-tree-event"),g.add(this),this.expandedNodes=new Set,this.hiddenNodes=new Set,this.selectedNode=null,this.lfAccordionLayout=!0,this.lfDataset=null,this.lfFilter=!0,this.lfEmpty="Empty data.",this.lfRipple=!0,this.lfSelectable=!0,this.lfStyle="",this.lfUiSize="medium",f.set(this,void 0),y.set(this,c),_.set(this,T),E.set(this,F),S.set(this,A),k.set(this,{}),x.set(this,void 0),m.set(this,"")}onLfEvent(e,t,o){var p;const{effects:r}=i(this,f,"f"),{expansion:s,node:n}=o||{};switch(t){case"click":s&&((p=n.children)!=null&&p.length)?(this.expandedNodes.has(n)?this.expandedNodes.delete(n):this.expandedNodes.add(n),this.expandedNodes=new Set(this.expandedNodes)):n&&(this.selectedNode=n);break;case"pointerdown":this.lfRipple&&r.ripple(e,i(this,k,"f")[n.id])}this.lfEvent.emit({comp:this,eventType:t,id:this.rootElement.id,originalEvent:e,node:n})}async getDebugInfo(){return this.debugInfo}async getProps(){const e=j.map(t=>[t,this[t]]);return Object.fromEntries(e)}async refresh(){P(this)}async unmount(e=0){setTimeout(()=>{this.onLfEvent(new CustomEvent("unmount"),"unmount"),this.rootElement.remove()},e)}connectedCallback(){i(this,f,"f")&&i(this,f,"f").theme.register(this)}async componentWillLoad(){z(this,f,await O(this))}componentDidLoad(){const{info:e}=i(this,f,"f").debug;this.onLfEvent(new CustomEvent("ready"),"ready"),e.update(this,"did-load")}componentWillRender(){const{info:e}=i(this,f,"f").debug;e.update(this,"will-render")}componentDidRender(){const{debug:e}=i(this,f,"f");e.info.update(this,"did-render")}render(){var d;const{bemClass:e,get:t,setLfStyle:o}=i(this,f,"f").theme,{emptyData:r,tree:s}=i(this,y,"f"),{lfDataset:n,lfEmpty:p,lfFilter:h,lfStyle:l}=this,b=!((d=n==null?void 0:n.nodes)!=null&&d.length);return z(this,k,{}),a(I,{key:"5bb40a2e5b1581d155ac1eb971faa123f2b962d5"},l&&a("style",{key:"d077098b7aa8b831fbb764bf7b28cc03e2113fcd",id:i(this,E,"f")},o(this)),a("div",{key:"ee7999fbda1372b236647574777921f106186cde",id:i(this,S,"f")},a("div",{key:"5befccaddf6785110381d505c33376f1e7fdc23f",class:e(s._),part:i(this,_,"f").tree},h&&a("lf-textfield",{key:"fd03282db386ca45f1991a14814af5438ca98d5d",class:e(s._,s.filter),lfStretchX:!0,lfIcon:t.current().variables["--lf-icon-search"],lfLabel:"Search...",lfStyling:"flat","onLf-textfield-event":u=>{this.onLfEvent(u,"lf-event"),u.detail.eventType==="input"&&i(this,g,"m",D).call(this,u)}}),b?a("div",{class:e(r._),part:i(this,_,"f").emptyData},a("div",{class:e(r._,r.text)},p)):i(this,g,"m",N).call(this))))}disconnectedCallback(){var e;(e=i(this,f,"f"))==null||e.theme.unregister(this)}get rootElement(){return M(this)}};f=new WeakMap,y=new WeakMap,_=new WeakMap,E=new WeakMap,S=new WeakMap,k=new WeakMap,x=new WeakMap,m=new WeakMap,g=new WeakSet,D=function(e){const{filter:t}=i(this,f,"f").data.node;clearTimeout(i(this,x,"f")),z(this,x,setTimeout(()=>{var o;if(z(this,m,(o=e.detail.inputValue)==null?void 0:o.toLowerCase(),"f"),i(this,m,"f")){const{ancestorNodes:r,remainingNodes:s}=t(this.lfDataset,{value:i(this,m,"f")},!0);this.hiddenNodes=new Set(s),r&&r.forEach(n=>{this.hiddenNodes.delete(n)})}else this.hiddenNodes=new Set},300))},N=function(){const{bemClass:e}=i(this,f,"f").theme,{noMatches:t}=i(this,y,"f"),o=[],r=this.lfDataset.nodes;for(let s=0;s<r.length;s++){const n=r[s];i(this,g,"m",C).call(this,o,n,0)}return o.length?o:i(this,m,"f")&&a("div",{class:e(t._)},a("div",{class:e(t._,t.icon)}),a("div",{class:e(t._,t.text)},'No matches found for "',a("strong",{class:e(t._,t.filter)},i(this,m,"f")),'".'))},C=function e(t,o,r){var b;const{stringify:s}=i(this,f,"f").data.cell;this.debugInfo.endTime||(this.lfInitialExpansionDepth==null||this.lfInitialExpansionDepth>r)&&this.expandedNodes.add(o);const n=!!i(this,m,"f")||this.expandedNodes.has(o),p=this.hiddenNodes.has(o),h=this.selectedNode===o,l={accordionLayout:this.lfAccordionLayout&&r===0,depth:r,elements:{ripple:a("div",{"data-cy":v.rippleSurface,"data-lf":$.rippleSurface,ref:d=>{d&&this.lfRipple&&(i(this,k,"f")[o.id]=d)}}),value:a("div",{class:"node__value"},s(o.value))},events:{onClick:d=>{this.onLfEvent(d,"click",{node:o})},onClickExpand:d=>{this.onLfEvent(d,"click",{expansion:!0,node:o})},onPointerDown:d=>{this.onLfEvent(d,"pointerdown",{node:o})}},expanded:n,manager:i(this,f,"f"),node:o,selected:h};p||(t.push(a(U,{...l})),n&&((b=o.children)==null||b.map(d=>i(this,g,"m",e).call(this,t,d,r+1))))},V.style=`::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}:host{display:block;font-family:var(--lf-tree-font-family, var(--lf-font-family-primary));font-size:var(--lf-tree-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(
        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)
      )}:host([lf-ui-size=medium]){font-size:calc(
        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)
      )}:host([lf-ui-size=small]){font-size:calc(
        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)
      )}:host([lf-ui-size=xlarge]){font-size:calc(
        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)
      )}:host([lf-ui-size=xsmall]){font-size:calc(
        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)
      )}:host([lf-ui-size=xxlarge]){font-size:calc(
        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)
      )}:host([lf-ui-size=xxsmall]){font-size:calc(
        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)
      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-accordion-layout]) .node[data-depth="0"]{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font-size:1em;height:var(--lf-tree-accordion-node-height, 4em)}:host([lf-accordion-layout]) .node[data-depth="0"] .node__value{font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;font-size:1em}:host([lf-selectable]) .node:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.075);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.175);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.225);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tree{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-bg, var(--lf-color-bg)), 0.275);color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);padding:var(--lf-tree-padding, 0)}.tree__filter{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));border-bottom-left-radius:0;border-bottom-right-radius:0;background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.875);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px);position:sticky;top:0;z-index:1}.node{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;height:var(--lf-tree-node-height, 2em);padding:var(--lftree-node-padding, 0 1em);position:relative}.node__content{width:100%;height:100%;align-items:center;display:flex}.node__dropdown,.node__expand,.node__icon{cursor:pointer;margin:0}.node__dropdown,.node__expand{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);overflow:hidden}.node__dropdown:hover,.node__expand:hover{opacity:0.75}.node__dropdown{-webkit-mask:var(--lf-icon-dropdown);mask:var(--lf-icon-dropdown);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__dropdown--expanded{transform:rotate(180deg)}.node__dropdown--expanded:hover{opacity:0.75}.node__dropdown--hidden{visibility:hidden}.node__expand{-webkit-mask:var(--lf-icon-collapsed);mask:var(--lf-icon-collapsed);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--expanded{-webkit-mask:var(--lf-icon-expanded);mask:var(--lf-icon-expanded);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--hidden{visibility:hidden}.node__icon{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__padding{height:100%;width:calc(1.75em * var(--lf_tree_padding_multiplier))}.node__value{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;margin:0 0 0 0.5em;width:100%}.no-matches{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));align-items:center;box-sizing:border-box;display:flex;justify-content:center;margin:auto;padding:1em;width:100%}.no-matches__icon{-webkit-mask:var(--lf-icon-warning);mask:var(--lf-icon-warning);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin-right:0.375em}.no-matches__text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em}.no-matches__filter{color:var(--lf-primary-color)}.empty-data{width:100%;height:100%;font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:1em;align-items:center;display:flex;justify-content:center;margin:1em 0}`;export{V as lf_tree};
