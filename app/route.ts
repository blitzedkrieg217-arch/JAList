import { packingHTML } from './packing-html';
import { requireChatGPTUser } from './chatgpt-auth';
export const dynamic='force-dynamic';
export async function GET(){await requireChatGPTUser('/');return new Response(packingHTML,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin'}});}
