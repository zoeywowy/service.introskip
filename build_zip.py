"""Build a minimal Kodi-installable ZIP (run: python build_zip.py)."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
ADDON = ET.parse(ROOT / "addon.xml").getroot()
ADDON_ID = ADDON.get("id")
VERSION = ADDON.get("version")

if ADDON_ID != "service.introskip":
    raise SystemExit("Unexpected add-on id: " + str(ADDON_ID))
if not VERSION:
    raise SystemExit("Missing add-on version")

# Explicit runtime allow-list: documentation, tests, workflows, caches and
# development tools can never leak into the Kodi installation package.
FILES = [
    ROOT / "addon.xml",
    ROOT / "service.py",
    ROOT / "main.py",
    ROOT / "icon.png",
    ROOT / "resources" / "settings.xml",
]
FILES.extend(sorted((ROOT / "resources" / "lib").glob("*.py")))
FILES.extend(sorted((ROOT / "resources" / "language" / "resource.language.en_gb").glob("*.po")))
FILES.extend(sorted((ROOT / "resources" / "skins" / "Default" / "1080i").glob("*.xml")))
MEDIA = ROOT / "resources" / "skins" / "Default" / "media"
FILES.extend(sorted(MEDIA.glob("modern_*.png")))
FILES.append(MEDIA / "skip-next.png")

missing = [str(path.relative_to(ROOT)) for path in FILES if not path.is_file()]
if missing:
    raise SystemExit("Missing required runtime files: " + ", ".join(missing))

OUTPUT = ROOT / "dist" / "{}-{}.zip".format(ADDON_ID, VERSION)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with ZipFile(OUTPUT, "w", ZIP_DEFLATED, compresslevel=9) as archive:
    for path in FILES:
        archive.write(path, arcname=str(Path(ADDON_ID) / path.relative_to(ROOT)))

with ZipFile(OUTPUT) as archive:
    bad_file = archive.testzip()
    if bad_file:
        raise SystemExit("Corrupt package member: " + bad_file)

print(OUTPUT)
