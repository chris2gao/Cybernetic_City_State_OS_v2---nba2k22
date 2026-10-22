# -*- coding: utf-8 -*-
"""
生成官方级 1984 年 NBA 历史选秀名单（整整 60 名真实新秀）
包含真实姓名、顺位预期、位置、面补 ID、身高级别、初始总评、潜力值与攻防倾向。
"""
import os
import json

PLAYERS_1984 = [
    # 首轮乐透与前场超巨 (Picks 1 - 14)
    {"pick": 1, "first": "Hakeem", "last": "Olajuwon", "pos": 4, "face": 378, "ht": 213, "wt": 255, "ovr": 84, "pot": 98, "mid": 82, "three": 25, "in_def": 92, "blk": 94, "team": "HOU"},
    {"pick": 2, "first": "Sam", "last": "Bowie", "pos": 4, "face": 1050, "ht": 216, "wt": 235, "ovr": 76, "pot": 83, "mid": 75, "three": 25, "in_def": 78, "blk": 80, "team": "POR"},
    {"pick": 3, "first": "Michael", "last": "Jordan", "pos": 1, "face": 653, "ht": 198, "wt": 198, "ovr": 85, "pot": 99, "mid": 95, "three": 74, "in_def": 82, "blk": 82, "team": "CHI"},
    {"pick": 4, "first": "Sam", "last": "Perkins", "pos": 3, "face": 1051, "ht": 206, "wt": 240, "ovr": 78, "pot": 87, "mid": 80, "three": 68, "in_def": 79, "blk": 76, "team": "DAL"},
    {"pick": 5, "first": "Charles", "last": "Barkley", "pos": 3, "face": 606, "ht": 198, "wt": 252, "ovr": 82, "pot": 96, "mid": 80, "three": 65, "in_def": 84, "blk": 79, "team": "PHI"},
    {"pick": 6, "first": "Melvin", "last": "Turpin", "pos": 4, "face": 1052, "ht": 211, "wt": 240, "ovr": 74, "pot": 81, "mid": 72, "three": 25, "in_def": 76, "blk": 77, "team": "CLE"},
    {"pick": 7, "first": "Alvin", "last": "Robertson", "pos": 1, "face": 1053, "ht": 190, "wt": 185, "ovr": 78, "pot": 89, "mid": 78, "three": 45, "in_def": 75, "blk": 60, "team": "SAS"},
    {"pick": 8, "first": "Lancaster", "last": "Gordon", "pos": 1, "face": 1054, "ht": 190, "wt": 185, "ovr": 73, "pot": 79, "mid": 74, "three": 40, "in_def": 70, "blk": 50, "team": "LAC"},
    {"pick": 9, "first": "Otis", "last": "Thorpe", "pos": 3, "face": 1055, "ht": 206, "wt": 225, "ovr": 77, "pot": 86, "mid": 75, "three": 25, "in_def": 80, "blk": 75, "team": "SAC"},
    {"pick": 10, "first": "Leon", "last": "Wood", "pos": 0, "face": 1056, "ht": 190, "wt": 185, "ovr": 72, "pot": 78, "mid": 76, "three": 60, "in_def": 65, "blk": 40, "team": "PHI"},
    {"pick": 11, "first": "Kevin", "last": "Willis", "pos": 4, "face": 663, "ht": 213, "wt": 220, "ovr": 77, "pot": 87, "mid": 76, "three": 25, "in_def": 82, "blk": 78, "team": "ATL"},
    {"pick": 12, "first": "Tim", "last": "McCormick", "pos": 4, "face": 1057, "ht": 211, "wt": 240, "ovr": 72, "pot": 79, "mid": 70, "three": 25, "in_def": 75, "blk": 72, "team": "CLE"},
    {"pick": 13, "first": "Jay", "last": "Humphries", "pos": 0, "face": 1058, "ht": 190, "wt": 185, "ovr": 74, "pot": 83, "mid": 76, "three": 50, "in_def": 74, "blk": 45, "team": "PHX"},
    {"pick": 14, "first": "Michael", "last": "Cage", "pos": 3, "face": 1059, "ht": 206, "wt": 224, "ovr": 76, "pot": 84, "mid": 73, "three": 25, "in_def": 81, "blk": 76, "team": "LAC"},

    # 首轮中后段 (Picks 15 - 30)
    {"pick": 15, "first": "Terence", "last": "Stansbury", "pos": 1, "face": 1060, "ht": 196, "wt": 170, "ovr": 71, "pot": 78, "mid": 72, "three": 45, "in_def": 68, "blk": 45, "team": "DAL"},
    {"pick": 16, "first": "John", "last": "Stockton", "pos": 0, "face": 417, "ht": 185, "wt": 170, "ovr": 76, "pot": 96, "mid": 85, "three": 78, "in_def": 75, "blk": 45, "team": "UTA"},
    {"pick": 17, "first": "Jeff", "last": "Turner", "pos": 3, "face": 1061, "ht": 206, "wt": 230, "ovr": 72, "pot": 79, "mid": 75, "three": 55, "in_def": 74, "blk": 70, "team": "NJN"},
    {"pick": 18, "first": "Vern", "last": "Fleming", "pos": 0, "face": 1062, "ht": 196, "wt": 185, "ovr": 75, "pot": 84, "mid": 78, "three": 45, "in_def": 76, "blk": 50, "team": "IND"},
    {"pick": 19, "first": "Bernard", "last": "Thompson", "pos": 2, "face": 1063, "ht": 198, "wt": 210, "ovr": 71, "pot": 77, "mid": 73, "three": 40, "in_def": 70, "blk": 55, "team": "POR"},
    {"pick": 20, "first": "Tony", "last": "Campbell", "pos": 2, "face": 1064, "ht": 201, "wt": 215, "ovr": 72, "pot": 80, "mid": 76, "three": 50, "in_def": 71, "blk": 52, "team": "DET"},
    {"pick": 21, "first": "Kenny", "last": "Green", "pos": 2, "face": 1065, "ht": 198, "wt": 210, "ovr": 70, "pot": 76, "mid": 71, "three": 35, "in_def": 69, "blk": 50, "team": "PHI"},
    {"pick": 22, "first": "Tom", "last": "Sewell", "pos": 1, "face": 1066, "ht": 196, "wt": 185, "ovr": 69, "pot": 75, "mid": 70, "three": 40, "in_def": 68, "blk": 45, "team": "PHI"},
    {"pick": 23, "first": "Earl", "last": "Jones", "pos": 4, "face": 1067, "ht": 213, "wt": 230, "ovr": 70, "pot": 76, "mid": 68, "three": 25, "in_def": 73, "blk": 74, "team": "LAL"},
    {"pick": 24, "first": "Michael", "last": "Young", "pos": 2, "face": 1068, "ht": 201, "wt": 220, "ovr": 71, "pot": 77, "mid": 74, "three": 45, "in_def": 70, "blk": 55, "team": "BOS"},
    {"pick": 25, "first": "Devin", "last": "Durrant", "pos": 2, "face": 1069, "ht": 201, "wt": 200, "ovr": 70, "pot": 76, "mid": 75, "three": 55, "in_def": 67, "blk": 45, "team": "IND"},
    {"pick": 26, "first": "Victor", "last": "Fleming", "pos": 0, "face": 1070, "ht": 188, "wt": 175, "ovr": 69, "pot": 75, "mid": 71, "three": 40, "in_def": 68, "blk": 40, "team": "POR"},
    {"pick": 27, "first": "Ron", "last": "Anderson", "pos": 2, "face": 1071, "ht": 201, "wt": 215, "ovr": 72, "pot": 79, "mid": 77, "three": 50, "in_def": 70, "blk": 50, "team": "CLE"},
    {"pick": 28, "first": "Cory", "last": "Blackwell", "pos": 2, "face": 1072, "ht": 198, "wt": 210, "ovr": 68, "pot": 74, "mid": 70, "three": 35, "in_def": 68, "blk": 48, "team": "SEA"},
    {"pick": 29, "first": "Stuart", "last": "Gray", "pos": 4, "face": 1073, "ht": 213, "wt": 235, "ovr": 70, "pot": 76, "mid": 67, "three": 25, "in_def": 74, "blk": 73, "team": "IND"},
    {"pick": 30, "first": "Steve", "last": "Burtt", "pos": 0, "face": 1074, "ht": 188, "wt": 185, "ovr": 71, "pot": 77, "mid": 75, "three": 55, "in_def": 67, "blk": 40, "team": "GSW"},

    # 次轮实力拼图与遗珠 (Picks 31 - 45)
    {"pick": 31, "first": "Jay", "last": "Murphy", "pos": 3, "face": 1075, "ht": 206, "wt": 220, "ovr": 69, "pot": 75, "mid": 72, "three": 30, "in_def": 72, "blk": 68, "team": "GSW"},
    {"pick": 32, "first": "Vince", "last": "Humphries", "pos": 3, "face": 1076, "ht": 203, "wt": 225, "ovr": 68, "pot": 74, "mid": 69, "three": 25, "in_def": 71, "blk": 66, "team": "SAS"},
    {"pick": 33, "first": "Steve", "last": "Colter", "pos": 0, "face": 1077, "ht": 190, "wt": 165, "ovr": 71, "pot": 78, "mid": 74, "three": 50, "in_def": 72, "blk": 42, "team": "POR"},
    {"pick": 34, "first": "Tony", "last": "Costner", "pos": 4, "face": 1078, "ht": 208, "wt": 225, "ovr": 68, "pot": 73, "mid": 66, "three": 25, "in_def": 72, "blk": 70, "team": "WAS"},
    {"pick": 35, "first": "Othell", "last": "Wilson", "pos": 0, "face": 1079, "ht": 183, "wt": 190, "ovr": 70, "pot": 76, "mid": 73, "three": 45, "in_def": 70, "blk": 40, "team": "GSW"},
    {"pick": 36, "first": "Kelly", "last": "McKinley", "pos": 2, "face": 1080, "ht": 201, "wt": 210, "ovr": 67, "pot": 73, "mid": 69, "three": 35, "in_def": 67, "blk": 45, "team": "POR"},
    {"pick": 37, "first": "Ben", "last": "Coleman", "pos": 3, "face": 1081, "ht": 206, "wt": 235, "ovr": 70, "pot": 77, "mid": 71, "three": 25, "in_def": 74, "blk": 71, "team": "CHI"},
    {"pick": 38, "first": "Charlie", "last": "Sitton", "pos": 2, "face": 1082, "ht": 203, "wt": 210, "ovr": 68, "pot": 74, "mid": 72, "three": 40, "in_def": 68, "blk": 48, "team": "DAL"},
    {"pick": 39, "first": "Danny", "last": "Young", "pos": 0, "face": 1083, "ht": 190, "wt": 175, "ovr": 71, "pot": 78, "mid": 73, "three": 52, "in_def": 73, "blk": 42, "team": "SEA"},
    {"pick": 40, "first": "Anthony", "last": "Teachey", "pos": 3, "face": 1084, "ht": 206, "wt": 210, "ovr": 68, "pot": 73, "mid": 68, "three": 25, "in_def": 72, "blk": 68, "team": "DAL"},
    {"pick": 41, "first": "Tom", "last": "Sluby", "pos": 1, "face": 1085, "ht": 193, "wt": 200, "ovr": 69, "pot": 74, "mid": 72, "three": 45, "in_def": 68, "blk": 45, "team": "DAL"},
    {"pick": 42, "first": "Willie", "last": "White", "pos": 1, "face": 1086, "ht": 190, "wt": 170, "ovr": 68, "pot": 73, "mid": 71, "three": 45, "in_def": 67, "blk": 40, "team": "DEN"},
    {"pick": 43, "first": "Greg", "last": "Wiltjer", "pos": 4, "face": 1087, "ht": 211, "wt": 240, "ovr": 69, "pot": 74, "mid": 66, "three": 25, "in_def": 73, "blk": 71, "team": "CHI"},
    {"pick": 44, "first": "Fred", "last": "Reynolds", "pos": 2, "face": 1088, "ht": 198, "wt": 200, "ovr": 67, "pot": 72, "mid": 68, "three": 30, "in_def": 66, "blk": 45, "team": "WAS"},
    {"pick": 45, "first": "Gary", "last": "Plummer", "pos": 3, "face": 1089, "ht": 206, "wt": 215, "ovr": 68, "pot": 73, "mid": 69, "three": 25, "in_def": 71, "blk": 67, "team": "GSW"},

    # 次轮神级遗珠与深度新秀 (Picks 46 - 60)
    {"pick": 46, "first": "Jerome", "last": "Kersey", "pos": 2, "face": 618, "ht": 201, "wt": 215, "ovr": 75, "pot": 88, "mid": 78, "three": 45, "in_def": 81, "blk": 68, "team": "POR"},
    {"pick": 47, "first": "Brian", "last": "Martin", "pos": 3, "face": 1090, "ht": 206, "wt": 210, "ovr": 67, "pot": 72, "mid": 67, "three": 25, "in_def": 70, "blk": 65, "team": "IND"},
    {"pick": 48, "first": "Jim", "last": "Petersen", "pos": 4, "face": 1091, "ht": 208, "wt": 235, "ovr": 71, "pot": 79, "mid": 71, "three": 25, "in_def": 76, "blk": 74, "team": "HOU"},
    {"pick": 49, "first": "Eric", "last": "Turner", "pos": 0, "face": 1092, "ht": 190, "wt": 180, "ovr": 67, "pot": 72, "mid": 70, "three": 40, "in_def": 66, "blk": 40, "team": "DET"},
    {"pick": 50, "first": "Carl", "last": "Henry", "pos": 1, "face": 1093, "ht": 198, "wt": 205, "ovr": 68, "pot": 73, "mid": 71, "three": 45, "in_def": 67, "blk": 45, "team": "SAC"},
    {"pick": 51, "first": "Dan", "last": "Trant", "pos": 0, "face": 1094, "ht": 188, "wt": 175, "ovr": 66, "pot": 71, "mid": 68, "three": 40, "in_def": 65, "blk": 38, "team": "BOS"},
    {"pick": 52, "first": "Vernon", "last": "Hawkins", "pos": 0, "face": 1095, "ht": 185, "wt": 170, "ovr": 66, "pot": 70, "mid": 67, "three": 40, "in_def": 64, "blk": 35, "team": "MIL"},
    {"pick": 53, "first": "Ricky", "last": "Ross", "pos": 1, "face": 1096, "ht": 198, "wt": 195, "ovr": 67, "pot": 71, "mid": 69, "three": 45, "in_def": 66, "blk": 42, "team": "WAS"},
    {"pick": 54, "first": "Michael", "last": "Revell", "pos": 2, "face": 1097, "ht": 201, "wt": 205, "ovr": 66, "pot": 70, "mid": 67, "three": 35, "in_def": 65, "blk": 45, "team": "CHI"},
    {"pick": 55, "first": "Ron", "last": "Cavenall", "pos": 4, "face": 1098, "ht": 216, "wt": 230, "ovr": 68, "pot": 73, "mid": 65, "three": 25, "in_def": 73, "blk": 73, "team": "NYK"},
    {"pick": 56, "first": "Dave", "last": "Lattin", "pos": 3, "face": 1099, "ht": 201, "wt": 225, "ovr": 67, "pot": 71, "mid": 68, "three": 25, "in_def": 71, "blk": 66, "team": "UTA"},
    {"pick": 57, "first": "Mark", "last": "Halsel", "pos": 3, "face": 1100, "ht": 203, "wt": 215, "ovr": 66, "pot": 70, "mid": 66, "three": 25, "in_def": 69, "blk": 64, "team": "CHI"},
    {"pick": 58, "first": "Greg", "last": "Hargrove", "pos": 0, "face": 1101, "ht": 188, "wt": 175, "ovr": 66, "pot": 70, "mid": 68, "three": 40, "in_def": 65, "blk": 36, "team": "DEN"},
    {"pick": 59, "first": "Mark", "last": "Waddell", "pos": 2, "face": 1102, "ht": 201, "wt": 210, "ovr": 65, "pot": 69, "mid": 66, "three": 30, "in_def": 64, "blk": 42, "team": "MIL"},
    {"pick": 60, "first": "Dan", "last": "Crosswhite", "pos": 4, "face": 1103, "ht": 213, "wt": 235, "ovr": 67, "pot": 71, "mid": 64, "three": 25, "in_def": 72, "blk": 70, "team": "BOS"}
]

if __name__ == "__main__":
    raise SystemExit(
        "Disabled legacy hand-authored ratings. Query verified historical rookies "
        "from player_pool.sqlite; keep generated rookies in unmatched slots. See docs/20 and docs/26."
    )
    out_dir = r"e:\games\NBA 2K22\Antigravity_GM_Engine\database\draft_classes"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "1984_draft_class.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(PLAYERS_1984, f, ensure_ascii=False, indent=2)
        
    print(f"[*] 成功生成 1984 届完整选秀名单！共 {len(PLAYERS_1984)} 名真实新秀。")
    print(f"[*] 保存路径: {out_file}")
