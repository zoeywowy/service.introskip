"""Build a Kodi repository using the standard Kodi/A4K ZIP layout.

The GitHub Pages site is only the bootstrap download page. Once installed,
Kodi reads the repository index, MD5 checksum and add-on ZIPs from raw GitHub.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPOSITORY_ZIPS = ROOT / "repository" / "zips"
PAGES_BASE = "https://zoeywowy.github.io/service.introskip/"
RAW_BASE = "https://raw.githubusercontent.com/zoeywowy/service.introskip/main/repository/zips/"
REPO_ID = "repository.introskip"
REPO_VERSION = "1.0.3"
SERVICE_ID = "service.introskip"


def make_repository_manifest() -> ET.Element:
    addon = ET.Element("addon", {
        "id": REPO_ID,
        "name": "IntroSkip Repository",
        "version": REPO_VERSION,
        "provider-name": "zoeywowy",
    })
    repo_extension = ET.SubElement(
        addon, "extension",
        {"point": "xbmc.addon.repository", "name": "IntroSkip Repository"},
    )
    directory = ET.SubElement(repo_extension, "dir", {"minversion": "22.0"})
    ET.SubElement(directory, "info", {"compressed": "false"}).text = RAW_BASE + "addons.xml"
    ET.SubElement(directory, "checksum").text = RAW_BASE + "addons.xml.md5"
    # This is Kodi's standard repository layout: addonid/addonid-version.zip.
    ET.SubElement(directory, "datadir", {"zip": "true"}).text = RAW_BASE

    metadata = ET.SubElement(addon, "extension", {"point": "xbmc.addon.metadata"})
    ET.SubElement(metadata, "summary", {"lang": "en_GB"}).text = "Install and update IntroSkip for Kodi 22"
    ET.SubElement(metadata, "description", {"lang": "en_GB"}).text = (
        "Unofficial Kodi 22 repository containing IntroSkip. Repository metadata "
        "and installable ZIPs use the standard Kodi add-on repository layout."
    )
    ET.SubElement(metadata, "platform").text = "all"
    ET.SubElement(metadata, "license").text = "Apache-2.0"
    ET.SubElement(metadata, "website").text = "https://github.com/zoeywowy/service.introskip"
    ET.SubElement(metadata, "source").text = "https://github.com/zoeywowy/service.introskip"
    assets = ET.SubElement(metadata, "assets")
    ET.SubElement(assets, "icon").text = "icon.png"
    return addon


def xml_document(element: ET.Element) -> bytes:
    return ET.tostring(element, encoding="utf-8", xml_declaration=True) + b"\n"


def main() -> None:
    addon_manifest = ET.parse(ROOT / "addon.xml").getroot()
    addon_id = addon_manifest.attrib["id"]
    addon_version = addon_manifest.attrib["version"]
    if addon_id != SERVICE_ID:
        raise SystemExit("Unexpected source add-on ID: " + addon_id)

    subprocess.run([sys.executable, str(ROOT / "build_zip.py")], check=True, cwd=ROOT)
    service_filename = f"{SERVICE_ID}-{addon_version}.zip"
    service_source = ROOT / "dist" / service_filename
    if not service_source.is_file():
        raise SystemExit("Service ZIP builder did not create " + str(service_source))
    with ZipFile(service_source) as package:
        if package.testzip() is not None or f"{SERVICE_ID}/addon.xml" not in package.namelist():
            raise SystemExit("Invalid IntroSkip package")

    icon = ROOT / "icon.png"
    if not icon.is_file():
        raise SystemExit("Missing icon.png")

    # Publish the repository and service in Kodi's conventional zips/ tree.
    service_dir = REPOSITORY_ZIPS / SERVICE_ID
    service_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(service_source, service_dir / service_filename)
    shutil.copy2(icon, service_dir / "icon.png")
    shutil.copy2(ROOT / "addon.xml", service_dir / "addon.xml")

    repository_addon = make_repository_manifest()
    repository_xml = xml_document(repository_addon)
    ET.fromstring(repository_xml)
    repository_dir = REPOSITORY_ZIPS / REPO_ID
    repository_dir.mkdir(parents=True, exist_ok=True)
    (repository_dir / "addon.xml").write_bytes(repository_xml)
    shutil.copy2(icon, repository_dir / "icon.png")

    repository_filename = f"{REPO_ID}-{REPO_VERSION}.zip"
    repository_zip = repository_dir / repository_filename
    with ZipFile(repository_zip, "w", ZIP_DEFLATED) as package:
        package.writestr(f"{REPO_ID}/addon.xml", repository_xml)
        package.write(icon, arcname=f"{REPO_ID}/icon.png")
    with ZipFile(repository_zip) as package:
        if package.testzip() is not None or f"{REPO_ID}/addon.xml" not in package.namelist():
            raise SystemExit("Invalid repository installer ZIP")

    # Kodi reads this uncompressed index and its adjacent MD5 file.
    addons = ET.Element("addons")
    addons.append(repository_addon)
    addons.append(addon_manifest)
    content = xml_document(addons)
    ET.fromstring(content)
    REPOSITORY_ZIPS.mkdir(parents=True, exist_ok=True)
    (REPOSITORY_ZIPS / "addons.xml").write_bytes(content)
    digest = hashlib.md5(content).hexdigest()
    (REPOSITORY_ZIPS / "addons.xml.md5").write_text(digest, encoding="ascii")

    # GitHub Pages is only the convenient first-install ZIP landing page.
    DOCS.mkdir(parents=True, exist_ok=True)
    for stale_name in ("addons.xml", "addons.xml.md5", "addons-checksum.txt"):
        stale = DOCS / stale_name
        if stale.exists():
            stale.unlink()
    for stale in DOCS.glob(f"{REPO_ID}-*.zip"):
        stale.unlink()
    shutil.rmtree(DOCS / REPO_ID, ignore_errors=True)
    shutil.rmtree(DOCS / SERVICE_ID, ignore_errors=True)
    shutil.copy2(repository_zip, DOCS / repository_filename)
    (DOCS / ".nojekyll").touch()

    service_release = (
        f"https://github.com/zoeywowy/service.introskip/releases/download/"
        f"v{addon_version}/{service_filename}"
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>IntroSkip Kodi Repository</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><h1>IntroSkip Kodi Repository</h1>
<p>For Kodi 22, download and install the repository ZIP:</p>
<p><a href="{repository_filename}">{repository_filename}</a></p>
<p>In Kodi: Add-ons → Install from zip file → select the downloaded ZIP.</p>
<h2>Repository data (Kodi standard layout)</h2>
<ul>
<li><a href="{RAW_BASE}addons.xml">Add-on index (addons.xml)</a></li>
<li><a href="{RAW_BASE}addons.xml.md5">MD5 checksum (addons.xml.md5)</a></li>
<li><a href="{RAW_BASE}">Package directory base</a></li>
</ul>
<p><a href="{service_release}">Direct IntroSkip service ZIP</a></p>
<p><a href="https://github.com/zoeywowy/service.introskip">Source code and documentation</a></p>
</body></html>
"""
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print("Kodi File Manager/bootstrap page:", PAGES_BASE)
    print("Repository installer:", PAGES_BASE + repository_filename)
    print("Kodi repository index:", RAW_BASE + "addons.xml")
    print("Kodi repository checksum:", RAW_BASE + "addons.xml.md5")
    print("Kodi package directory:", RAW_BASE)


if __name__ == "__main__":
    main()
