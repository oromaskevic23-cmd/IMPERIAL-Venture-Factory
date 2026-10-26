"use strict";
const el=id=>document.getElementById(id);
let csrf="",projectId="",versionId="";
function status(s){el("status").textContent=s;}
async function call(path,{method="GET",data}={}){
 const options={method,credentials:"same-origin",headers:{"Accept":"application/json"}};
 if(data!==undefined){options.headers["Content-Type"]="application/json";options.headers["X-CSRF-Token"]=csrf;options.body=JSON.stringify(data);}
 const r=await fetch(path,options),value=await r.json();
 if(!r.ok)throw new Error(value.error||"HTTP "+r.status);
 return value;
}
async function action(fn){try{await fn();}catch(e){status("Error: "+e.message);}}
async function identity(){
 const me=await call("/api/me");csrf=me.csrf;el("account").textContent="Signed in: "+me.email;
 await projects();
}
async function auth(type){
 const result=await call("/api/"+type,{method:"POST",data:{email:el("email").value,password:el("password").value}});
 csrf=result.csrf;await identity();status("Account ready.");
}
async function projects(){
 const data=await call("/api/projects");const s=el("projects");s.replaceChildren();
 let option=document.createElement("option");option.value="";option.textContent="Choose a project";s.append(option);
 for(const p of data.projects){option=document.createElement("option");option.value=String(p.id);option.textContent=p.name+" (#"+p.id+")";s.append(option);}
 if(projectId&&data.projects.some(p=>String(p.id)===projectId)){s.value=projectId;await detail();}
}
async function detail(){
 projectId=el("projects").value;
 if(!projectId)return;
 const v=await call("/api/projects/"+projectId);
 const s=el("versions");s.replaceChildren();let op=document.createElement("option");op.value="";op.textContent="Select version";s.append(op);
 for(const x of v.versions){op=document.createElement("option");op.value=String(x.id);op.textContent=x.filename+" · revision "+x.number;s.append(op);}
 if(versionId&&v.versions.some(x=>String(x.id)===versionId))s.value=versionId;
 else if(v.versions.length){versionId=String(v.versions.at(-1).id);s.value=versionId;}
 el("details").textContent=JSON.stringify(v,null,2);
}
el("accountForm").addEventListener("submit",e=>{e.preventDefault();action(()=>auth("login"));});
el("register").addEventListener("click",()=>action(()=>auth("register")));
el("logout").addEventListener("click",()=>action(async()=>{await call("/api/logout",{method:"POST",data:{}});csrf="";projectId="";versionId="";el("account").textContent="Not signed in";el("details").textContent="Signed out";status("Signed out.");}));
el("projectForm").addEventListener("submit",e=>{e.preventDefault();action(async()=>{
 const v=await call("/api/projects",{method:"POST",data:{name:el("projectName").value}});
 projectId=String(v.project_id);await projects();status("Project created: "+projectId);});});
el("projects").addEventListener("change",()=>action(detail));
el("refresh").addEventListener("click",()=>action(projects));
el("reviewerForm").addEventListener("submit",e=>{e.preventDefault();action(async()=>{
 await call("/api/projects/"+projectId+"/reviewers",{method:"POST",data:{email:el("reviewerEmail").value}});
 await detail();status("Reviewer invited.");});});
el("uploadForm").addEventListener("submit",e=>{e.preventDefault();action(async()=>{
 const v=await call("/api/projects/"+projectId+"/versions",{method:"POST",
 data:{filename:el("fileName").value,content:el("fileContent").value}});
 versionId=String(v.version_id);await detail();status("Document revision "+v.number+" saved.");});});
el("versions").addEventListener("change",()=>{versionId=el("versions").value;});
el("commentForm").addEventListener("submit",e=>{e.preventDefault();action(async()=>{
 await call("/api/versions/"+versionId+"/comments",{method:"POST",data:{text:el("commentText").value}});
 await detail();status("Reviewer comment persisted.");});});
for(const decision of ["approve","reject"]){
 el(decision).addEventListener("click",()=>action(async()=>{
  await call("/api/versions/"+versionId+"/decisions",{method:"POST",data:{decision:decision.toUpperCase()}});
  await detail();status("Version "+decision+" decision saved.");}));
}
el("export").addEventListener("click",()=>action(async()=>{
 const data=await call("/api/projects/"+projectId+"/export");
 const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});
 const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="approvedesk-project-"+projectId+".json";a.click();
 setTimeout(()=>URL.revokeObjectURL(a.href),1000);status("Export ready.");}));
action(identity);
