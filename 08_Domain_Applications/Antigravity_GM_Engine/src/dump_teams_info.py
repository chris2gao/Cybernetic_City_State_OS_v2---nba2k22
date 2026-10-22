# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from scanner import LeagueScanner
import config

mem = GameMemory()
scanner = LeagueScanner(mem)
teams = scanner.find_active_teams()

print(f"Total active teams: {len(teams)}")
for tid in sorted(teams.keys()):
    t = teams[tid]
    addr = t['address']
    pop = mem.read_uint32(addr + 0xF80)
    fan = mem.read_float(addr + 0xF7C)
    ticket = mem.read_float(addr + 0xF98)
    gate = mem.read_uint32(addr + 0xFD8)
    merch = mem.read_uint32(addr + 0xFDC)
    media = mem.read_uint32(addr + 0xFE4)
    payroll = mem.read_uint32(addr + 0xFF4)
    budget = mem.read_uint32(addr + 0x1014)
    staff_budget = mem.read_uint32(addr + 0x1018)
    cash = mem.read_uint32(addr + 0x1010)
    chem = mem.read_float(addr + 0xEC4)
    print(f"{t['abbreviation']:3} | {t['city']:12} {t['name']:14} | ID:{tid:2} | Addr:{hex(addr)} | Pop:{pop:10,} | Ticket:${ticket:6.2f} | Fan:{fan:4.2f} | Gate:${gate:10,} | Merch:${merch:9,} | Media:${media:9,} | Pay:${payroll:11,} | Budg:${budget:11,} | Staff:${staff_budget:9,} | Cash:${cash:10,} | Chem:{chem:4.1f}%")
