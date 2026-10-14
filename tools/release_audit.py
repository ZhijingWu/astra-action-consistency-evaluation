"""Offline heuristic privacy/secret/size scan and SHA-256 inventory.

No scanner proves absence of secrets. Review the intended files and notices.
This utility never stages, commits, creates remotes, or publishes anything.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 5 * 1024 * 1024
EXCLUDED_DIRS = {'.git', '.venv', '__pycache__', '.pytest_cache', 'build', 'dist'}
EXCLUDED_FILES = {'SHA256SUMS.txt', 'verification/release_scan.json'}
PATTERNS = {
    'private_absolute_path': re.compile(r'(?i)(?:\b[a-z]:[\\/]|/(?:data\d+|home|Users)/)'),
    'github_token': re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})'),
    'openai_token': re.compile(r'sk-(?:proj-)?[A-Za-z0-9_\-]{20,}'),
    'aws_access_key': re.compile(r'(?:AKIA|ASIA)[A-Z0-9]{16}'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'credential_assignment': re.compile(r'''(?i)\b(?:password|api_key|access_token|client_secret)\s*[=:]\s*["']?[A-Za-z0-9+/_\-]{12,}'''),
    'authenticated_url': re.compile(r'https?://[^\s/:]+:[^\s/@]+@'),
}
FORBIDDEN_SUFFIXES = {'.ckpt', '.pth', '.safetensors', '.mp4', '.avi', '.mov', '.npy', '.npz', '.zip', '.pdf', '.dll', '.exe', '.pyd'}
TEXT_SUFFIXES = {'.md', '.txt', '.py', '.json', '.csv', '.toml', '.yml', '.yaml', '.bib', '.cff', '.svg'}


def files(root=ROOT):
    return sorted(p for p in root.rglob('*') if p.is_file() and not any(part in EXCLUDED_DIRS for part in p.relative_to(root).parts))


def scan(root=ROOT):
    findings, inventory = [], []
    for path in files(root):
        name = path.relative_to(root).as_posix()
        if name == 'verification/release_scan.json':
            continue  # This generated receipt cannot embed its own final hash.
        data = path.read_bytes()
        inventory.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        if len(data) > MAX_BYTES:
            findings.append({'file': name, 'type': 'large_file'})
        if path.is_symlink():
            findings.append({'file': name, 'type': 'symlink'})
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name in ['.env', '.netrc', 'id_rsa', 'id_ed25519']:
            findings.append({'file': name, 'type': 'forbidden_file_type_or_name'})
        if any(word in name.lower() for word in ['unblinding', 'reviewer_package', 'input_snapshot', 'proxy_config']):
            findings.append({'file': name, 'type': 'restricted_filename'})
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in ['LICENSE', '.gitignore', '.gitattributes']:
            try:
                text = data.decode('utf-8-sig')
            except UnicodeError:
                findings.append({'file': name, 'type': 'invalid_utf8'})
                continue
            for kind, pattern in PATTERNS.items():
                if pattern.search(text):
                    findings.append({'file': name, 'type': kind})
            # Declarations and reviewer identifiers must not appear in public tables/records.
            if path.suffix.lower() in {'.csv', '.json'} and re.search(r'(?i)(?:reviewer_id|annotator_id|reviewer_name|user_declaration)', text):
                findings.append({'file': name, 'type': 'annotation_identity_or_declaration'})
    return {'status': 'PASS' if not findings else 'FAIL', 'findings': findings,
            'file_count': len(inventory), 'logical_bytes': sum(r['bytes'] for r in inventory),
            'maximum_file_bytes': max((r['bytes'] for r in inventory), default=0),
            'per_file_limit_bytes': MAX_BYTES,
            'scan_receipt_excluded_from_its_own_inventory': True,
            'limitations': 'Offline heuristic scan plus intended-file review; no guarantee of absence of all secrets. Git metadata and ignored caches are outside the payload.',
            'inventory': inventory}


def manifest(root=ROOT):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files(root) if p.relative_to(root).as_posix() not in EXCLUDED_FILES}


def write_manifest(root=ROOT):
    (root / 'SHA256SUMS.txt').write_text(''.join(f'{value}  {name}\n' for name, value in manifest(root).items()), encoding='utf-8', newline='\n')


def verify_manifest(root=ROOT):
    expected = {}
    for line in (root / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        value, name = line.split('  ', 1)
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in expected:
            raise ValueError('Invalid manifest path or duplicate')
        expected[name] = value
    actual = manifest(root)
    mismatches = sorted(name for name in expected.keys() | actual.keys() if expected.get(name) != actual.get(name))
    return {'status': 'PASS' if not mismatches else 'FAIL', 'payload_files_verified': len(expected), 'mismatches': mismatches,
            'excludes': sorted(EXCLUDED_FILES), 'reason': 'Manifest cannot hash itself; scan receipt embeds hashes of payload and would create a circular dependency.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest', action='store_true')
    parser.add_argument('--verify-manifest', action='store_true')
    args = parser.parse_args()
    if args.write_manifest:
        write_manifest()
    if args.verify_manifest:
        result = verify_manifest()
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['status'] == 'PASS' else 1)
    result = scan()
    print(json.dumps({k: v for k, v in result.items() if k != 'inventory'}, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
