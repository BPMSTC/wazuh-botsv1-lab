import argparse
import json
import time
from pathlib import Path


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def replay_entry(entry: dict, base_dir: Path) -> int:
    source = (base_dir / entry["input"]).resolve()
    target = (base_dir / entry["target"]).resolve()
    sleep_ms = int(entry.get("sleep_ms", 0))

    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with source.open("r", encoding="utf-8") as src, target.open("a", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            dst.write(line.rstrip("\n") + "\n")
            count += 1
            if sleep_ms > 0:
                time.sleep(sleep_ms / 1000.0)

    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay normalized logs by manifest order.")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON")
    parser.add_argument("--base-dir", default=".", help="Base directory for relative paths")
    parser.add_argument("--reset-targets", action="store_true", help="Delete target files before replay starts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    base_dir = Path(args.base_dir)

    manifest = load_manifest(manifest_path)
    entries = manifest.get("entries", [])

    if args.reset_targets:
        seen_targets = set()
        for entry in entries:
            target = (base_dir / entry["target"]).resolve()
            if target in seen_targets:
                continue
            seen_targets.add(target)
            if target.exists():
                target.unlink()

    total = 0
    for entry in entries:
        count = replay_entry(entry, base_dir)
        total += count
        print(f"Replayed {entry.get('name', 'entry')} records={count}")

    print(f"Replay complete total_records={total}")


if __name__ == "__main__":
    main()
