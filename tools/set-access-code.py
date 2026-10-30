#!/usr/bin/env python3
"""Set the SafeBuilt Doors access code (lock screen).

Usage:  python3 tools/set-access-code.py ENV_VAR_NAME

Reads the code from the environment variable named in argv[1] (so it never
appears in shell history or on screen), makes a new random salt, and rewrites
BRAND.accessSalt / BRAND.accessHash (hex SHA-256 of salt + code) in index.html
and in the mirror copy (../fire-door-app/index.html, or the paths given in
FDA_TARGETS, separated by ':'). The code itself is never printed or stored.
An empty variable switches the lock off (salt and hash set to '').
"""
import hashlib, os, re, secrets, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_TARGETS = [os.path.join(REPO, 'index.html'),
                   os.path.join(os.path.dirname(REPO), 'fire-door-app', 'index.html')]
SALT_RE = re.compile(r"^(\s*accessSalt:)'[^'\n]*'", re.M)
HASH_RE = re.compile(r"^(\s*accessHash:)'[^'\n]*'", re.M)


def main():
    if len(sys.argv) != 2:
        sys.exit('usage: set-access-code.py ENV_VAR_NAME')
    name = sys.argv[1]
    if name not in os.environ:
        sys.exit(f'environment variable {name} is not set')
    code = os.environ[name]
    if code:
        if len(code) < 4:
            sys.exit('access code is too short (min 4 characters)')
        salt = secrets.token_hex(16)
        digest = hashlib.sha256((salt + code).encode('utf-8')).hexdigest()
    else:
        salt = digest = ''
    targets = os.environ.get('FDA_TARGETS')
    targets = targets.split(':') if targets else DEFAULT_TARGETS
    done = 0
    for path in targets:
        if not os.path.isfile(path):
            print(f'skip (not found): {path}')
            continue
        with open(path, encoding='utf-8') as fh:
            src = fh.read()
        out, n1 = SALT_RE.subn(lambda m: f"{m.group(1)}'{salt}'", src, count=1)
        out, n2 = HASH_RE.subn(lambda m: f"{m.group(1)}'{digest}'", out, count=1)
        if n1 != 1 or n2 != 1:
            sys.exit(f'accessSalt/accessHash not found in {path}')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(out)
        done += 1
        print(f'updated: {path}')
    if not done:
        sys.exit('no files updated')
    print('lock ' + ('ON (new salt; all devices must re-enter the code)' if digest else 'OFF'))


if __name__ == '__main__':
    main()
