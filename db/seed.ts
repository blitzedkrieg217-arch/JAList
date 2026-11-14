const initial=[
{name:"General / Japan",items:[
["Power adapters (Qty: 2)"],["Body cam / GoPro-style camera",1],["Suica card (get at destination)"],["Wallet for Nate",1],
["Documents",0,["ID","Passport","All reservation documents","Driver's license"]],["Portable trash bags (get at destination)"],
["Backpack liner",1],["Travel insurance",1],["Sunglasses"],["Hat"],["Polaroid mini photo printer",1],["Crocs (Todd)"]]},
{name:"Toiletries",items:[
["Birth control"],["Tampons"],["Toothbrush"],["Sunscreen"],["Razor"],["Clippers (Nate)"],["Hair ties"],["Q-tips"],["Floss"],["Deodorant"],["Tums"],["Icy Hot patches",1]]},
{name:"Airplane / Carry-on",items:[
["Snacks",0,["Lozenges","Gum","Melatonin","Dramamine","Lip balm","Liquid I.V."]],
["Headphones / earplugs"],["Eye masks"],["Seat cushion",1],["Pillow",1],["Compression socks"],["Blanket",1],["Wet wipes"],["Face mask"],["Water bottle"],["Nintendo Switch",0,["Hard case (?)"]],["Toothbrush + hygiene kit"],["Tissues"],["Deodorant"],["Power bank (check airline restrictions)"],["Pen"]]}];
let counter=0;
function fromInitial(){return {version:1,groups:initial.map((g,gi)=>({id:"g"+gi,name:g.name,items:g.items.map((a,ii)=>({id:"i"+gi+"-"+ii,name:a[0],research:!!a[1],checked:false,notes:"",children:(a[2]||[]).map((s,si)=>({id:"s"+gi+"-"+ii+"-"+si,name:s,research:s.includes("(?)"),checked:false,notes:"",children:[]}))}))}))};}

export const seed = fromInitial;
