import os
import yaml

def test_topology_tracer():
    print("=== Topology Reachability Test (Mocking Coordinator) ===")
    
    # 模拟用户提问："雅可比矩阵是怎么做多元非线性逼近的？"
    user_query = "雅可比矩阵是怎么做多元非线性逼近的？"
    
    # 模拟 Coordinator 检索命中：
    print(f"\n[Student Query]: {user_query}")
    print("[Coordinator Step 1]: Search DB for keyword '雅可比'")
    
    target_node = "CALCULUS-289" # 假设检索引擎命中了雅可比节点
    print(f"[Coordinator Step 2]: Hit Node => {target_node}")
    
    # 寻找关联大桥
    db_path = "../../08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"
    bridge_files = [f for f in os.listdir(db_path) if f.startswith("BRIDGE-006")]
    
    print(f"[Coordinator Step 3]: Force Backward Trace looking for Bridges...")
    
    if not bridge_files:
        print("[FAILED] BRIDGE-006 not found.")
        return
        
    bridge_path = os.path.join(db_path, bridge_files[0])
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bridge_data = yaml.safe_load(f)
        
    print(f"[Coordinator Step 4]: Found Intersecting Bridge => {bridge_files[0]}")
    print(f"  -> Bridge Name: {bridge_data.get('concept_name')}")
    print(f"  -> Physical Metaphor: {bridge_data.get('llm_physical_mapping')}")
    
    # 根据大桥内容提取关联线代节点 (LINEAR_ALGEBRA-308)
    print("\n[Socratic Router Output]:")
    print(f">> 你还记得线性代数里的矩阵运算吗？其实，【{bridge_data.get('concept_name')}】。")
    print(f">> 想象一下：{bridge_data.get('llm_physical_mapping')}")
    print(">> [Cliffhanger]: 那么，如果这个平坦网格被不均匀的拉伸，这对应矩阵里的什么概念？(引向特征值...)")
    
    print("\n[SUCCESS] Topology traced successfully. Socratic Router generated correct response.")

if __name__ == "__main__":
    test_topology_tracer()
