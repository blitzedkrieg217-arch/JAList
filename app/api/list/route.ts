import { env } from 'cloudflare:workers';
import { getChatGPTUser } from '../../chatgpt-auth';
import { seed } from '../../../db/seed';
import { applyOperations } from '../../../db/operations';
export const dynamic='force-dynamic';
const json=(data:any,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
async function load(user:string){
 await env.DB.prepare('INSERT OR IGNORE INTO packing_lists (user_id, document, revision) VALUES (?, ?, 0)').bind(user,JSON.stringify({data:seed(),receipts:[]})).run();
 return await env.DB.prepare('SELECT document, revision FROM packing_lists WHERE user_id = ?').bind(user).first<{document:string,revision:number}>();
}
export async function GET(){const user=await getChatGPTUser();if(!user)return json({error:'Sign in required'},401);const row=await load(user.userId);return json({data:JSON.parse(row!.document).data,revision:row!.revision});}
export async function POST(request:Request){
 const user=await getChatGPTUser();if(!user)return json({error:'Sign in required'},401);
 if(request.headers.get('origin')!==new URL(request.url).origin)return json({error:'Invalid origin'},403);
 if(Number(request.headers.get('content-length')||0)>1000000)return json({error:'Request too large'},413);
 let body:any;try{const text=await request.text();if(text.length>1000000)return json({error:'Request too large'},413);body=JSON.parse(text);if(typeof body.id!=='string'||body.id.length>100||!Array.isArray(body.ops)||body.ops.length>3000)throw 0;}catch{return json({error:'Invalid request'},400);}
 for(let attempt=0;attempt<8;attempt++){
  const row=await load(user.userId),doc=JSON.parse(row!.document);
  if(doc.receipts.includes(body.id))return json({data:doc.data,revision:row!.revision});
  try{applyOperations(doc.data,body.ops);}catch{return json({error:'Invalid update'},400);}
  doc.receipts=[...doc.receipts.slice(-199),body.id];
  const result=await env.DB.prepare('UPDATE packing_lists SET document = ?, revision = revision + 1 WHERE user_id = ? AND revision = ?').bind(JSON.stringify(doc),user.userId,row!.revision).run();
  if(result.meta.changes)return json({data:doc.data,revision:row!.revision+1});
 }
 return json({error:'Busy; retry shortly'},409);
}
