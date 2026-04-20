import argparse
import io
import shutil
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_REF = "v4.14.4"
REPO_ARCHIVE_TEMPLATE = "https://github.com/wazuh/wazuh-docker/archive/refs/tags/{ref}.zip"


def download_archive(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:
        return response.read()


def extract_single_node(archive_bytes: bytes, destination: Path, ref: str) -> None:
    root_prefix = f"wazuh-docker-{ref.lstrip('v')}/single-node/"
    destination.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = [name for name in archive.namelist() if name.startswith(root_prefix)]
        if not members:
            raise RuntimeError(f"Could not find single-node assets in archive for {ref}")

        for member in members:
            relative = Path(member[len(root_prefix):])
            if not relative.parts:
                continue

            target = destination / relative
            if member.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vendor official Wazuh single-node assets into the deployment directory.")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Wazuh docker tag to vendor, for example v4.14.4")
    parser.add_argument(
        "--destination",
        default="deployment/vendor/wazuh-docker/single-node",
        help="Directory where the single-node files will be extracted",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing vendored directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destination = Path(args.destination)

    if destination.exists() and any(destination.iterdir()):
        if not args.force:
            raise SystemExit(f"Destination already exists: {destination}. Use --force to replace it.")
        shutil.rmtree(destination)

    url = REPO_ARCHIVE_TEMPLATE.format(ref=args.ref)
    archive_bytes = download_archive(url)
    extract_single_node(archive_bytes, destination, args.ref)

    print(f"Vendored Wazuh single-node assets ref={args.ref} destination={destination}")


if __name__ == "__main__":
    main()
