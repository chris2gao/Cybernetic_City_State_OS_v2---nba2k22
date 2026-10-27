import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const packageRoot=path.join(process.env.APPDATA,'npm/node_modules/rea-agents');
const sdk=path.join(packageRoot,'node_modules/@modelcontextprotocol/client/dist');
const {Client}=await import(pathToFileURL(path.join(sdk,'index.mjs')));
const {StdioClientTransport}=await import(pathToFileURL(path.join(sdk,'stdio.mjs')));
const out=process.argv[2];if(!out)throw Error('output path required');
const client=new Client({name:'nba2k22-development-capability-inventory',version:'1.0.0'});
const transport=new StdioClientTransport({command:process.execPath,args:[path.join(packageRoot,'scripts/rea.mjs'),'mcp'],env:{...process.env,REA_MCP_OUTPUT_SCHEMA_PROFILE:'off'},stderr:'pipe'});
const selected=new Set(['open_binary','close_binary','inspect_artifact','extract_artifact','compare_artifacts','inspect_analysis_view','export_evidence_bundle','instrument_with_frida','start_frida_session','load_frida_script','frida_session_status','unload_frida_script','close_frida_session','list_frida_processes','analyze_function','search_strings','trace_native_values','inspect_binary_layout']);
function strip(v){if(Array.isArray(v))return v.map(strip);if(v&&typeof v==='object')return Object.fromEntries(Object.entries(v).filter(([k])=>!['description','title','examples'].includes(k)).map(([k,x])=>[k,strip(x)]));return v;}
try{
 await client.connect(transport);const t=await client.listTools();const pkg=JSON.parse(await fs.readFile(path.join(packageRoot,'package.json'),'utf8'));
 const result={package_version:pkg.version,tool_count:t.tools.length,all_tool_names:t.tools.map(t=>t.name),selected_tools:t.tools.filter(t=>selected.has(t.name)).map(t=>({name:t.name,purpose:t.description.split('\n\n')[0],input_schema:strip(t.inputSchema)})),limitations:['catalog discovery is not backend or platform usability proof','same exact package version must be checked before reusing these schemas']};
 await fs.writeFile(out,JSON.stringify(result,null,2));
 console.log(JSON.stringify({package_version:pkg.version,count:result.tool_count,selected:result.selected_tools.map(t=>({name:t.name,required:t.input_schema.required??[],fields:Object.keys(t.input_schema.properties??{})}))}));
}finally{await client.close();}
