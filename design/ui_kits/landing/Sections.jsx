const TI=window.TransitIndexDesignSystem_923c60;
const fmt=(v,lang,d=1)=>Number(v).toLocaleString(lang==='en'?'en-GB':'pl-PL',{minimumFractionDigits:d,maximumFractionDigits:d});
function Kicker({children,bullet,line='vermilion',lane='R',terminus}){
  const {LineBullet}=TI;
  return <div className="kicker" data-station="" data-lane={lane} data-terminus={terminus?'':undefined}>{bullet&&<LineBullet label={bullet} line={line} size="sm"/>}<span>{children}</span></div>;
}
function Header({t,lang,setLang,night,setNight}){
  const {Logo,IconButton,Button}=TI;
  return <header className="hdr"><div className="hdr-in">
    <a href="#top" style={{textDecoration:'none'}}><Logo size={30}/></a>
    <nav className="hdr-nav">{t.nav.map(([h,l])=><a key={h} href={h}>{l}</a>)}</nav>
    <div style={{display:'flex',gap:4,alignItems:'center'}}>
      {['pl','en'].map(l=><Button key={l} size="sm" variant={lang===l?'primary':'ghost'} onClick={()=>setLang(l)} style={{padding:'0 10px'}}>{l.toUpperCase()}</Button>)}
      <IconButton icon={night?'light_mode':'dark_mode'} label={night?t.day:t.night} onClick={()=>setNight(!night)}/>
    </div></div></header>;
}
function Hero({t,lang}){
  const {Stat,Button}=TI; const h=t.hero;
  return <section id="top" className="sec hero"><div className="col" data-content-edge="">
    <div className="kicker">{h.kicker}</div>
    <h1 className="h1">{h.title}</h1>
    <p className="lead">{h.lead}</p>
    <div data-station="" data-lane="R" style={{position:'relative',marginTop:40,paddingRight:120}}>
      <Stat size="xl" value={h.value} unit="km/h" label={h.label} misregister/>
      <div className="stamp" aria-hidden="true"><span>{h.stamp[0]}</span><b>{h.stamp[1]}</b><span>{h.stamp[2]}</span></div>
    </div>
    <div style={{display:'flex',gap:10,flexWrap:'wrap',marginTop:36}}><a href="#ranking"><Button variant="accent" iconRight="south">{h.cta1}</Button></a><a href="#mapa"><Button variant="secondary" iconRight="map">{h.cta2}</Button></a></div>
  </div></section>;
}
function StretchStrip({n,lang}){
  const cls=v=>v<10?1:v<14?2:v<18?3:v<22?4:5;
  return <div style={{overflowX:'auto',margin:'36px 0 0'}}><div style={{minWidth:560,display:'grid',gridTemplateColumns:'repeat('+n.speeds.length+',1fr)',position:'relative',paddingBottom:30}}>
    {n.speeds.map((v,i)=><div key={i} style={{position:'relative',paddingTop:26}}>
      <div style={{fontFamily:'var(--font-condensed)',fontWeight:700,fontSize:15,fontVariantNumeric:'tabular-nums',position:'absolute',top:0,left:'50%',transform:'translateX(-50%)',whiteSpace:'nowrap'}}>{fmt(v,lang)} km/h</div>
      <div style={{height:10,background:'var(--speed-'+cls(v)+')'}}></div>
      <span className="stop" style={{left:-8}}></span>{i===n.speeds.length-1&&<span className="stop" style={{right:-8}}></span>}
      <div className="stopname" style={{left:0}}>{n.stops[i]}</div>{i===n.speeds.length-1&&<div className="stopname" style={{right:0,transform:'translateX(50%)'}}>{n.stops[i+1]}</div>}
    </div>)}
  </div></div>;
}
function NumberSec({t,lang}){
  const {Stat}=TI; const n=t.num;
  return <section className="sec"><div className="col">
    <Kicker bullet="02" line="orange" lane="L">{n.kicker}</Kicker>
    <div style={{marginTop:28}}><Stat size="lg" value={n.value}/></div>
    <h2 className="h2">{n.title}</h2>
    <p className="lead">{n.body}</p>
    <StretchStrip n={n} lang={lang}/>
    <div className="kpis">{n.kpis.map(([v,l])=><Stat key={l} size="md" value={v} label={l}/>)}</div>
  </div></section>;
}
function Ranking({t,lang}){
  const {RankingBar,Button}=TI; const r=t.rank; const ref=React.useRef(null);
  React.useEffect(()=>{const bars=ref.current.querySelectorAll('[data-bar]');if(window.matchMedia('(prefers-reduced-motion: reduce)').matches||!window.gsap)return;
    const tw=gsap.fromTo(bars,{scaleX:0},{scaleX:1,duration:.9,ease:'power3.out',stagger:.05,scrollTrigger:{trigger:ref.current,start:'top 72%',once:true}});return ()=>tw.scrollTrigger&&tw.scrollTrigger.kill();},[]);
  return <section id="ranking" className="sec"><div className="col">
    <Kicker bullet="03" line="yellow" lane="R">{r.kicker}</Kicker>
    <h2 className="h2">{r.title}</h2><p className="small">{r.note}</p>
    <div ref={ref} style={{marginTop:24,borderTop:'2px solid var(--ink)'}}>{window.TI_CITIES.map((c,i)=><RankingBar key={c.pl} rank={i+1} label={c[lang]} value={c.v} max={22} locale={lang} flag={c.flag} flagLabel={c.flag?r[c.flag]:undefined} highlight={c.hl}/>)}</div>
    <div style={{marginTop:20}}><Button variant="ghost" iconRight="download">{r.more}</Button></div>
  </div></section>;
}
const ROUTES=[{pts:[[20,300],[180,300],[260,220],[260,30]],cls:[4,3,'t3',2,1]},{pts:[[40,80],[200,80],[300,180],[580,180]],cls:[5,4,4,3,'n',3]},{pts:[[120,370],[120,270],[220,170],[420,170],[510,80],[590,80]],cls:[2,1,'n',2,3,4,5]},{pts:[[340,370],[340,270],[440,270],[530,360]],cls:[3,'t2',2,1]}];
function MapTeaser(){
  const ref=React.useRef(null); const [geo,setGeo]=React.useState(null); const TG=TI.TransitGeometry;
  const ds=React.useMemo(()=>ROUTES.map(r=>TG.path(r.pts,30)),[]);
  React.useLayoutEffect(()=>{const ps=[...ref.current.querySelectorAll('[data-route]')];setGeo(ps.map((p,i)=>{const L=p.getTotalLength(),n=ROUTES[i].cls.length,cuts=[...Array(n+1)].map((_,k)=>L*k/n);return {L,cuts,stops:cuts.map(c=>{const q=p.getPointAtLength(c);return [q.x,q.y];})};}));},[]);
  const dash=(g,k,thin)=>{const a=g.cuts[k],b=g.cuts[k+1];const arr=[0,a];if(thin){let x=0;while(x<b-a){const d=Math.min(6,b-a-x);arr.push(d,4);x+=10;}arr[arr.length-1]=g.L*2;}else arr.push(b-a,g.L*2);return arr.join(' ');};
  return <svg ref={ref} viewBox="0 0 600 380" style={{display:'block',width:'100%',height:'auto',background:'var(--map-base)'}} role="img" aria-label="Schematic speed map preview">
    {[60,140,220,300].map(y=><line key={'h'+y} x1="0" x2="600" y1={y+20} y2={y+20} strokeWidth="6" style={{stroke:'var(--map-street)'}}/>)}
    {[90,300,470].map(x=><line key={'v'+x} y1="0" y2="380" x1={x} x2={x} strokeWidth="6" style={{stroke:'var(--map-street)'}}/>)}
    {ROUTES.map((r,i)=><g key={i} fill="none" strokeLinecap="butt">
      <path data-route="" d={ds[i]} strokeWidth="12" strokeLinecap="round" style={{stroke:'var(--map-base)'}}/>
      {geo&&r.cls.map((c,k)=>{const nd=c==='n',thin=typeof c==='string'&&c[0]==='t';const col=nd?'var(--speed-nodata)':'var(--speed-'+(thin?c.slice(1):c)+')';return <path key={k} d={ds[i]} strokeWidth="6" strokeDasharray={dash(geo[i],k,thin)} style={{stroke:col}}/>;})}
      {geo&&geo[i].stops.map(([x,y],k)=><circle key={k} cx={x} cy={y} r="3.4" strokeWidth="1.6" style={{fill:'var(--map-base)',stroke:'var(--ink)'}}/>)}
    </g>)}
  </svg>;
}
function MapSec({t}){
  const {SpeedLegend,Button}=TI; const m=t.map,l=m.legend;
  return <section id="mapa" className="sec"><div className="col">
    <Kicker bullet="04" line="sky" lane="L">{m.kicker}</Kicker>
    <h2 className="h2">{m.title}</h2><p className="lead">{m.body}</p>
    <div style={{marginTop:28,border:'2px solid var(--ink)'}}><MapTeaser/><div style={{background:'var(--map-base)',borderTop:'2px solid var(--ink)',padding:16}}><SpeedLegend title={l.title} slowLabel={l.slow} fastLabel={l.fast} noDataLabel={l.nd} thinLabel={l.thin}/></div></div>
    <div style={{marginTop:20}}><Button iconRight="open_in_full">{m.cta}</Button></div>
  </div></section>;
}
function Limits({t}){
  const {LineBullet,Button}=TI; const x=t.lim;
  return <section id="ograniczenia" className="sec"><div className="col">
    <Kicker bullet="05" line="blue" lane="R">{x.kicker}</Kicker>
    <h2 className="h2">{x.title}</h2>
    <div className="limits">{x.items.map(([h,d],i)=><div key={i} style={{borderTop:'2px solid var(--ink)',paddingTop:14,display:'flex',gap:12}}><LineBullet label={i+1} line="black" size="sm"/><div><b style={{fontSize:18,letterSpacing:'-0.01em'}}>{h}</b><p className="small" style={{margin:'6px 0 0'}}>{d}</p></div></div>)}</div>
    <div style={{display:'flex',gap:10,flexWrap:'wrap',marginTop:28}}>{x.links.map(([l,ic])=><Button key={l} variant="secondary" iconLeft={ic}>{l}</Button>)}</div>
  </div></section>;
}
function Footer({t}){
  const {Logo}=TI; const f=t.foot;
  const Col=({h,items})=><div><div className="kicker" style={{marginBottom:10}}>{h}</div>{items.map(i=><div key={i} style={{fontSize:15,lineHeight:1.9}}><a href="#top" style={{textDecorationThickness:1}}>{i}</a></div>)}</div>;
  return <footer className="sec foot"><div className="col">
    <Kicker lane="L" terminus>{f.kicker}</Kicker>
    <div className="foot-cols"><Col h={f.ed} items={f.eds}/><Col h={f.dl} items={f.dls}/><Col h={f.about} items={f.abouts}/></div>
    <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-end',gap:16,flexWrap:'wrap',marginTop:56,paddingTop:20,borderTop:'2px solid var(--ink)'}}><Logo size={28} credit/><span className="small" style={{color:'var(--ink-3)'}}>{f.note}</span></div>
  </div></footer>;
}
Object.assign(window,{Header,Hero,NumberSec,Ranking,MapSec,Limits,Footer});
