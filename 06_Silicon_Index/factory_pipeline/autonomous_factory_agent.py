import os
import json
import yaml
import time
import subprocess
from collections import defaultdict, deque
import re

# ==============================================================================
# ⚠️ 配置你的 API KEY 和 基础 URL
# 支持 OpenAI, DeepSeek, 或者是本地的 vLLM/Ollama 兼容层
# ==============================================================================
API_KEY = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = "gpt-4o" # 或 "deepseek-coder", "gemini-1.5-pro" 等

DB_DIR = "../../08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"
MAP_PATH = "../../08_Domain_Applications/Math_Mentor/学习期prompt/topology_router_map.json"
STATE_FILE = "generation_state.json"
MAX_RETRIES = 3

try:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
except ImportError:
    print("[ERROR] openai package not found. Please install it via `pip install openai`")
    exit(1)

def extract_dag():
    with open(MAP_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    nodes = set(data.keys())
    
    for node_id, info in data.items():
        foundations = info.get("ALLOWED_FOUNDATIONS", [])
        if node_id not in in_degree:
            in_degree[node_id] = 0
            
        for f_text in foundations:
            match = re.search(r'\(n_(\d+)\)', f_text)
            if match:
                parent_id = f"n_{match.group(1)}"
                if parent_id in nodes:
                    graph[parent_id].append(node_id)
                    in_degree[node_id] += 1
                    
    roots = [n for n in nodes if in_degree[n] == 0]
    queue = deque(roots)
    order = []
    
    while queue:
        curr = queue.popleft()
        order.append(curr)
        for child in graph[curr]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)
                
    return order, data, graph

def load_state(order):
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
    else:
        state = {n: "PENDING" for n in order}
        
    # Mark manually created ones as SUCCESS
    for fname in os.listdir(DB_DIR):
        if fname.endswith(".yaml"):
            with open(os.path.join(DB_DIR, fname), 'r', encoding='utf-8') as f:
                try:
                    y = yaml.safe_load(f)
                    if y and 'concept_node' in y and 'id' in y['concept_node']:
                        # The id in our handwritten YAMLs might not perfectly match n_X, 
                        # but in the real run, we will enforce ID mapping.
                        pass
                except Exception:
                    pass
    return state

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def call_llm(prompt):
    print("   [LLM] 发起 API 请求...")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are the Cybernetic City State Math Operator. You output ONLY strictly valid YAML corresponding to the V9.1 concept_node schema. Do not output markdown code blocks like ```yaml, just raw text. Use raw string logic for LaTeX symbols (e.g. \\\\lim)."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

def build_prompt(node_id, node_info, foundations_content):
    prompt = f"""
请为以下数学知识点生成一个 V9.1 格式的 YAML 算子配置文件。

知识点 ID: {node_id}
知识点名称/描述: {json.dumps(node_info, ensure_ascii=False)}

"""
    if foundations_content:
        prompt += "\n此知识点必须基于以下已经生成的前置知识点（上下文挂载）：\n"
        for fid, fyaml in foundations_content.items():
            prompt += f"\n--- 前置依赖 {fid} --- \n{fyaml}\n"
        prompt += "\n**强制要求：你在编写 code_implementation 和 sympy 断言时，应当自然地使用或扩展上述前置代码中的逻辑/张量映射。**\n"

    prompt += """
必须包含以下字段：
concept_node:
  id: "..." # 保持为当前请求的节点 ID
  symbol: "..." # 核心数学符号或公式表达式，注意 LaTeX 语法中的双斜杠
  name: "..." # 知识点名称
  domain: "..." # 所属领域
  pure_math_definition:
    description: "..."
    axioms: []
  llm_physical_mapping:
    tensor_shape_flow: "..."
    cognitive_intuition: "..."
  code_implementation:
    snippet: |
      import torch
      ...
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      ...
      assert ...

请仅输出合法的 YAML，不要使用 markdown 标记！
"""
    return prompt

def main():
    print("=== 启动 V9.1 自动化大工厂 (The Great Synthesis) ===")
    order, node_data, graph = extract_dag()
    state = load_state(order)
    
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs("temp_factory", exist_ok=True)
    
    for node_id in order:
        if state[node_id] == "SUCCESS":
            continue
            
        print(f"\n[*] 正在合成节点: {node_id}")
        
        # 提取前置依赖的 YAML
        foundations = node_data[node_id].get("ALLOWED_FOUNDATIONS", [])
        foundations_content = {}
        for f_text in foundations:
            match = re.search(r'\(n_(\d+)\)', f_text)
            if match:
                fid = f"n_{match.group(1)}"
                path = os.path.join(DB_DIR, f"{fid}.yaml")
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        foundations_content[fid] = f.read()

        base_prompt = build_prompt(node_id, node_data[node_id], foundations_content)
        current_prompt = base_prompt
        
        success = False
        for attempt in range(MAX_RETRIES):
            print(f"   -> 尝试次数: {attempt + 1}/{MAX_RETRIES}")
            try:
                yaml_text = call_llm(current_prompt)
                
                # 清理可能的 markdown 块
                if yaml_text.startswith("```yaml"):
                    yaml_text = yaml_text.split("\n", 1)[1]
                if yaml_text.endswith("```"):
                    yaml_text = yaml_text.rsplit("\n", 1)[0]
                    
                temp_path = f"temp_factory/{node_id}.yaml"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(yaml_text)
                    
                # 运行沙盒测试
                print("   [Sandbox] 运行物理验证...")
                result = subprocess.run(["python", "sandbox_evaluator.py", temp_path], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("   [QC PASSED] 断言通过！")
                    # 验证成功，移动到最终目录
                    final_path = os.path.join(DB_DIR, f"{node_id}.yaml")
                    os.rename(temp_path, final_path)
                    state[node_id] = "SUCCESS"
                    save_state(state)
                    success = True
                    break
                else:
                    error_msg = result.stderr or result.stdout
                    print(f"   [QC FAILED] 沙盒驳回。错误信息:\n{error_msg.strip()}")
                    # 自动反思纠错：把报错信息附加到 Prompt 里让 LLM 重写
                    current_prompt = base_prompt + f"\n\n你的上一次生成未通过物理沙盒测试，报错信息如下：\n{error_msg}\n\n请修正错误并重新输出 YAML。切记不能有非法转义字符或导入被禁用的库！"
            
            except Exception as e:
                print(f"   [API ERROR] 调用失败: {e}")
                time.sleep(5)
                
        if not success:
            print(f"[!] 节点 {node_id} 经过 {MAX_RETRIES} 次重试依旧失败，标记为 FAILED。")
            state[node_id] = "FAILED"
            save_state(state)
            
    print("\n=== 工厂流水线执行完毕 ===")

if __name__ == "__main__":
    main()
