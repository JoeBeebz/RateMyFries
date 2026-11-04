"""Restore a CMS-encrypted class-server copy on its intended EC2 machine.

Run as root on the new instance. The transfer certificate's private key never
leaves that instance; plaintext configuration is never sent through SSM history.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tarfile


def check_database(path):
    with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as connection:
        assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not connection.execute('PRAGMA foreign_key_check').fetchall()
        return {table: connection.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]
                for table in ('users', 'restaurants', 'fries', 'reviews', 'business_requests')}


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run this installer as root on the new EC2 instance.')
    transfer = Path('/root/fry-transfer')
    envelope = Path(sys.argv[1]).resolve(strict=True)
    assert envelope.is_relative_to(transfer)
    plaintext = transfer / 'restore.tar.gz'
    subprocess.run(['openssl', 'cms', '-decrypt', '-inform', 'DER', '-in', str(envelope),
                    '-recip', str(transfer / 'certificate.pem'), '-inkey', str(transfer / 'key.pem'),
                    '-out', str(plaintext)], check=True)
    plaintext.chmod(0o600)
    stage = transfer / ('restore-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    stage.mkdir(mode=0o700)
    with tarfile.open(plaintext) as archive:
        for member in archive.getmembers():
            assert member.isfile() or member.isdir(), 'Only ordinary files/directories are accepted'
            assert (stage / member.name).resolve().is_relative_to(stage)
        archive.extractall(stage, filter='data')
    manifest = json.loads((stage / 'manifest.json').read_text())
    counts = check_database(stage / 'state/fries.sqlite3')
    assert counts == manifest['counts']
    commit = manifest['commit'].strip()
    assert len(commit) == 40 and all(c in '0123456789abcdef' for c in commit)
    base = Path('/srv/ratemyfries')
    release = base / 'releases' / (commit[:12] + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    release.parent.mkdir(exist_ok=True)
    shutil.copytree(stage / 'app', release)
    instance = release / 'instance'
    instance.mkdir(mode=0o700)
    for name in ('fries.sqlite3', 'secret.key'):
        shutil.copy2(stage / 'state' / name, instance / name)
        (instance / name).chmod(0o600)
    shutil.copy2(stage / 'secrets/google.env', '/etc/ratemyfries/google.env')
    Path('/etc/ratemyfries/google.env').chmod(0o600)
    subprocess.run(['python3.12', '-m', 'venv', str(release / '.venv')], check=True)
    subprocess.run([str(release / '.venv/bin/python'), '-m', 'pip', 'install', '-r', str(release / 'requirements.txt')], check=True)
    subprocess.run(['chown', '-R', 'fryapp:fry-admins', str(release)], check=True)
    current = base / 'current'
    if current.exists() and not current.is_symlink():
        raise RuntimeError('Refusing to replace an unmanaged current directory')
    previous = str(current.resolve()) if current.is_symlink() else None
    pending = base / '.current-next'
    assert not pending.exists() and not pending.is_symlink()
    pending.symlink_to(release, target_is_directory=True)
    os.replace(pending, current)
    (release / 'DEPLOYED_COMMIT').write_text(commit + '\n')
    subprocess.run(['chown', 'fryapp:fry-admins', str(release / 'DEPLOYED_COMMIT')], check=True)
    subprocess.run(['systemctl', 'restart', 'ratemyfries.service'], check=True)
    subprocess.run(['systemctl', 'is-active', '--quiet', 'ratemyfries.service'], check=True)
    assert check_database(instance / 'fries.sqlite3') == counts
    print(json.dumps({'installed': True, 'commit': commit, 'counts': counts,
                      'release': str(release), 'previous_release': previous,
                      'listener': '127.0.0.1:8000'}))


if __name__ == '__main__':
    main()
