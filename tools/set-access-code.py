#!/usr/bin/env python3
"""Access codes are now managed online - this script no longer changes index.html.

Since the online access service went live, the lock screen checks codes with the
SafeBuilt access service (Cloudflare Worker 'fda-access', URL in BRAND.accessApi).
Each code has its own device limit (e.g. 3 or 10 phones) and can be deactivated
or have single devices removed.

Manage codes (create, device limit, deactivate, delete, remove devices) at:
    https://fda-access.safebuilt.workers.dev/admin   (log in with the admin key)

No code, salt or hash is stored in this public repository any more.
To switch the lock off, set BRAND.accessApi to '' in index.html.
"""
import sys

if __name__ == '__main__':
    print(__doc__.strip())
    sys.exit(1)
