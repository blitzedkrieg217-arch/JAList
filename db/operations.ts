export function applyOperations(data:any, ops:any[]) {
 const index=()=>{const map=new Map<string,any>(); for(const g of data.groups){const visit=(items:any[],parent:any)=>{for(const i of items){map.set(i.id,{i,items,g,parent});visit(i.children||[],i);}};visit(g.items,null);}return map;};
 for(const op of ops){
  if(!op||!['add','remove','update'].includes(op.type))throw Error('Invalid operation');
  const m=index(),found=m.get(op.id);
  if(op.type==='remove'&&found)found.items.splice(found.items.indexOf(found.i),1);
  if(op.type==='update'){
   if(!op.fields||Object.keys(op.fields).some(k=>!['name','notes','checked','research'].includes(k)))throw Error('Invalid fields');
   for(const [k,v] of Object.entries(op.fields)){
    if(['name','notes'].includes(k)?typeof v!=='string'||(v as string).length>(k==='name'?150:20000):typeof v!=='boolean')throw Error('Invalid value');
    if(k==='name'&&!(v as string).trim())throw Error('Name required');
   }
   if(found)Object.assign(found.i,op.fields);
  }
  if(op.type==='add'){
   const check=(i:any,depth=0)=>{if(depth>12||!i||typeof i.id!=='string'||i.id.length>100||typeof i.name!=='string'||!i.name.trim()||i.name.length>150||typeof i.notes!=='string'||i.notes.length>20000||typeof i.checked!=='boolean'||typeof i.research!=='boolean'||!Array.isArray(i.children))throw Error('Invalid item');i.children.forEach((c:any)=>check(c,depth+1));};check(op.item);
   const g=data.groups.find((g:any)=>g.id===op.group),parent=op.parent?m.get(op.parent):null;
   if(!g||op.parent&&(!parent||parent.g.id!==g.id))continue;
   if(!m.has(op.item.id))(parent?parent.i.children:g.items).push(op.item);
  }
 }
 if(JSON.stringify(data).length>1000000)throw Error('List too large');
 return data;
}
