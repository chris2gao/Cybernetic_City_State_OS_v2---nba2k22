from pathlib import Path
runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment28';old='4edfc63ff5b3e5611481c0e69078bd232e168a8d';new='618255cc42d8a5c128120ed2ba904e827da343ea'
for p in (run/'increment28_work_unit.yml',dest/'IMPLEMENTATION.md',runtime/'finalize_increment28.py'):
    text=p.read_text(encoding='utf-8').replace(old,new).replace('224','225').replace('verification/','verification-repaired/')
    if p.name=='finalize_increment28.py':text=text.replace("dest/'worker-terminal.json'","dest/'retry-worker-terminal.json'").replace("dest/'worker-launch.json'","dest/'retry-worker-launch.json'")
    p.write_text(text,encoding='utf-8',newline='\n')
p=runtime/'audit_actual_finance.py';text=p.read_text(encoding='utf-8').replace("dest/'worker-result.json'","dest/'retry-worker-result.json'").replace("dest/'worker-terminal.json'","dest/'retry-worker-terminal.json'").replace('finance-refresh-01','finance-refresh-02')
text=text.replace("('finance-refresh-02','finance-metadata-01','finance-metadata-02')","('finance-refresh-01','finance-refresh-02','finance-metadata-01','finance-metadata-02','finance-dimensions-01')")
text=text.replace("'verify_finance_worker_terminal.ps1',Path(__file__).name)","'verify_finance_worker_terminal.ps1','read_finance_dimensions.py','start_finance_dimensions.ps1','run_finance_retry.py','start_finance_retry.ps1','verify_finance_retry_terminal.ps1','repair_increment28_evidence_refs.py',Path(__file__).name)")
p.write_text(text,encoding='utf-8',newline='\n')
p=dest/'IMPLEMENTATION.md';text=p.read_text(encoding='utf-8');text+='''

The first actual finance attempt stopped before ingestion because it compared
the full24-byte runtime name-dimension control block against static PE bytes.
A bounded diagnostic established unchanged extents25/18/7 and a runtime-initialized
word at+8 (value2 rather than static0). The repaired reader checks the one-dimensional
extent/rank whose meaning is evidenced, retains the full runtime control block,
and repeats it for stability. It does not assign semantics to other control words.
The original failed attempt is preserved in the source archive; the corrected
candidate was rechecked with225 tests and SQLite smoke before acquisition resumed.
''';p.write_text(text,encoding='utf-8',newline='\n')
