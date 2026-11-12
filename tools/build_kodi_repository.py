"""Build a GitHub Pages-hosted Kodi repository for IntroSkip.

Usage: python tools/build_kodi_repository.py

GitHub Pages: https://zoeywowy.github.io/service.introskip/
Kodi File Manager source: that same URL, after Pages is enabled.
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
PUBLIC = ROOT / "docs"
BASE = "https://zoeywowy.github.io/service.introskip/"
REPO_ID = "repository.introskip"
REPO_VERSION = "1.0.1"
SERVICE_ID = "service.introskip"


def make_repository_manifest() -> ET.Element:
    addon = ET.Element("addon", {
        "id": REPO_ID,
        "name": "IntroSkip Repository",
        "version": REPO_VERSION,
        "provider-name": "zoeywowy",
    })
    requirements = ET.SubElement(addon, "requires")
    ET.SubElement(requirements, "import", {"addon": "xbmc.addon", "version": "12.0.0"})
    repo_extension = ET.SubElement(addon, "extension", {"point": "xbmc.addon.repository"})
    directory = ET.SubElement(repo_extension, "dir")
    ET.SubElement(directory, "info", {"compressed": "false"}).text = BASE + "addons.xml"
    ET.SubElement(directory, "checksum").text = BASE + "addons.xml.md5"
    ET.SubElement(directory, "datadir").text = BASE
    # GitHub Pages does not serve the optional Kodi content-sha256 HTTP header.
    ET.SubElement(directory, "hashes").text = "false"
    metadata = ET.SubElement(addon, "extension", {"point": "xbmc.addon.metadata"})
    ET.SubElement(metadata, "summary", {"lang": "en_GB"}).text = "Install and update IntroSkip for Kodi 22"
    ET.SubElement(metadata, "description", {"lang": "en_GB"}).text = (
        "Unofficial repository containing IntroSkip: TV recap, intro, outro "
        "and movie credit skip prompts using Cinemeta, IntroDB and Kodi 22 chapters."
    )
    ET.SubElement(metadata, "platform").text = "all"
    ET.SubElement(metadata, "license").text = "Apache-2.0"
    ET.SubElement(metadata, "website").text = "https://github.com/zoeywowy/service.introskip"
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

    PUBLIC.mkdir(parents=True, exist_ok=True)
    service_dest_dir = PUBLIC / SERVICE_ID
    service_dest_dir.mkdir(exist_ok=True)
    shutil.copy2(service_source, service_dest_dir / service_filename)

    repository_addon = make_repository_manifest()
    repository_xml = xml_document(repository_addon)
    ET.fromstring(repository_xml)
    icon = ROOT / "icon.png"
    if not icon.is_file():
        raise SystemExit("Missing icon.png")
    repo_filename = f"{REPO_ID}-{REPO_VERSION}.zip"
    repo_dir = PUBLIC / REPO_ID
    repo_dir.mkdir(exist_ok=True)
    # Kodi expects add-on artwork alongside the hosted ZIP files.
    shutil.copy2(icon, service_dest_dir / "icon.png")
    shutil.copy2(icon, repo_dir / "icon.png")

    for repo_zip in (PUBLIC / repo_filename, repo_dir / repo_filename):
        with ZipFile(repo_zip, "w", ZIP_DEFLATED) as package:
            package.writestr(f"{REPO_ID}/addon.xml", repository_xml)
            package.write(icon, arcname=f"{REPO_ID}/icon.png")
        with ZipFile(repo_zip) as package:
            if package.testzip() is not None:
                raise SystemExit("Invalid repository ZIP: " + str(repo_zip))

    # The uncompressed addons.xml lists both the repository and the service.
    addons = ET.Element("addons")
    addons.append(repository_addon)
    addons.append(addon_manifest)
    content = xml_document(addons)
    ET.fromstring(content)
    (PUBLIC / "addons.xml").write_bytes(content)
    # Kodi uses this as the update-change indicator, not as a security proof.
    (PUBLIC / "addons.xml.md5").write_text(
        hashlib.md5(content).hexdigest(), encoding="ascii"
    )
    (PUBLIC / ".nojekyll").touch()
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Index of /service.introskip/ — IntroSkip Kodi Add-on Repository</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><h1>IntroSkip Kodi Repository</h1>
<p>For Kodi 22: Add source <strong>{BASE}</strong>, then
<strong>Add-ons → Install from zip file</strong> and choose the repository ZIP.</p>
<h2>Repository installer</h2>
<ul>
<li><a href="{repo_filename}">{repo_filename}</a></li>
<li><a href="{SERVICE_ID}/{service_filename}">{service_filename}</a> (direct installation)</li>
</ul>
<p>Once installed, find <strong>IntroSkip Repository</strong> under
Add-ons → Install from repository and choose IntroSkip.</p>
<p><a href="https://github.com/zoeywowy/service.introskip">
Source code and issues</a></p></body></html>
"""
    (PUBLIC / "index.html").write_text(html, encoding="utf-8")
    print("Kodi source URL:", BASE)
    print("Kodi repo installer:", BASE + repo_filename)
    print("Kodi package:", BASE + f"{SERVICE_ID}/{service_filename}")
    print("Repository index:", BASE + "addons.xml")


if __name__ == "__main__":
    main()
