import fs from 'node:fs/promises';import path from 'node:path';import {pathToFileURL} from 'node:url';
const root=process.argv[2];if(!root)throw Error('evidence directory required');
const pkg=path.join(process.env.APPDATA,'npm/node_modules/rea-agents'),sdk=path.join(pkg,'node_modules/@modelcontextprotocol/client/dist');
const {Client}=await import(pathToFileURL(path.join(sdk,'index.mjs')));const {StdioClientTransport}=await import(pathToFileURL(path.join(sdk,'stdio.mjs')));
const client=new Client({name:'nba2k22-resource-comparison',version:'1.0.0'}),transport=new StdioClientTransport({command:process.execPath,args:[path.join(pkg,'scripts/rea.mjs'),'mcp'],env:{...process.env,REA_MCP_OUTPUT_SCHEMA_PROFILE:'off'},stderr:'pipe'});
const metrics=[];
function decode(r){return r.structuredContent??JSON.parse(r.content.find(c=>c.type==='text').text);}
async function call(name,args){const start=performance.now();const r=await client.callTool({name,arguments:args},{timeout:60000});metrics.push({name,ms:Math.round(performance.now()-start),bytes:Buffer.byteLength(JSON.stringify(r)),isError:r.isError===true});if(r.isError)throw Error(JSON.stringify(decode(r)));return decode(r);}
try{
 await client.connect(transport);
 await call('open_binary',{path:'E:/Games/NBA 2K22/Mods/newscorebug.iff'});
 const left=await call('inspect_artifact',{});await call('close_binary',{});
 await call('open_binary',{path:path.join(root,'rea-scorebug-preview.iff')});
 const right=await call('inspect_artifact',{});
 const result=await call('compare_artifacts',{left,right});
 await fs.writeFile(path.join(root,'scorebug-comparison.json'),JSON.stringify(result,null,2));
 await call('export_evidence_bundle',{path:path.join(root,'scorebug-comparison-evidence.json')});
 console.log(JSON.stringify({evidence_id:result.evidence_id,normalized_keys:Object.keys(result.normalized_result??{}),metrics}));
}finally{try{await call('close_binary',{});}finally{await client.close();await fs.writeFile(path.join(root,'scorebug-comparison-metrics.json'),JSON.stringify(metrics,null,2));}}
