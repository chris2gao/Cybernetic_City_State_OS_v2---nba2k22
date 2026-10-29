"""Verify ancestry, exact rehearsed tree and domain preservation using Git objects."""
import argparse
import json
from pathlib import Path
import subprocess

BASE = '7742568ac677b3c16079887463f05e81cb1191ed'
CORE = 'e075cdf288a765b7bfd2f4891c8f384404da16e1'
PREVIEW_TREE = 'b42d10b81aec3fd4439d183e857f7e2877aca4ca'
RUN = '01_os/07_content/_runs/run-20261029-nba-core-prms-sync-issue-11-001/'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', required=True)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    git = lambda *a: subprocess.check_output(['git', *a], cwd=root)
    head = git('rev-parse', 'HEAD').decode().strip()
    for ancestor in (BASE, CORE):
        subprocess.run(['git','merge-base','--is-ancestor',ancestor,head], cwd=root, check=True)
    def entries(ref):
        return {item.split(b'\t',1)[1].decode('utf-8'): item.split(b'\t',1)[0].decode()
            for item in git('ls-tree','-rz',ref).split(b'\0') if item}
    old, current, preview, source = (entries(ref) for ref in (BASE, head, PREVIEW_TREE, CORE))
    # Exact merged tree except this task's new domain-owned run artifacts.
    assert {p:v for p,v in current.items() if not p.startswith(RUN)} == preview
    import yaml
    manifest = yaml.safe_load(git('show',CORE+':CORE_MANIFEST.yml'))
    protected_prefixes = manifest['domain_owned_paths'] + ['01_os/07_content/']
    protected = [p for p in old if any(p.startswith(prefix) for prefix in protected_prefixes)]
    assert all(current.get(p) == old[p] for p in protected), 'existing domain content changed or deleted'
    assert all(p in current for p in old), 'unexpected tracked deletion'
    prefixes = ('01_os/06_execution/boot/context_management/prms/',
                '01_os/03_mechanisms/context_management/prms/')
    prms = [p for p in source if p.startswith(prefixes)]
    prms += ['01_os/02_boot/context_management/启动清单_v1.yml','01_os/05_registry/prms_v1.yml']
    assert all(current.get(p) == source[p] for p in prms), 'PRMS source drift'
    # Git ancestry, not copying, is the integration proof. Existing domain 09
    # is unchanged; lack of a formal G2 is not silently upgraded by this merge.
    result = {'status':'VERIFIED_SAFE_CORE_INHERITANCE', 'candidate':head,
        'nba_base':BASE, 'core_source':CORE, 'merge_base':git('merge-base',BASE,CORE).decode().strip(),
        'rehearsed_merge_tree':PREVIEW_TREE, 'protected_existing_domain_files':len(protected),
        'changed_existing_domain_files':0, 'deleted_existing_files':0, 'exact_prms_source_files':len(prms),
        'other_domains_updated':False, 'formal_G2_publication_performed':False}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
