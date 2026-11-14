import re,json,pathlib
p=pathlib.Path(__file__).parent
s=(p/'original-index.html').read_text()
initial=re.search(r'const initial=(\[.*?\]);\nlet counter',s,re.S).group(1)
# Keep original list generator as the server's authoritative first-run seed.
seed=s[s.index('const initial='):s.index('function valid')]
(p/'db/seed.ts').write_text(seed+'\nexport const seed = fromInitial;\n')
s=re.sub(r'<details class="syncbox">.*?</details>','',s,flags=re.S)
s=re.sub(r'  <button id="exportBtn">.*?<input type="file"[^>]+>','',s,flags=re.S)
s=s.replace('Saved in this browser','Loading cloud list…')
s=re.sub(r'<footer>.*?</footer>','<footer>Private list · Automatically saved to your account · <a href="/signout-with-chatgpt?return_to=%2F" target="_top">Sign out</a></footer>',s,flags=re.S)
s=s.replace('let data;try{data=JSON.parse(localStorage.getItem(KEY));if(!valid(data))throw 0;}catch{data=fromInitial();}','let data=fromInitial(); let ready=false;')
s=re.sub(r'function save\(\).*?\nfunction flat', 'function save(){queueSave();}\nfunction flat',s,flags=re.S)
s=s.replace('const id="custom-"+Date.now()+"-"+(++counter);','const id="custom-"+crypto.randomUUID();')
a=s.index('$("exportBtn").addEventListener');s=s[:a]+'''__SYNC__
</script></body></html>'''
# Add an initial loading guard, accessible status, and mobile wrapping.
s=s.replace('<span class="muted" id="saveText">','<span class="muted" role="status" aria-live="polite" id="saveText">')
s=s.replace('.itemline{display:flex;', '.itemline{flex-wrap:wrap;display:flex;')
s=s.replace('.itemname{flex:1;', '.itemname{min-width:90px;flex:1;')
s=s.replace('main{max-width:', 'main.inactive{pointer-events:none;opacity:.6}main{max-width:')
s=s.replace('<main>', '<main class="inactive">')
s=s.replace('$("progressBar").style.width=', 'document.querySelector("[role=progressbar]").setAttribute("aria-valuenow",String(items.length?Math.round(100*done/items.length):0));\n $("progressBar").style.width=')
s=s.replace('const items=allItems(),done=items.filter(x=>x.checked).length;', 'const category=$("itemCategory").value;\n const items=allItems(),done=items.filter(x=>x.checked).length;')
s=s.replace(' updateParents();\n}', ' if(data.groups.some(g=>g.id===category))$("itemCategory").value=category;\n updateParents();\n}')
s=s.replace('const isOpen=showAllNotes||opened.has(i.id)', 'const isOpen=(showAllNotes&&!!(i.notes||"\\").trim())||opened.has(i.id)') if False else s
# Research filtering must include descendants at all depths.
s=s.replace('!(i.children||[]).some(x=>x.research)', '!flat(i.children||[]).some(x=>x.research)')
sync='''
let baseline=null, busy=false, dirty=false, retryPacket=null, retrySent=null, timer;
const clone=x=>JSON.parse(JSON.stringify(x));
function index(d){const m=new Map();for(const g of d.groups){function visit(items,parent){for(const i of items){m.set(i.id,{i,group:g.id,parent});visit(i.children||[],i.id);}}visit(g.items,null);}return m;}
function diff(before,after){
 const a=index(before),b=index(after),ops=[];
 for(const [id,v] of a)if(!b.has(id))ops.push({type:'remove',id});
 for(const [id,v] of b){const old=a.get(id);if(!old){if(!v.parent||a.has(v.parent))ops.push({type:'add',group:v.group,parent:v.parent,item:v.i});continue;}
 const fields={};for(const k of ['name','notes','checked','research'])if(old.i[k]!==v.i[k])fields[k]=v.i[k];
 if(Object.keys(fields).length)ops.push({type:'update',id,fields});}
 return ops;
}
function status(text){$('saveText').textContent=text;}
function queueSave(){if(!ready)return;dirty=true;status('Saving…');clearTimeout(timer);timer=setTimeout(sync,600);}
async function request(method,body){const r=await fetch('/api/list',{method,cache:'no-store',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});if(!r.ok)throw Error(r.status===401?'Sign in required':'Cloud unavailable');return r.json();}
async function sync(){
 if(busy)return;busy=true;
 try{
 if(!ready){const remote=await request('GET');data=remote.data;baseline=clone(data);ready=true;document.querySelector('main').classList.remove('inactive');render();status('All changes saved');return;}
 if(retryPacket||dirty){
 const packet=retryPacket||{id:crypto.randomUUID(),ops:diff(baseline,data)};
 const sent=retrySent||clone(data);retrySent=sent;retryPacket=packet;status('Saving…');
 const remote=await request('POST',packet);
 retryPacket=null;retrySent=null;
 // Preserve edits made while the request was in flight, then rebase them onto cloud state.
 const later=diff(sent,data);baseline=clone(remote.data);data=applyLocal(clone(remote.data),later);dirty=later.length>0;
 if(!document.querySelector('textarea:focus'))render();
 status(dirty?'Saving…':'All changes saved');
 }else if(!document.querySelector('textarea:focus')&&!document.hidden){
 const remote=await request('GET');const pending=diff(baseline,data);baseline=clone(remote.data);data=applyLocal(clone(remote.data),pending);dirty=pending.length>0;if(!document.querySelector('textarea:focus'))render();status(dirty?'Saving…':'All changes saved');
 }
 }catch(e){status(navigator.onLine?'Sync interrupted · retrying automatically':'Offline · changes waiting to sync');}
 finally{busy=false;if(dirty||retryPacket)timer=setTimeout(sync,2500);}
}
function applyLocal(d,ops){for(const op of ops){const m=index(d),v=m.get(op.id);if(op.type==='update'&&v)Object.assign(v.i,op.fields);if(op.type==='remove'&&v){const g=d.groups.find(x=>x.id===v.group),items=v.parent?m.get(v.parent).i.children:g.items;items.splice(items.findIndex(x=>x.id===op.id),1);}if(op.type==='add'&&!m.has(op.item.id)){const g=d.groups.find(x=>x.id===op.group),parent=op.parent?m.get(op.parent):null;if(g&&(!op.parent||parent))(parent?parent.i.children:g.items).push(clone(op.item));}}return d;}
window.addEventListener('online',sync);window.addEventListener('focus',sync);
window.addEventListener('beforeunload',e=>{if(dirty||retryPacket){e.preventDefault();e.returnValue='';}});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)sync();});
setInterval(sync,5000);sync();
'''
s=s.replace('__SYNC__',sync)
(p/'app/packing-html.ts').write_text('export const packingHTML = '+json.dumps(s)+';\n')
(p/'app/page.tsx').unlink(missing_ok=True)
(p/'app/route.ts').write_text('''import { packingHTML } from './packing-html';
import { requireChatGPTUser } from './chatgpt-auth';
export const dynamic='force-dynamic';
export async function GET(){await requireChatGPTUser('/');return new Response(packingHTML,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin'}});}
''')
(p/'app/layout.tsx').write_text('export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}\n')
