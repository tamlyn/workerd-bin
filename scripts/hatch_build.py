import gzip
import hashlib
import json
import os
import platform
import shutil
import stat
import urllib.request
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.version import Version

# Minimum OS versions required by the upstream binaries: the highest GLIBC
# symbol version they reference, and their Mach-O minos (13.5, which wheel
# tags can only express as 13.0).
MIN_GLIBC = "2_35"
MIN_MACOS = "13_0"

ASSET_TO_TAG = {
    "workerd-darwin-64.gz": f"py3-none-macosx_{MIN_MACOS}_x86_64",
    "workerd-darwin-arm64.gz": f"py3-none-macosx_{MIN_MACOS}_arm64",
    "workerd-linux-64.gz": f"py3-none-manylinux_{MIN_GLIBC}_x86_64",
    "workerd-linux-arm64.gz": f"py3-none-manylinux_{MIN_GLIBC}_aarch64",
}


def detect_asset() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = {"x86_64": "64", "aarch64": "arm64", "arm64": "arm64"}.get(machine)
    asset = f"workerd-{system}-{arch}.gz"
    if asset not in ASSET_TO_TAG:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")
    return asset


def github_request(url: str) -> urllib.request.Request:
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def expected_sha256(version: str, asset: str) -> str:
    url = f"https://api.github.com/repos/cloudflare/workerd/releases/tags/v{version}"
    with urllib.request.urlopen(github_request(url)) as resp:
        release = json.load(resp)
    for a in release["assets"]:
        if a["name"] == asset:
            algorithm, _, digest = (a.get("digest") or "").partition(":")
            if algorithm == "sha256" and digest:
                return digest.lower()
    raise RuntimeError(f"No sha256 digest published for {asset} in v{version}")


def download_workerd(directory: Path, version: str, asset: str) -> Path:
    expected = expected_sha256(version, asset)
    url = f"https://github.com/cloudflare/workerd/releases/download/v{version}/{asset}"
    archive = directory / asset

    with urllib.request.urlopen(url) as resp, archive.open("wb") as out:
        shutil.copyfileobj(resp, out)

    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(f"{asset} hash mismatch: {actual} != {expected}")

    binary = directory / "workerd"
    with gzip.open(archive, "rb") as src, binary.open("wb") as out:
        shutil.copyfileobj(src, out)
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    archive.unlink()
    return binary


class CustomHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        if self.target_name == "sdist":
            return
        asset = os.environ.get("WORKERD_ASSET") or detect_asset()
        # Packaging-only fixes are released as post-releases (e.g. 1.20261023.1.post1)
        # of the same upstream workerd version.
        upstream_version = Version(self.metadata.version).base_version
        binary = download_workerd(Path(self.directory), upstream_version, asset)
        build_data["tag"] = ASSET_TO_TAG[asset]
        build_data["shared_scripts"][str(binary.absolute())] = f"src/{binary.name}"

    def finalize(self, version: str, build_data: dict, artifact_path: str) -> None:
        if self.target_name == "sdist":
            return
        (Path(self.directory) / "workerd").unlink(missing_ok=True)
