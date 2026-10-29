"""Explicit local Human-relay export/receive/ack verification. Never opens chats."""
import argparse
import json
from pathlib import Path
import sys

from source import GitSource, PRMSError, canonical
from state import LocalGitState, WriterGate
from handoff import export_handoff, receiver_request, receive_handoff, verify_receiver_ack


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_new(path, value):
    # Existing files, including any active state/receipt, are never overwritten.
    with Path(path).open('xb') as stream:
        stream.write(canonical(value) + b'\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['export', 'receive', 'verify-ack'])
    parser.add_argument('--core-root', required=True)
    parser.add_argument('--core-commit', required=True)
    parser.add_argument('--core-repository', required=True)
    parser.add_argument('--state-root', required=True)
    parser.add_argument('--state-ref', default='refs/heads/prms-state')
    parser.add_argument('--plan', required=True)
    parser.add_argument('--choice', required=True)
    parser.add_argument('--history-choice', required=True)
    parser.add_argument('--package')
    parser.add_argument('--handoff-id')
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--receiver-request', required=True)
    parser.add_argument('--receiver-session')
    parser.add_argument('--max-bundle-bytes', type=int, default=4_000_000)
    parser.add_argument('--ack')
    args = parser.parse_args(argv)
    try:
        source = GitSource(args.core_root, args.core_commit, args.core_repository)
        gate = WriterGate(LocalGitState(args.state_root, args.state_ref))
        shared = dict(core_plan=load(args.plan), core_choice=load(args.choice), history_choice=load(args.history_choice))
        if args.command == 'export':
            if not args.package or not args.handoff_id:
                raise PRMSError('REJECTED', 'export requires package and handoff ID')
            if Path(args.bundle).resolve() == Path(args.receiver_request).resolve() or any(
                    Path(path).exists() for path in (args.bundle, args.receiver_request)):
                raise PRMSError('REJECTED', 'export requires two distinct new output files')
            bundle = export_handoff(gate, source, load(args.package), handoff_id=args.handoff_id, **shared)
            if len(canonical(bundle)) > args.max_bundle_bytes:
                raise PRMSError('CONTEXT_BUDGET_INSUFFICIENT', 'export wire budget exceeded')
            write_new(args.bundle, bundle)
            write_new(args.receiver_request, receiver_request(bundle))
            result = {'status': 'EXPORTED_FOR_HUMAN_RELAY', 'bundle_digest': bundle['bundle_digest'],
                      'automatic_injection': False, 'context_status': bundle['package']['status']}
        else:
            if not args.ack or not args.receiver_session:
                raise PRMSError('REJECTED', 'receiver requires ack path and explicit current session')
            bundle = load(args.bundle)
            receiver = dict(expected_request=load(args.receiver_request), receiver_session_id=args.receiver_session,
                            max_bundle_bytes=args.max_bundle_bytes, **shared)
            if args.command == 'receive':
                result = receive_handoff(gate, source, bundle, **receiver)
                write_new(args.ack, result)
            else:
                result = verify_receiver_ack(gate, source, bundle, load(args.ack), **receiver)
        print(json.dumps({k: result[k] for k in ('status', 'context_status', 'automatic_injection') if k in result}))
        return 0
    except (PRMSError, KeyError, ValueError, TypeError, OSError) as exc:
        print(json.dumps({'status': getattr(exc, 'status', 'REJECTED'), 'detail': str(exc)}, ensure_ascii=True))
        return 2


if __name__ == '__main__':
    sys.exit(main())
