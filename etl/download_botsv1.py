import argparse
import gzip
import json
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_MANIFEST = Path("etl/source_manifest.json")
DEFAULT_OUTPUT_DIR = Path("data/raw")
DEFAULT_LOG_PATH = Path("data/raw/download-log.jsonl")


def load_manifest(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["sources"]


def filter_sources(sources: list[dict], requested: Iterable[str]) -> list[dict]:
    requested_set = set(requested)
    if not requested_set:
        return sources
    return [source for source in sources if source["name"] in requested_set]


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def maybe_decompress(source: Path) -> Path:
    if source.suffix != ".gz":
        return source

    target = source.with_suffix("")
    with gzip.open(source, "rb") as compressed, target.open("wb") as handle:
        shutil.copyfileobj(compressed, handle)
    return target


def append_log(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download selected BOTSv1 sourcetype files.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to source manifest JSON")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for raw downloads")
    parser.add_argument("--log-path", default=str(DEFAULT_LOG_PATH), help="Download log JSONL path")
    parser.add_argument("--lane", action="append", default=[], help="Manifest source name to download; may be repeated")
    parser.add_argument("--decompress", action="store_true", help="Decompress .gz files after download")
    parser.add_argument("--force", action="store_true", help="Overwrite existing downloaded files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    log_path = Path(args.log_path)

    sources = filter_sources(load_manifest(manifest_path), args.lane)
    if not sources:
        raise SystemExit("No matching sources found in manifest")

    for source in sources:
        lane_dir = output_dir / source["name"]
        archive_path = lane_dir / source["filename"]

        if archive_path.exists() and not args.force:
            print(f"Skipping existing file: {archive_path}")
            continue

        download_file(source["url"], archive_path)
        final_path = maybe_decompress(archive_path) if args.decompress else archive_path

        append_log(
            log_path,
            {
                "downloaded_at": datetime.now(tz=timezone.utc).isoformat(),
                "name": source["name"],
                "lane": source["lane"],
                "sourcetype": source["sourcetype"],
                "url": source["url"],
                "archive_path": str(archive_path),
                "final_path": str(final_path),
            },
        )
        print(f"Downloaded name={source['name']} final_path={final_path}")


if __name__ == "__main__":
    main()
