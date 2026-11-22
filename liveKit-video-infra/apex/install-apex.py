#!/usr/bin/env python3
"""Validate and hot-reload the apex site without replacing the API release."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

if os.geteuid() != 0:
    raise SystemExit("Run as root after reviewing the configuration.")
source = Path(sys.argv[1]).resolve(strict=True)
if not source.is_file() or source.stat().st_size > 16384:
    raise SystemExit("Unexpected apex site file.")
site = Path('/etc/caddy/patvero-apex.caddy')
main = Path('/etc/caddy/Caddyfile')
original = main.read_bytes()
original_stat = main.stat()
expected = source.read_bytes()
import_line = b'import /etc/caddy/patvero-apex.caddy'
if b'api.patvero.com' not in original:
    raise SystemExit("Expected API configuration was not found; no changes made.")
if site.exists() and site.read_bytes() != expected:
    raise SystemExit("An existing apex site differs; review it before replacing it.")
if import_line in original and site.exists():
    print(json.dumps({'status': 'already_installed'}))
    raise SystemExit(0)

backup = Path('/var/backups') / ('patvero-apex-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(mode=0o700)
shutil.copy2(main, backup / 'Caddyfile')
os.chmod(backup / 'Caddyfile', 0o600)
site_preexisted = site.exists()
site.write_bytes(expected)
os.chmod(site, 0o644)
candidate = original.rstrip() + b'\n\n' + import_line + b'\n'
fd, temporary = tempfile.mkstemp(prefix='patvero-apex-', suffix='.caddy', dir='/etc/caddy')
changed_main = False
try:
    with os.fdopen(fd, 'wb') as handle:
        handle.write(candidate)
    check = subprocess.run(['caddy', 'validate', '--config', temporary, '--adapter', 'caddyfile'], capture_output=True)
    if check.returncode:
        raise RuntimeError('Caddy rejected the candidate; API configuration was not changed.')
    os.chmod(temporary, original_stat.st_mode & 0o777)
    os.chown(temporary, original_stat.st_uid, original_stat.st_gid)
    os.replace(temporary, main)
    changed_main = True
    reload = subprocess.run(['systemctl', 'reload', 'caddy'], capture_output=True)
    if reload.returncode:
        raise RuntimeError('Hot reload failed.')
    print(json.dumps({'status': 'installed', 'backup': str(backup), 'site_sha256': hashlib.sha256(expected).hexdigest()}))
except Exception:
    if changed_main:
        restore_fd, restore_path = tempfile.mkstemp(prefix='patvero-restore-', suffix='.caddy', dir='/etc/caddy')
        with os.fdopen(restore_fd, 'wb') as handle:
            handle.write(original)
        os.chmod(restore_path, original_stat.st_mode & 0o777)
        os.chown(restore_path, original_stat.st_uid, original_stat.st_gid)
        os.replace(restore_path, main)
        subprocess.run(['systemctl', 'reload', 'caddy'], capture_output=True)
    if not site_preexisted:
        site.unlink(missing_ok=True)
    raise
finally:
    Path(temporary).unlink(missing_ok=True)
