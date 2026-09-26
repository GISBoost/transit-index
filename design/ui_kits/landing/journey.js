(function(){
var NSN='TransitIndexDesignSystem_923c60',SVGNS='http://www.w3.org/2000/svg';
var KEYS_A=['vermilion','orange','yellow'],KEYS_B=['sky','blue'],DEL=[0,0.035,0.07,0.02,0.055];
var triggers=[],tweens=[],entryDone=false,timer=null,lastW=window.innerWidth;
function reduced(){return window.matchMedia('(prefers-reduced-motion: reduce)').matches||!window.gsap||!window.ScrollTrigger;}
function mk(tag,attrs,parent){var e=document.createElementNS(SVGNS,tag);for(var k in attrs)e.setAttribute(k,attrs[k]);if(parent)parent.appendChild(e);return e;}
function build(){
  var NS=window[NSN],svg=document.getElementById('journey');if(!NS||!NS.TransitGeometry||!svg)return;
  var TG=NS.TransitGeometry;
  triggers.forEach(function(t){t.kill();});tweens.forEach(function(t){t.kill();});triggers=[];tweens=[];
  while(svg.firstChild)svg.removeChild(svg.firstChild);
  svg.style.height='0px';
  var W=document.documentElement.clientWidth,H=document.documentElement.scrollHeight;
  svg.setAttribute('viewBox','0 0 '+W+' '+H);svg.style.width=W+'px';svg.style.height=H+'px';
  var edge=document.querySelector('[data-content-edge]'),cr=edge?edge.getBoundingClientRect().right:W*0.6;
  var w=10,g=4,bw=5*w+4*g,cs=cr+56+bw/2,ce=W-40-bw/2,mobile=(ce-cs)<200;
  if(mobile){w=4;g=2;bw=5*w+4*g;}
  var s=w+g,r=bw*1.6,lanes=mobile?{L:14+bw/2,R:14+bw/2}:{L:cs,R:ce};
  var st=[].slice.call(document.querySelectorAll('[data-station]')).map(function(e){var b=e.getBoundingClientRect();return {y:Math.round(b.top+window.scrollY+b.height/2),x:lanes[e.getAttribute('data-lane')||'R'],term:e.hasAttribute('data-terminus')};});
  if(st.length<2)return;
  var root=mk('g',{},svg),nodes=mk('g',{},svg);
  function bundle(parent,main,lineOffs,casingOff,keys){
    var gEl=mk('g',{fill:'none','stroke-linecap':'round','stroke-linejoin':'round'},parent);
    var cas=mk('path',{d:TG.bundle(main,[casingOff],r)[0],'stroke-width':keys.length*w+(keys.length-1)*g+2*g},gEl);cas.style.stroke='var(--paper)';
    var lines=TG.bundle(main,lineOffs,r).map(function(d,j){var p=mk('path',{d:d,'stroke-width':w},gEl);p.style.stroke='var(--line-'+keys[j]+')';return p;});
    return {cas:cas,lines:lines};
  }
  var s0=st[0],ey=Math.max(96,s0.y-r*2.4);
  var entryMain=mobile?[[s0.x,-20],[s0.x,s0.y]]:[[W+bw,ey],[s0.x,ey],[s0.x,s0.y]];
  var eA=bundle(root,entryMain,[2*s,s,0],s,KEYS_A),eB=bundle(root,entryMain,[-s,-2*s],-1.5*s,KEYS_B);
  var segs=[],cA=-s,cB=1.5*s;
  for(var k=0;k<st.length-1;k++){
    var a=st[k],b=st[k+1],h=b.y-a.y,dx=b.x-a.x,adx=Math.abs(dx),mA,mB;
    if(adx<1){mA=[[a.x+cA,a.y],[a.x+cA,b.y]];mB=[[a.x+cB,a.y],[a.x+cB,b.y]];}
    else{
      var yL=a.y+Math.max(r,h*0.2),yF=yL+Math.max(bw*2.2,h*0.18);
      if(yF+adx+r>b.y){yF=b.y-adx-r;yL=Math.min(yL,yF-bw*2.2);if(yL<a.y+r*0.6){yL=yF=a.y+Math.max(r*0.6,(h-adx)/2);}}
      var leadA=dx>0,ya=leadA?yL:yF,yb=leadA?yF:yL;
      mA=[[a.x+cA,a.y],[a.x+cA,ya],[b.x+cA,ya+adx],[b.x+cA,b.y]];
      mB=[[a.x+cB,a.y],[a.x+cB,yb],[b.x+cB,yb+adx],[b.x+cB,b.y]];
    }
    var grp=mk('g',{},root),pA,pB;
    if(k%2===0){pB=bundle(grp,mB,[s/2,-s/2],0,KEYS_B);pA=bundle(grp,mA,[s,0,-s],0,KEYS_A);}
    else{pA=bundle(grp,mA,[s,0,-s],0,KEYS_A);pB=bundle(grp,mB,[s/2,-s/2],0,KEYS_B);}
    segs.push({a:a,b:b,A:pA,B:pB});
  }
  st.forEach(function(p){var hh=w+14,rc=mk('rect',{x:p.x-bw/2-9,y:p.y-hh/2,width:bw+18,height:hh,rx:hh/2,'stroke-width':mobile?2:3},nodes);rc.style.fill=p.term?'var(--ink)':'var(--paper)';rc.style.stroke='var(--ink)';});
  var head=mk('g',{opacity:0},nodes),hc=mk('circle',{r:w*1.15},head),hi=mk('circle',{r:w*0.45},head);hc.style.fill='var(--ink)';hi.style.fill='var(--paper)';
  if(reduced())return;
  var gs=window.gsap,vh=window.innerHeight;
  function prep(p){var L=p.getTotalLength();p.style.strokeDasharray=L+' '+L;p.style.strokeDashoffset=L;p._L=L;return p;}
  if(!entryDone&&window.scrollY<10){
    var tl0=gs.timeline({delay:.25,onComplete:function(){entryDone=true;}});
    [eA,eB].forEach(function(part,bi){prep(part.cas);tl0.to(part.cas,{strokeDashoffset:0,duration:1.6,ease:'power2.inOut'},bi*0.12);part.lines.forEach(function(p,j){prep(p);tl0.to(p,{strokeDashoffset:0,duration:1.6,ease:'power2.inOut'},(bi*3+j)*0.06);});});
    tweens.push(tl0);
  } else entryDone=true;
  segs.forEach(function(sg){
    var tl=gs.timeline({paused:true});
    [sg.A,sg.B].forEach(function(part,bi){var dl=part.lines.map(function(_,j){return DEL[bi*3+j];}),mn=Math.min.apply(null,dl);
      prep(part.cas);tl.to(part.cas,{strokeDashoffset:0,duration:1-mn,ease:'none'},mn);
      part.lines.forEach(function(p,j){prep(p);tl.to(p,{strokeDashoffset:0,duration:1-dl[j],ease:'none'},dl[j]);});});
    var lead=sg.A.lines[1];
    tl.eventCallback('onUpdate',function(){var p=(tl.progress()-DEL[1])/(1-DEL[1]);if(p>0.002&&p<0.998){var pt=lead.getPointAtLength(lead._L*p);head.setAttribute('transform','translate('+pt.x.toFixed(1)+' '+pt.y.toFixed(1)+')');head.setAttribute('opacity','1');}else head.setAttribute('opacity','0');});
    var start=Math.max(0,sg.a.y-vh*0.6),end=Math.max(start+1,sg.b.y-vh*0.6);
    triggers.push(ScrollTrigger.create({start:start,end:end,animation:tl,scrub:0.6}));tweens.push(tl);
  });
}
function schedule(){clearTimeout(timer);timer=setTimeout(function(){build();if(window.ScrollTrigger)ScrollTrigger.refresh();},160);}
window.addEventListener('resize',function(){if(window.innerWidth!==lastW){lastW=window.innerWidth;schedule();}});
window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',schedule);
window.TIJourney={build:build,schedule:schedule};
})();
