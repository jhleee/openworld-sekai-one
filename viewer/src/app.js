'use strict';
const dataset=JSON.parse(document.getElementById('wiki-data').textContent),pages=dataset.pages,byId=new Map(pages.map(p=>[p.record,p]));
const categories={Guide:'세계 안내',Rule:'세계 규칙',Place:'지역·장소',Organization:'단체·조직',Character:'영웅·인물',Power:'권능',Spirit:'정령',SacredBeast:'영물',Monster:'몬스터',Item:'유니크 아이템',Event:'역사·사건',Claim:'주장·소문',Thread:'열린 갈등',Culture:'생활·문화',Fact:'확정 상태',Belief:'인물의 믿음'};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=id=>'#page/'+encodeURIComponent(id);let headingIndex=0,toc=[];
function inline(text){
 const tokens=[];const token=html=>'\u0000'+(tokens.push(html)-1)+'\u0000';
 text=text.replace(/`([^`]+)`/g,(_,x)=>token('<code>'+esc(x)+'</code>'));
 text=text.replace(/\[([^\]]+)\]\(([^\s)]+)\)/g,(_,label,target)=>{
  const bare=target.split('#')[0].split('/').pop(),id=bare.replace(/\.md$/,'');
  return token(byId.has(id)?'<a href="'+link(id)+'">'+esc(label)+'</a>':esc(label));
 });
 text=esc(text).replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
 return text.replace(/\u0000(\d+)\u0000/g,(_,n)=>tokens[Number(n)]||'');
}
function markdown(text){
 headingIndex=0;toc=[];const lines=text.split('\n'),out=[];let para=[],list=null,code=null;
 const flush=()=>{if(para.length){out.push('<p>'+inline(para.join(' '))+'</p>');para=[]}if(list){out.push('</'+list+'>');list=null}};
 for(let i=0;i<lines.length;i++){
  const line=lines[i];if(line.startsWith('```')){flush();if(code!==null){out.push('<pre><code>'+esc(code.join('\n'))+'</code></pre>');code=null}else code=[];continue}if(code!==null){code.push(line);continue}
  const h=line.match(/^(#{1,6})\s+(.+)$/);if(h){flush();if(h[1].length===1)continue;const level=Math.min(3,h[1].length),id='section-'+headingIndex++;toc.push({id,text:h[2],level});out.push('<h'+level+' id="'+id+'">'+inline(h[2])+'</h'+level+'>');continue}
  if(line.includes('|')&&i+1<lines.length&&/^\s*\|?\s*:?-+/.test(lines[i+1])){flush();const cells=s=>s.trim().replace(/^\||\|$/g,'').split('|').map(x=>x.trim());out.push('<table><thead><tr>'+cells(line).map(x=>'<th>'+inline(x)+'</th>').join('')+'</tr></thead><tbody>');i+=2;while(i<lines.length&&lines[i].includes('|')){out.push('<tr>'+cells(lines[i]).map(x=>'<td>'+inline(x)+'</td>').join('')+'</tr>');i++}i--;out.push('</tbody></table>');continue}
  const item=line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)$/);if(item){if(para.length){out.push('<p>'+inline(para.join(' '))+'</p>');para=[]}const type=/^\s*\d+\./.test(line)?'ol':'ul';if(list!==type){if(list)out.push('</'+list+'>');out.push('<'+type+'>');list=type}out.push('<li>'+inline(item[1])+'</li>');continue}
  if(!line.trim()){flush();continue}if(/^---+$/.test(line)){flush();out.push('<hr>');continue}if(list){out.push('</'+list+'>');list=null}para.push(line.trim());
 }flush();if(code!==null)out.push('<pre>'+esc(code.join('\n'))+'</pre>');return out.join('\n');
}
function read(key,fallback){try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}}function save(key,value){try{localStorage.setItem(key,JSON.stringify(value))}catch{}}
let recent=read('arken-recent',[]);if(!Array.isArray(recent))recent=[];document.body.classList.toggle('dark',read('arken-dark',false));
const main=document.getElementById('main'),rail=document.getElementById('rail');
function tiles(items){return '<div class="grid">'+items.map(p=>'<a class="tile" href="'+link(p.record)+'"><strong>'+esc(p.name)+'</strong><p>'+esc(p.data?.summary||categories[p.category])+'</p></a>').join('')+'</div>'}
function sidebar(){document.getElementById('categories').innerHTML=Object.entries(categories).filter(([k])=>k!=='Guide'&&pages.some(p=>p.category===k)).map(([k,n])=>'<a href="#category/'+k+'">'+n+'<span class="count">'+pages.filter(p=>p.category===k).length+'</span></a>').join('');document.getElementById('recent').innerHTML=recent.filter(id=>byId.has(id)).slice(0,6).map(id=>'<a href="'+link(id)+'">'+esc(byId.get(id).name)+'</a>').join('')}
function home(){
 main.innerHTML='<div class="eyebrow">THE WORLD OF ARKEN · OFFLINE EDITION</div><h1>아르켄 위키</h1><p class="lead">부서진 하늘 아래의 일곱 맹약</p><div class="hero"><strong>한 세계, 수많은 선택.</strong><p>맹약력 312년 초여름. 마법은 기술이고, 가호는 약속이며, 권능은 책임입니다.</p><p>영웅의 전설부터 뱃사공의 생계까지, 서로 연결된 세계를 읽어보세요.</p></div><div class="stats"><span><b>'+dataset.articles+'</b>세계관 문서</span><span><b>'+Object.keys(categories).filter(k=>k!=='Guide'&&pages.some(p=>p.category===k)).length+'</b>분류</span><span><b>312</b>현재 맹약력</span></div><h2>처음 오셨나요?</h2>'+tiles(['overview','SYS-MAGIC','SYS-BLESSING','SYS-AUTHORITY'].map(id=>byId.get(id)))+'<h2>인물과 그들의 선택</h2>'+tiles(['HERO-SERIN','NPC-TOMA','NPC-SURI','NPC-VARKA'].map(id=>byId.get(id)))+'<h2>세계 둘러보기</h2>'+tiles(['LOC-HUSH','LOC-ESTEL','MON-WORM','ITM-LANTERN'].map(id=>byId.get(id)));
 rail.innerHTML='<div class="panel"><h3>이 위키에 대하여</h3><p>이 파일 하나에 모든 문서가 담겨 있습니다. 인터넷 연결 없이 검색하고 링크를 따라갈 수 있습니다.</p><a href="#page/constitution">세계의 원칙과 창작 경계 →</a></div><div class="panel"><h3>분류 바로가기</h3>'+Object.entries(categories).filter(([k])=>k!=='Guide'&&pages.some(p=>p.category===k)).map(([k,n])=>'<a href="#category/'+k+'">'+n+'</a>').join('')+'</div>';
}
function article(id){const p=byId.get(id);if(!p){main.innerHTML='<h1>문서를 찾을 수 없습니다</h1><a href="#home">대문으로 돌아가기</a>';rail.innerHTML='';return}
 recent=[id,...recent.filter(x=>x!==id)].slice(0,8);save('arken-recent',recent);const body=markdown(p.body),headings=toc.slice();
 main.innerHTML='<div class="eyebrow">ARKEN / '+esc(categories[p.category]||p.category)+'</div><h1>'+esc(p.name)+'</h1><div>'+p.tags.map(t=>'<a class="tag" href="#search/'+encodeURIComponent(t)+'">'+esc(t)+'</a>').join('')+'</div><div class="actions"><a href="#category/'+encodeURIComponent(p.category)+'">같은 분류 보기</a><button class="outline" id="download-md">Markdown 저장 ↓</button></div><article class="body">'+body+'</article>'+(p.data?'<details><summary>근거 기록 보기 · '+esc(id)+'</summary><pre>'+esc(JSON.stringify(p.data,null,2))+'</pre></details>':'');
 const related=pages.filter(x=>x.record!==id&&x.references.includes(id));
 rail.innerHTML='<div class="panel"><h3>목차</h3>'+headings.map(h=>'<a class="'+(h.level===3?'toc-sub':'')+'" href="#page/'+encodeURIComponent(id)+'/'+h.id+'">'+esc(h.text)+'</a>').join('')+'</div>'+(related.length?'<div class="panel"><h3>이 문서를 가리키는 문서</h3>'+related.map(x=>'<a href="'+link(x.record)+'">'+esc(x.name)+'</a>').join('')+'</div>':'')+'<div class="panel"><h3>문서 정보</h3><p>'+esc(categories[p.category]||p.category)+'</p><div class="record-id">'+esc(id)+'</div></div>';
 document.getElementById('download-md').onclick=()=>{const meta={...p};delete meta.body;delete meta.data;const front='---\n'+Object.entries(meta).map(([k,v])=>k+': '+JSON.stringify(v)).join('\n')+'\n---\n';const url=URL.createObjectURL(new Blob([front+p.body],{type:'text/markdown;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=id+'.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
}
function results(title,items){main.innerHTML='<div class="eyebrow">ARKEN INDEX</div><h1>'+esc(title)+'</h1><p class="lead">'+items.length+'개 문서</p>'+(items.length?items.map(p=>'<div class="result"><a href="'+link(p.record)+'"><strong>'+esc(p.name)+'</strong></a><p>'+esc(p.data?.summary||categories[p.category])+'</p><span class="tag">'+esc(categories[p.category])+'</span></div>').join(''):'<div class="empty">일치하는 문서가 없습니다. 다른 이름이나 키워드로 검색해 보세요.</div>');rail.innerHTML=''}
function route(){let parts;try{parts=location.hash.slice(1).split('/').map(decodeURIComponent)}catch{parts=['home']}const [view,arg,section]=parts;document.getElementById('query').value=view==='search'?(arg||''):'';
 if(view==='page')article(arg);else if(view==='category')results(categories[arg]||arg,pages.filter(p=>p.category===arg));else if(view==='search'){const q=(arg||'').trim().toLocaleLowerCase();results('검색: '+(arg||''),q?pages.filter(p=>(p.name+' '+p.tags.join(' ')+' '+p.body).toLocaleLowerCase().includes(q)).sort((a,b)=>Number(b.name.toLocaleLowerCase().includes(q))-Number(a.name.toLocaleLowerCase().includes(q))):[])}else home();sidebar();document.title=(view==='page'&&byId.has(arg)?byId.get(arg).name+' — ':'')+'아르켄 위키';
 if(section&&/^section-\d+$/.test(section))document.getElementById(section)?.scrollIntoView();else window.scrollTo(0,0);
}
document.getElementById('search').onsubmit=e=>{e.preventDefault();location.hash='search/'+encodeURIComponent(document.getElementById('query').value.trim())};document.getElementById('random').onclick=()=>{const choices=pages.filter(p=>p.category!=='Guide');location.hash=link(choices[Math.floor(Math.random()*choices.length)].record)};document.getElementById('theme').onclick=()=>{document.body.classList.toggle('dark');save('arken-dark',document.body.classList.contains('dark'))};window.addEventListener('hashchange',route);route();
