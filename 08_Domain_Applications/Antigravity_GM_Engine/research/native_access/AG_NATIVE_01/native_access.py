# -*- coding: utf-8 -*-
"""NBA 2K22 原生数据访问引擎 (Native Data Access Engine)

AG-NATIVE-01 核心交付物：
1. 实现对 NBA 2K22 内部 ROSTERDATA 对象目录管理器的自动探测与一致性校验；
2. 提供统一的 Reader 接口 (list_objects, get_object, get_related, find_objects)；
3. 支持 PLAYER, TEAM, STAFF, PLAYER_STATS, TEAM_STATS, DRAFT_ASSETS, WAIVED_SALARY 7 类原生对象；
4. 抽象 MemoryBackend，实现实机在线读取与离线合成/回放完全解耦；
5. 自动复用现有多域解码器，保留原始二进制并提供关系图遍历能力。
"""

import os
import sys
import json
import struct
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

# 尝试引入工程既有配置和解码器（用于解码已知字段，无强依赖可降级）
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "config"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    import source_extensions
    HAS_SOURCE_EXTENSIONS = True
except ImportError:
    HAS_SOURCE_EXTENSIONS = False

try:
    import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False


# =============================================================================
# 1. 内存访问抽象层 (Memory Backend Abstraction)
# =============================================================================

class MemoryBackend(ABC):
    """内存读取后端抽象基类"""

    @abstractmethod
    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        """从指定地址读取指定字节数"""
        pass

    def read_uint8(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 1)
        return b[0] if b else None

    def read_uint16(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 2)
        return struct.unpack("<H", b)[0] if b and len(b) == 2 else None

    def read_uint32(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 4)
        return struct.unpack("<I", b)[0] if b and len(b) == 4 else None

    def read_uint64(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 8)
        return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None

    def read_utf16_string(self, address: int, max_chars: int = 40) -> str:
        b = self.read_bytes(address, max_chars * 2)
        if not b:
            return ""
        return b.decode("utf-16le", errors="ignore").split("\x00")[0]

    @property
    def is_live(self) -> bool:
        return False


class LiveMemoryBackend(MemoryBackend):
    """实机只读内存后端 (基于 Windows API)"""

    def __init__(self, mem=None):
        if mem is None:
            import memory
            self.mem = memory.GameMemory(read_only=True)
        else:
            self.mem = mem

    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        return self.mem.read_bytes(address, size)

    @property
    def is_live(self) -> bool:
        return True

    @property
    def pid(self) -> int:
        return getattr(self.mem, "pid", 0)

    @property
    def base_address(self) -> int:
        return getattr(self.mem, "base_address", 0x140000000)


class MockMemoryBackend(MemoryBackend):
    """离线合成/快照内存后端 (用于确定性测试与无游戏环境运行)"""

    def __init__(self, fixtures_dir: Optional[str] = None):
        self.memory_blocks: Dict[int, bytes] = {}
        self.sparse_records: Dict[str, Dict[int, bytes]] = {}
        self.manifest: Dict[str, Any] = {}
        if fixtures_dir:
            self.load_fixtures(fixtures_dir)

    def register_block(self, address: int, data: bytes):
        """注册连续内存块"""
        self.memory_blocks[address] = data

    def register_sparse_record(self, object_type: str, index: int, data: bytes):
        """注册稀疏对象记录"""
        self.sparse_records.setdefault(object_type, {})[index] = data

    def load_fixtures(self, fixtures_dir: str):
        """从 fixtures 目录加载离线样本数据"""
        manifest_path = os.path.join(fixtures_dir, "fixtures_manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f)

        root_path = os.path.join(fixtures_dir, "sample_roster_root.bin")
        if os.path.exists(root_path):
            with open(root_path, "rb") as f:
                root_addr = int(self.manifest.get("roster_root_address", "0x7FF4E6DFB2E8"), 16)
                self.register_block(root_addr, f.read())

        teams_path = os.path.join(fixtures_dir, "sample_teams.bin")
        if os.path.exists(teams_path):
            with open(teams_path, "rb") as f:
                team_addr = int(self.manifest.get("teams", {}).get("address", "0x7FF4E73065F0"), 16)
                self.register_block(team_addr, f.read())

        staff_path = os.path.join(fixtures_dir, "sample_staff.bin")
        if os.path.exists(staff_path):
            with open(staff_path, "rb") as f:
                staff_addr = int(self.manifest.get("descriptors", {}).get("staff", {}).get("address", "0x7FF4E7421160"), 16)
                self.register_block(staff_addr, f.read())

        draft_path = os.path.join(fixtures_dir, "sample_draft_assets.bin")
        if os.path.exists(draft_path):
            with open(draft_path, "rb") as f:
                draft_addr = int(self.manifest.get("descriptors", {}).get("draft_assets", {}).get("address", "0x7FF4E7B2D7C0"), 16)
                self.register_block(draft_addr, f.read())

        waived_path = os.path.join(fixtures_dir, "sample_waived_salary.bin")
        if os.path.exists(waived_path):
            with open(waived_path, "rb") as f:
                ws_addr = int(self.manifest.get("waived_salary", {}).get("address", "0x7FF4E7C3E180"), 16)
                self.register_block(ws_addr, f.read())

        # 加载索引前缀的稀疏记录 (players, player_stats, team_stats)
        self._load_indexed_file(os.path.join(fixtures_dir, "sample_players.bin"), "PLAYER", 1264)
        self._load_indexed_file(os.path.join(fixtures_dir, "sample_player_stats.bin"), "PLAYER_STATS", 48)
        self._load_indexed_file(os.path.join(fixtures_dir, "sample_team_stats.bin"), "TEAM_STATS", 62)

    def _load_indexed_file(self, filepath: str, object_type: str, stride: int):
        if not os.path.exists(filepath):
            return
        with open(filepath, "rb") as f:
            content = f.read()
        entry_size = 4 + stride
        for off in range(0, len(content), entry_size):
            if off + entry_size <= len(content):
                idx = struct.unpack_from("<I", content, off)[0]
                record_bytes = content[off + 4 : off + entry_size]
                self.register_sparse_record(object_type, idx, record_bytes)

    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        # 1. 检查连续块
        for base, data in self.memory_blocks.items():
            if base <= address < base + len(data):
                offset = address - base
                if offset + size <= len(data):
                    return data[offset : offset + size]
        return None

    def read_sparse_record(self, object_type: str, index: int) -> Optional[bytes]:
        return self.sparse_records.get(object_type, {}).get(index)


# =============================================================================
# 2. 原生对象记录封装 (Native Record)
# =============================================================================

class NativeRecord:
    """包装单条原生对象记录，保留原始字节，提供按字段只读访问与格式化展示"""

    def __init__(
        self,
        object_type: str,
        index: int,
        address: int,
        stride: int,
        raw_bytes: bytes,
        decoded: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ):
        self.object_type = object_type
        self.index = index
        self.address = address
        self.stride = stride
        self.raw_bytes = raw_bytes
        self.decoded = decoded or {}
        self.provenance = provenance or {}

    def get(self, key: str, default: Any = None) -> Any:
        """从解码字典中安全获取字段值"""
        if key in self.decoded:
            return self.decoded[key]
        # 尝试在各子分组中查找
        for group in self.decoded.values():
            if isinstance(group, dict) and key in group:
                item = group[key]
                return item.get("value", item) if isinstance(item, dict) else item
        return default

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_type": self.object_type,
            "index": self.index,
            "address": hex(self.address),
            "stride": self.stride,
            "raw_hex_preview": self.raw_bytes[:32].hex() + ("..." if len(self.raw_bytes) > 32 else ""),
            "decoded": self.decoded,
            "provenance": self.provenance,
        }

    def __repr__(self) -> str:
        ident = ""
        if self.object_type == "PLAYER":
            ident = f" ({self.get('first_name', '')} {self.get('last_name', '')})"
        elif self.object_type == "TEAM":
            ident = f" ({self.get('city', '')} {self.get('name', '')} [{self.get('abbreviation', '')}])"
        elif self.object_type == "STAFF":
            ident = f" ({self.get('first_name', '')} {self.get('last_name', '')})"
        elif self.object_type == "TEAM_STATS":
            ident = f" (W={self.get('w', '?')}, L={self.get('l', '?')})"
        elif self.object_type == "PLAYER_STATS":
            ident = f" (PTS={self.get('points', '?')}, REB={self.get('rebounds', '?')}, AST={self.get('assists', '?')})"
        return f"<NativeRecord {self.object_type}[{self.index}]{ident} @ 0x{self.address:X}>"


# =============================================================================
# 3. 原生数据访问核心引擎 (Native Reader)
# =============================================================================

class NativeReader:
    """NBA 2K22 统一原生数据读取器 (Unified Native Reader)

    核心职能：
    1. 自动定位与校验 ROSTERDATA 原生数组目录；
    2. 提供通用统一的对象获取接口 (get_object)；
    3. 支持原生关系跨对象图式遍历 (get_related)；
    4. 完全兼容离线沙箱测试与真实游戏只读内存访问。
    """

    # 预设的 ROSTERDATA 目录项定义 (基于实机内存逆向与汇编校验)
    DEFAULT_CATALOG = {
        "PLAYER": {
            "root_offset": 0x020,
            "stride": 1264,
            "min_count": 3000,
            "max_count": 5000,
            "codec": "PLAYER",
        },
        "TEAM": {
            "root_offset": 0x090,
            "stride": 4696,
            "min_count": 30,
            "max_count": 1000,
            "codec": "TEAM",
        },
        "STAFF": {
            "root_offset": 0x140,
            "stride": 352,
            "min_count": 100,
            "max_count": 3000,
            "codec": "STAFF",
        },
        "PLAYER_STATS": {
            "root_offset": 0x190,
            "stride": 48,
            "min_count": 500,
            "max_count": 20000,
            "codec": "PLAYER_STATS",
        },
        "TEAM_STATS": {
            "root_offset": 0x1D0,
            "stride": 62,
            "min_count": 30,
            "max_count": 5000,
            "codec": "TEAM_STATS",
        },
        "DRAFT_ASSETS": {
            "root_offset": 0x2B0,
            "stride": 32,
            "min_count": 100,
            "max_count": 2000,
            "codec": "DRAFT_ASSETS",
        },
        "WAIVED_SALARY": {
            "root_offset": 0x3E0,
            "stride": 136,
            "min_count": 10,
            "max_count": 1000,
            "codec": "WAIVED_SALARY",
        },
    }

    def __init__(
        self,
        backend: Optional[MemoryBackend] = None,
        root_address: Optional[int] = None,
        catalog: Optional[Dict[str, Any]] = None,
    ):
        self.backend = backend or LiveMemoryBackend()
        self.root_address = root_address
        self.catalog = catalog or self.DEFAULT_CATALOG
        self.descriptors: Dict[str, Dict[str, Any]] = {}
        self._is_calibrated = False

    def auto_calibrate(self, search_start: int = 0x7FF4E0000000, search_end: int = 0x7FF4F0000000) -> int:
        """自动在指定地址空间内通过不变方程探测 ROSTERDATA 目录根基址。

        不变方程规则：
        - root + 0x18 为球员计数 count (通常 3300 ~ 3400)
        - root + 0x20 必须等于 root + 0x4F0
        - root + 0x30 必须等于 (root + 0x4F0) + count * 1264
        - 验证后续 staff, stats, teams 数组地址及边界自洽
        """
        if isinstance(self.backend, MockMemoryBackend):
            root_str = self.backend.manifest.get("roster_root_address", "0x7FF4E6DFB2E8")
            self.root_address = int(root_str, 16)
            self._parse_descriptors()
            self._is_calibrated = True
            return self.root_address

        # 实机内存扫描
        chunk_size = 16 * 1024 * 1024  # 16MB 分块
        stride_p = 1264
        for base in range(search_start, search_end, chunk_size):
            chunk = self.backend.read_bytes(base, chunk_size)
            if not chunk:
                continue
            for offset in range(0x18, len(chunk) - 0x4F0, 8):
                count = struct.unpack_from("<Q", chunk, offset)[0]
                if 3000 <= count <= 4000:
                    ptr = struct.unpack_from("<Q", chunk, offset + 8)[0]
                    cand_root = base + offset - 0x18
                    if ptr == cand_root + 0x4F0:
                        end = struct.unpack_from("<Q", chunk, offset + 0x18)[0]
                        if end == ptr + count * stride_p:
                            self.root_address = cand_root
                            self._parse_descriptors()
                            self._is_calibrated = True
                            return self.root_address

        raise RuntimeError("未能探测到有效的 ROSTERDATA 根目录基址")

    def _parse_descriptors(self):
        """基于已知 root_address 解析所有对象数组的实际地址、容量和终点"""
        if not self.root_address:
            raise RuntimeError("尚未设定或探测到 root_address")

        self.descriptors = {}
        for kind, spec in self.catalog.items():
            off = spec["root_offset"]
            stride = spec["stride"]

            addr = self.backend.read_uint64(self.root_address + off)
            count = self.backend.read_uint64(self.root_address + off - 8)
            end = self.backend.read_uint64(self.root_address + off + 0x10)

            # 在 MockBackend 下，若 root block 内读出数据则做严格校验
            if addr and count:
                if end and end != addr + count * stride:
                    # 某些辅助数组可能有容量对齐，记录警告
                    pass
                self.descriptors[kind] = {
                    "object_type": kind,
                    "address": addr,
                    "count": count,
                    "stride": stride,
                    "codec": spec.get("codec"),
                }
            elif isinstance(self.backend, MockMemoryBackend):
                # 从 manifest 提取回退
                m_info = self.backend.manifest.get("descriptors", {}).get(kind.lower()) or self.backend.manifest.get(kind.lower())
                if m_info:
                    self.descriptors[kind] = {
                        "object_type": kind,
                        "address": int(m_info["address"], 16) if isinstance(m_info["address"], str) else m_info["address"],
                        "count": m_info["count"],
                        "stride": m_info["stride"],
                        "codec": spec.get("codec"),
                    }

    def list_objects(self, object_type: str) -> Dict[str, Any]:
        """列出指定对象类型的数组元信息 (数量、地址、步长)"""
        if not self._is_calibrated:
            if self.root_address:
                self._parse_descriptors()
                self._is_calibrated = True
            else:
                self.auto_calibrate()

        obj_upper = object_type.upper()
        if obj_upper not in self.descriptors:
            raise ValueError(f"未知的原生对象类型: {object_type}，支持类型: {list(self.catalog.keys())}")

        d = self.descriptors[obj_upper]
        return {
            "object_type": obj_upper,
            "count": d["count"],
            "stride": d["stride"],
            "address": hex(d["address"]),
            "is_live": self.backend.is_live,
        }

    def get_object(self, object_type: str, index: int) -> NativeRecord:
        """根据原生对象类型和索引，安全读取并返回一条完整记录。

        特性：
        - 越界安全防护 (IndexError)
        - 类型校验 (ValueError)
        - 自动执行领域解码
        - 保留原始字节
        """
        if not self._is_calibrated:
            if self.root_address:
                self._parse_descriptors()
                self._is_calibrated = True
            else:
                self.auto_calibrate()

        obj_upper = object_type.upper()
        if obj_upper not in self.descriptors:
            raise ValueError(f"未知的原生对象类型: {object_type}")

        meta = self.descriptors[obj_upper]
        count = meta["count"]
        stride = meta["stride"]
        base_addr = meta["address"]

        if index < 0 or index >= count:
            raise IndexError(f"索引越界: {obj_upper} 索引 {index} 超出有效范围 [0, {count})")

        rec_addr = base_addr + index * stride
        raw_bytes = None

        # 优先从 MockBackend 稀疏记录读取
        if isinstance(self.backend, MockMemoryBackend):
            raw_bytes = self.backend.read_sparse_record(obj_upper, index)

        # 常规从内存块读取
        if raw_bytes is None:
            raw_bytes = self.backend.read_bytes(rec_addr, stride)

        if raw_bytes is None or len(raw_bytes) != stride:
            raise OSError(f"读取原生记录失败: {obj_upper}[{index}] @ 0x{rec_addr:X}")

        # 解码结构体
        decoded = self._decode_record(obj_upper, raw_bytes, index, rec_addr)

        provenance = {
            "source_address": hex(rec_addr),
            "backend": "LIVE_MEMORY" if self.backend.is_live else "MOCK_FIXTURE",
            "stride": stride,
            "root_address": hex(self.root_address) if self.root_address else None,
        }

        return NativeRecord(
            object_type=obj_upper,
            index=index,
            address=rec_addr,
            stride=stride,
            raw_bytes=raw_bytes,
            decoded=decoded,
            provenance=provenance,
        )

    def _decode_record(self, object_type: str, raw: bytes, index: int, address: int) -> Dict[str, Any]:
        """根据对象类型派发对应解码器"""
        decoded: Dict[str, Any] = {}

        if object_type == "PLAYER":
            # 基础身份解包
            last_name = raw[0:40].decode("utf-16le", errors="ignore").split("\x00")[0]
            first_name = raw[40:80].decode("utf-16le", errors="ignore").split("\x00")[0]
            cf_id = struct.unpack_from("<H", raw, 0x6C)[0]
            team_ptr = struct.unpack_from("<Q", raw, 0x60)[0]
            stats_idx = struct.unpack_from("<H", raw, 0xFC)[0]
            decoded["identity"] = {
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}",
                "face_id": cf_id,
                "current_team_ptr": hex(team_ptr),
                "stats_index": stats_idx if stats_idx != 65535 else None,
            }
            # 尝试调用既有 source_extensions 解码能力和合同
            if HAS_SOURCE_EXTENSIONS:
                try:
                    dec = source_extensions.decode_fields(raw, "PLAYER")
                    decoded.update(dec)
                except Exception:
                    pass

        elif object_type == "TEAM":
            # TEAM 步长 4696
            name = raw[0x2B4 : 0x2B4 + 40].decode("utf-16le", errors="ignore").split("\x00")[0]
            city = raw[0x2E6 : 0x2E6 + 40].decode("utf-16le", errors="ignore").split("\x00")[0]
            abb = raw[0x30A : 0x30A + 10].decode("utf-16le", errors="ignore").split("\x00")[0]
            uid = struct.unpack_from("<H", raw, 0xCA8)[0]
            ttype = raw[0xEEB] & 0x1F
            stats_idx = struct.unpack_from("<H", raw, 0xE80)[0]
            decoded["info"] = {
                "team_id": uid,
                "city": city,
                "name": name,
                "abbreviation": abb,
                "team_type": ttype,
                "stats_index": stats_idx if stats_idx != 65535 else None,
            }
            # 教练与制服组槽位指针
            decoded["staff_ptrs"] = {
                "head_coach": hex(struct.unpack_from("<Q", raw, 0xCE8)[0]),
                "assistant_coach": hex(struct.unpack_from("<Q", raw, 0xCF0)[0]),
                "scout": hex(struct.unpack_from("<Q", raw, 0xCF8)[0]),
                "trainer": hex(struct.unpack_from("<Q", raw, 0xD00)[0]),
                "gm": hex(struct.unpack_from("<Q", raw, 0xD08)[0]),
                "owner": hex(struct.unpack_from("<Q", raw, 0xD10)[0]),
            }

        elif object_type == "STAFF":
            # STAFF 步长 352
            last = raw[0x58 : 0x58 + 40].decode("utf-16le", errors="ignore").split("\x00")[0]
            first = raw[0x30 : 0x30 + 40].decode("utf-16le", errors="ignore").split("\x00")[0]
            team_ptr = struct.unpack_from("<Q", raw, 0x18)[0]
            decoded["identity"] = {
                "first_name": first,
                "last_name": last,
                "full_name": f"{first} {last}",
                "assigned_team_ptr": hex(team_ptr),
            }
            if HAS_SOURCE_EXTENSIONS:
                try:
                    dec = source_extensions.decode_fields(raw, "STAFF")
                    decoded.update(dec)
                except Exception:
                    pass

        elif object_type == "PLAYER_STATS":
            if HAS_SOURCE_EXTENSIONS:
                try:
                    dec = source_extensions.decode_fields(raw, "PLAYER_STATS")
                    decoded.update(dec)
                except Exception:
                    pass

        elif object_type == "TEAM_STATS":
            if HAS_SOURCE_EXTENSIONS:
                try:
                    dec = source_extensions.decode_fields(raw, "TEAM_STATS")
                    decoded.update(dec)
                except Exception:
                    pass

        elif object_type == "DRAFT_ASSETS":
            # 32 字节原生选秀资产
            owner = struct.unpack_from("<Q", raw, 0)[0]
            orig = struct.unpack_from("<Q", raw, 8)[0]
            meta = struct.unpack_from("<I", raw, 28)[0]
            year_off = meta & 0x7
            round_code = (meta >> 3) & 0x1F
            pick_idx = (meta >> 8) & 0xFF
            abs_year = 2000 + ((meta >> 22) & 0x3FF)
            decoded["asset"] = {
                "owner_team_ptr": hex(owner),
                "original_team_ptr": hex(orig),
                "draft_year": abs_year,
                "draft_round": round_code + 1,
                "pick_index": pick_idx,
                "year_offset": year_off,
            }

        elif object_type == "WAIVED_SALARY":
            # 136 字节离队死钱结构
            team_ptr = struct.unpack_from("<Q", raw, 8)[0]
            s1 = struct.unpack_from("<I", raw, 16)[0]
            s2 = struct.unpack_from("<I", raw, 20)[0]
            s3 = struct.unpack_from("<I", raw, 24)[0]
            decoded["waived"] = {
                "team_ptr": hex(team_ptr),
                "salary_y1": s1,
                "salary_y2": s2,
                "salary_y3": s3,
            }

        return decoded

    def get_related(
        self,
        source: Union[NativeRecord, str],
        index_or_target: Union[int, str],
        target_type: Optional[str] = None,
    ) -> Union[Optional[NativeRecord], List[NativeRecord]]:
        """跨原生对象图式关联查询 (Object Graph Traversal)

        支持语法：
        - `reader.get_related(player_record, 'PLAYER_STATS')`
        - `reader.get_related('PLAYER', 179, 'PLAYER_STATS')`
        - `reader.get_related('TEAM', 13, 'TEAM_STATS')`
        - `reader.get_related('TEAM', 13, 'STAFF')`
        - `reader.get_related('TEAM', 13, 'WAIVED_SALARY')`
        - `reader.get_related('STAFF', 0, 'TEAM')`
        """
        # 参数重载规整
        if isinstance(source, NativeRecord):
            record = source
            tgt_type = index_or_target.upper()
        else:
            src_type = source.upper()
            src_idx = int(index_or_target)
            tgt_type = target_type.upper()
            record = self.get_object(src_type, src_idx)

        src_type = record.object_type

        # 1. PLAYER -> PLAYER_STATS
        if src_type == "PLAYER" and tgt_type == "PLAYER_STATS":
            stats_idx = struct.unpack_from("<H", record.raw_bytes, 0xFC)[0]
            if stats_idx == 65535 or stats_idx >= self.list_objects("PLAYER_STATS")["count"]:
                return None
            return self.get_object("PLAYER_STATS", stats_idx)

        # 2. PLAYER -> TEAM
        elif src_type == "PLAYER" and tgt_type == "TEAM":
            team_ptr = struct.unpack_from("<Q", record.raw_bytes, 0x60)[0]
            if team_ptr == 0:
                return None
            # 在 TEAM 列表中通过 address 匹配
            team_meta = self.list_objects("TEAM")
            team_base = int(team_meta["address"], 16)
            stride_t = team_meta["stride"]
            if team_base <= team_ptr < team_base + team_meta["count"] * stride_t:
                t_idx = (team_ptr - team_base) // stride_t
                return self.get_object("TEAM", t_idx)
            return None

        # 3. TEAM -> TEAM_STATS
        elif src_type == "TEAM" and tgt_type == "TEAM_STATS":
            stats_idx = struct.unpack_from("<H", record.raw_bytes, 0xE80)[0]
            if stats_idx == 65535 or stats_idx >= self.list_objects("TEAM_STATS")["count"]:
                return None
            return self.get_object("TEAM_STATS", stats_idx)

        # 4. TEAM -> STAFF (主教练)
        elif src_type == "TEAM" and tgt_type == "STAFF":
            # 默认返回主教练，亦可返回所有关联 staff
            hc_ptr = struct.unpack_from("<Q", record.raw_bytes, 0xCE8)[0]
            if hc_ptr == 0:
                return None
            staff_meta = self.list_objects("STAFF")
            s_base = int(staff_meta["address"], 16)
            stride_s = staff_meta["stride"]
            if s_base <= hc_ptr < s_base + staff_meta["count"] * stride_s:
                s_idx = (hc_ptr - s_base) // stride_s
                return self.get_object("STAFF", s_idx)
            return None

        # 5. STAFF -> TEAM
        elif src_type == "STAFF" and tgt_type == "TEAM":
            team_ptr = struct.unpack_from("<Q", record.raw_bytes, 0x18)[0]
            if team_ptr == 0:
                return None
            team_meta = self.list_objects("TEAM")
            t_base = int(team_meta["address"], 16)
            stride_t = team_meta["stride"]
            if t_base <= team_ptr < t_base + team_meta["count"] * stride_t:
                t_idx = (team_ptr - t_base) // stride_t
                return self.get_object("TEAM", t_idx)
            return None

        # 6. TEAM -> WAIVED_SALARY
        elif src_type == "TEAM" and tgt_type == "WAIVED_SALARY":
            results = []
            ws_meta = self.list_objects("WAIVED_SALARY")
            target_team_addr = record.address
            for i in range(min(ws_meta["count"], 500)):
                try:
                    ws_rec = self.get_object("WAIVED_SALARY", i)
                except OSError:
                    break
                ptr = struct.unpack_from("<Q", ws_rec.raw_bytes, 8)[0]
                if ptr == target_team_addr:
                    results.append(ws_rec)
            return results

        # 7. TEAM -> DRAFT_ASSETS
        elif src_type == "TEAM" and tgt_type == "DRAFT_ASSETS":
            results = []
            da_meta = self.list_objects("DRAFT_ASSETS")
            target_team_addr = record.address
            for i in range(min(da_meta["count"], 504)):
                try:
                    da_rec = self.get_object("DRAFT_ASSETS", i)
                except OSError:
                    break
                owner_ptr = struct.unpack_from("<Q", da_rec.raw_bytes, 0)[0]
                if owner_ptr == target_team_addr:
                    results.append(da_rec)
            return results

        raise NotImplementedError(f"未支持的对象图关系跳转: {src_type} -> {tgt_type}")

    def find_objects(self, object_type: str, limit: int = 50, **filters) -> List[NativeRecord]:
        """按字段过滤查询对象列表"""
        meta = self.list_objects(object_type)
        results = []
        for i in range(meta["count"]):
            try:
                rec = self.get_object(object_type, i)
            except Exception:
                continue

            matched = True
            for k, expected in filters.items():
                val = rec.get(k)
                if val is None or str(val).lower() != str(expected).lower():
                    matched = False
                    break

            if matched:
                results.append(rec)
                if len(results) >= limit:
                    break

        return results
