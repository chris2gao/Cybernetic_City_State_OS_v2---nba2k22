"""Real installed CLI regression; no mocks, installation or global state writes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / '01_os/_runs/run-012-check-jsonschema安装接入验证/07_测试执行/fixtures'
WRAPPER = ROOT / '01_os/06_execution/tools/check_jsonschema/invoke.ps1'
PWSH = 'C:/Program Files/PowerShell/7/pwsh.exe'
SCHEMA = FIXTURES / 'run_manifest.schema.json'
CLI = shutil.which('check-jsonschema')
assert CLI, 'TOOL_UNAVAILABLE: check-jsonschema'
records = []


def invoke(schema, instance, *options, expected):
    command = [PWSH, '-NoLogo', '-NoProfile', '-NonInteractive', '-File', str(WRAPPER),
               '-SchemaPath', str(schema), '-InstancePath', str(instance), *options]
    started = time.time_ns()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
    stdout, stderr = result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    assert result.returncode == expected, (command, result.returncode, stdout, stderr)
    records.append({'command': command, 'exit': result.returncode, 'start_ns': started,
                    'elapsed_seconds': (time.time_ns() - started) / 1e9,
                    'stdout': stdout, 'stderr': stderr})
    return result


with tempfile.TemporaryDirectory(prefix='core-c1-') as directory:
    temp = Path(directory)
    unicode_dir = temp / '含 中文与空格'
    unicode_dir.mkdir()
    unicode_bad = unicode_dir / '非法 实例.yaml'
    english_bad = temp / 'invalid_enum.yaml'
    for target in [unicode_bad, english_bad]:
        shutil.copyfile(FIXTURES / 'invalid_enum.yaml', target)
    inputs = [unicode_bad, FIXTURES / 'valid.yaml', english_bad, FIXTURES / 'valid.json']
    for instance, expected in zip(inputs, [1, 0, 1, 0]):
        result = invoke(SCHEMA, instance, expected=expected)
        reference = subprocess.run([CLI, '--schemafile', str(SCHEMA), str(instance)],
                                   env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
                                   capture_output=True, timeout=30)
        assert (result.returncode, result.stdout, result.stderr) == (
            reference.returncode, reference.stdout, reference.stderr), 'CLI channel/exit changed'
        if expected:
            output = result.stdout.decode('utf-8')
            assert str(instance) in output and '\ufffd' not in output
            assert "$.status: 'done' is not one of ['planned', 'running', 'completed', 'blocked']" in output

    invalid_schema = unicode_dir / '非法 Schema.json'
    invalid_schema.write_text('{"type": "not-a-schema-type"}', encoding='utf-8')
    reference = subprocess.run([CLI, '--schemafile', str(invalid_schema), str(unicode_bad)],
                               env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
                               capture_output=True, timeout=30)
    assert reference.returncode != 0 and reference.stderr, 'Expected real CLI schema-error stderr'
    result = invoke(invalid_schema, unicode_bad, expected=reference.returncode)
    assert (result.stdout, result.stderr) == (reference.stdout, reference.stderr), 'Nonempty stderr changed'

    external = temp / 'external.schema.json'
    external.write_text('{"$ref":"https://example.invalid/schema.json"}', encoding='utf-8')
    invoke(external, unicode_bad, expected=65)
    invoke(SCHEMA, unicode_bad, '-ExpectedVersion', '0.0.0', expected=78)
    invoke(SCHEMA, unicode_bad, '-Executable', str(temp / 'missing-cli.exe'), expected=69)
    invoke(SCHEMA, temp / 'missing.yaml', expected=66)

    # One reusable caller script proves finally restores in-session state on both exits.
    caller = temp / 'caller.ps1'
    caller.write_text('''param($Wrapper, $Schema, $Instance, $Mode)
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
if ($Mode -eq 'unset') { Remove-Item Env:PYTHONIOENCODING -ErrorAction SilentlyContinue }
elseif ($Mode -eq 'empty') { $env:PYTHONIOENCODING = '' }
else { $env:PYTHONIOENCODING = 'cp936' }
$before = [Environment]::GetEnvironmentVariable('PYTHONIOENCODING', 'Process')
& $Wrapper -SchemaPath $Schema -InstancePath $Instance
$code = $LASTEXITCODE
$after = [Environment]::GetEnvironmentVariable('PYTHONIOENCODING', 'Process')
'STATE=' + (@{before=$before;after=$after;code=$code} | ConvertTo-Json -Compress)
''', encoding='utf-8')
    for mode in ['unset', 'set', 'empty']:
        for instance, expected in [(FIXTURES / 'valid.yaml', 0), (temp / 'missing.yaml', 66)]:
            result = subprocess.run([PWSH, '-NoLogo', '-NoProfile', '-NonInteractive', '-File',
                                     str(caller), str(WRAPPER), str(SCHEMA), str(instance), mode],
                                    cwd=ROOT, capture_output=True, timeout=30, check=True)
            text = result.stdout.decode('utf-8')
            state = json.loads(next(line[6:] for line in text.splitlines() if line.startswith('STATE=')))
            assert state['before'] == state['after'] and state['code'] == expected, state
            records.append({'environment_restore': state, 'mode': mode})

print(json.dumps({'status': 'success', 'wrapper_sha256': hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
                  'real_wrapper_cases': 9, 'channel_reference_comparisons': 5,
                  'environment_restore_cases': 6, 'records': records}, ensure_ascii=False))
