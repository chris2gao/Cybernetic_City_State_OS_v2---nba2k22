import yaml
import json
import re
import os

class ASTNode:
    """
    AST 物理树节点，映射 YAML 的层级和物理排列
    """
    def __init__(self, key_name, depth):
        self.key_name = key_name
        self.node_id = self._extract_id(key_name)
        self.depth = depth
        
        # 核心拓扑指针
        self.parent = None
        self.children = []
        self.prev_sibling = None
        self.next_sibling = None
        self.global_id = -1
        
        # 叶子节点具体的 bullet points (具体知识点)
        self.bullet_points = []
        
    def _extract_id(self, name):
        """尝试从字符串中提取 n_XX 格式的 ID"""
        match = re.search(r'\(n_(\d+)\)', name)
        if match:
            return f"n_{match.group(1)}"
        return None
        
    def __repr__(self):
        return f"<ASTNode '{self.key_name}' (ID: {self.node_id}, Depth: {self.depth}, GlobalID: {self.global_id})>"

class YamlTopologyCompiler:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.root_nodes = []
        self.all_nodes = []
        self.id_to_node = {}
        
    def build_ast(self):
        """解析 YAML 并构建带双向物理指针的多叉树"""
        print(f"Loading YAML from {self.yaml_path}...")
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        self.root_nodes = self._build_ast_recursive(data, depth=0, parent=None)
        self._assign_global_ids_and_map(self.root_nodes)
        print(f"AST built. Total entities: {len(self.all_nodes)}")
        
    def _build_ast_recursive(self, data, depth, parent):
        nodes = []
        if isinstance(data, dict):
            # Python 3.7+ 字典保持插入顺序，这正是我们的物理顺序
            keys = list(data.keys())
            prev_node = None
            for k in keys:
                node = ASTNode(k, depth)
                node.parent = parent
                
                # 建立水平物理指针 (Horizontal Pointers)
                if prev_node:
                    prev_node.next_sibling = node
                    node.prev_sibling = prev_node
                
                nodes.append(node)
                prev_node = node
                
                # 递归子层级
                child_data = data[k]
                if isinstance(child_data, (dict, list)):
                    child_nodes = self._build_ast_recursive(child_data, depth + 1, node)
                    node.children = child_nodes
        elif isinstance(data, list):
            # 这是一个纯列表，说明是底层的 bullet points
            if parent:
                parent.bullet_points = [str(x) for x in data]
        return nodes

    def _assign_global_ids_and_map(self, root_nodes):
        """执行全局先序遍历，分配递增序号，并建立 ID 映射表"""
        counter = 0
        def traverse(nodes):
            nonlocal counter
            for node in nodes:
                node.global_id = counter
                self.all_nodes.append(node)
                if node.node_id:
                    self.id_to_node[node.node_id] = node
                counter += 1
                traverse(node.children)
        traverse(root_nodes)
        
    def _get_prefix(self, name):
        if " - " in name:
            return name.split(" - ")[0].strip()
        return name
        
    def _get_full_subtree_text(self, node):
        """深度全量提取：返回包含节点标题及所有细分知识点文本的列表"""
        res = [node.key_name]
        res.extend(node.bullet_points)
        for child in node.children:
            res.extend(self._get_full_subtree_text(child))
        return res
        
    def _get_right_most_leaf(self, node):
        """获取一棵树的最右侧（终端）实体叶子节点"""
        if not node.children:
            return node
        return self._get_right_most_leaf(node.children[-1])

    def compute_allowed_foundations(self, target_node):
        """Phase 2: 前向底座提取算法"""
        allowed = []
        
        # 1. 语境树干追踪
        curr = target_node.parent
        while curr:
            allowed.append(curr.key_name)
            curr = curr.parent
            
        # 2. 同层前序追踪（强依赖 vs 历史降维）
        target_prefix = self._get_prefix(target_node.key_name)
        historical_domains_seen = set()
        
        curr = target_node.prev_sibling
        while curr:
            curr_prefix = self._get_prefix(curr.key_name)
            if curr_prefix == target_prefix:
                # 同域强依赖：100% 深度全量提取
                allowed.extend(self._get_full_subtree_text(curr))
            else:
                # 跨域历史板块（同层）：仅保留终点接口（代理降维）
                if curr_prefix not in historical_domains_seen:
                    allowed.append(f"【降维代理】 {curr_prefix} -> 终点知识: {curr.key_name}")
                    historical_domains_seen.add(curr_prefix)
            curr = curr.prev_sibling
            
        # 3. 跨层历史板块（远古大阶段）：代理降维
        p = target_node.parent
        while p:
            p_sibling = p.prev_sibling
            while p_sibling:
                right_most = self._get_right_most_leaf(p_sibling)
                allowed.append(f"【历史大阶段代理】 {p_sibling.key_name} -> 终点: {right_most.key_name}")
                p_sibling = p_sibling.prev_sibling
            p = p.parent
            
        return allowed

    def compute_forbidden_terms(self, target_node):
        """Phase 2: 后向致盲提取算法"""
        forbidden = []
        
        # 1. 局部高密度封锁：同父节点下紧随其后的所有未来兄弟节点
        curr = target_node.next_sibling
        while curr:
            forbidden.extend(self._get_full_subtree_text(curr))
            curr = curr.next_sibling
            
        # 2. 全局低密度致盲：跨越当前阶段的未来大阶段
        p = target_node.parent
        while p:
            p_sibling = p.next_sibling
            while p_sibling:
                # 仅截取大类标题和第二层级副标题，不深入具体知识点
                forbidden.append(f"【未来高维致盲】 {p_sibling.key_name}")
                for child in p_sibling.children:
                    forbidden.append(f"【未来领域】 {child.key_name}")
                p_sibling = p_sibling.next_sibling
            p = p.parent
            
        return forbidden

    def compile_to_json(self, output_path):
        """Phase 3: 全局编译与序列化"""
        print(f"Starting global compilation for {len(self.id_to_node)} specific nodes...")
        routing_map = {}
        
        for node_id, node in self.id_to_node.items():
            allowed = self.compute_allowed_foundations(node)
            forbidden = self.compute_forbidden_terms(node)
            
            routing_map[node_id] = {
                "ALLOWED_FOUNDATIONS": allowed,
                "FORBIDDEN_TERMS": forbidden
            }
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(routing_map, f, ensure_ascii=False, indent=2)
            
        print(f"Compilation finished! O(1) Routing table saved to: {output_path}")

if __name__ == "__main__":
    # 执行全量编译
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, "../01_Research_Reports/数学知识路线图_知识点版.yaml")
    output_json_path = os.path.join(current_dir, "../01_Research_Reports/topology_router_map.json")
    
    compiler = YamlTopologyCompiler(yaml_path)
    compiler.build_ast()
    
    compiler.compile_to_json(output_json_path)
