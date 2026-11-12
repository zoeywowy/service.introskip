"""Build Kodi-installable ZIP from this repository (run: python build_zip.py)."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
addon_id = ET.parse(root / 'addon.xml').getroot().get('id')
version = ET.parse(root / 'addon.xml').getroot().get('version')
if addon_id != 'service.introskip':
    raise SystemExit('Unexpected addon id: ' + str(addon_id))
out = root / 'dist' / f'{addon_id}-{version}.zip'
out.parent.mkdir(exist_ok=True)
ignore_dirs = {'.git', '.github', 'dist', 'docs', 'tests', '__pycache__', '.pytest_cache', '.venv', 'venv'}
exclude_names = {'build_zip.py', '.gitignore', 'CONTRIBUTING.md', 'SECURITY.md', 'LICENSE'}
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in ignore_dirs for part in relative.parts) or path.name in exclude_names or path.suffix in ('.pyc', '.log'):
            continue
        archive.write(path, arcname=str(Path(addon_id) / relative))
print(out)
