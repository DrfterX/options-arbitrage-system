#!/usr/bin/env python3
import sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.dirname(BASE))
site_pkg = os.path.join(BASE, '.venv', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
if os.path.isdir(site_pkg):
    for fname in os.listdir(site_pkg):
        if fname.endswith('.pth'):
            pth_path = os.path.join(site_pkg, fname)
            with open(pth_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('import '):
                        exec(line)
from web.app import app
if len(sys.argv) >= 3:
    host, port = sys.argv[1], int(sys.argv[2])
else:
    host, port = '127.0.0.1', 5100
print(f"Signal service: http://{host}:{port}")
app.run(host=host, port=port, debug=False)
