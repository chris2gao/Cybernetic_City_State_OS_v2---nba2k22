import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from native_getter_catalog import NativeGetterCatalog

def test_getter_catalog_lookup():
    getter = NativeGetterCatalog.get("player.by_id")
    assert getter is not None
    assert getter.rva == "0xf3fa80"
    assert getter.category == "PLAYER"
    
    playbook_getter = NativeGetterCatalog.get("playbook.get_count")
    assert playbook_getter is not None
    assert playbook_getter.rva == "0x149ae80"
    assert playbook_getter.field_offset == "+0x7fc"

def test_getter_categories():
    player_getters = NativeGetterCatalog.list_by_category("PLAYER")
    assert len(player_getters) == 8
    
    coach_getters = NativeGetterCatalog.list_by_category("COACH")
    assert len(coach_getters) == 5
    
    summary = NativeGetterCatalog.get_summary_dict()
    assert len(summary) >= 18
