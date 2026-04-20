import argparse
import gzip
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List

from mappers.iis_mapper import map_iis_record
from mappers.sysmon_mapper import map_sysmon_record
from mappers.winevent_mapper import map_winevent_record

Mapper = Callable[[dict], dict]


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("r", encoding="utf-8")


def iter_json_records(path: Path) -> Iterator[dict]:
    with open_text(path) as handle:
        content = handle.read(1)
        if not content:
            return

    with open_text(path) as handle:
        first_char = handle.read(1)
        handle.seek(0)

        if first_char == "[":
            for record in json.load(handle):
                if isinstance(record, dict):
                    yield record
            return

        for line in handle:
            text = line.strip()
            if not text:
                continue
            value = json.loads(text)
            if isinstance(value, dict):
                yield value


def write_json_lines(path: Path, records: Iterable[dict]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
            count += 1
    return count


def choose_mapper(lane: str) -> Mapper:
    mappers: Dict[str, Mapper] = {
        "sysmon": map_sysmon_record,
        "winevent": map_winevent_record,
        "iis": map_iis_record,
    }
    if lane not in mappers:
        supported = ", ".join(sorted(mappers.keys()))
        raise ValueError(f"Unsupported lane '{lane}'. Supported lanes: {supported}")
    return mappers[lane]


def transform(records: Iterable[dict], mapper: Mapper, limit: int | None = None) -> List[dict]:
    output: List[dict] = []
    for record in records:
        mapped = mapper(record)
        if mapped:
            output.append(mapped)
        if limit is not None and len(output) >= limit:
            break
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize BOTSv1 sourcetype exports.")
    parser.add_argument("--lane", required=True, choices=["sysmon", "winevent", "iis"])
    parser.add_argument("--input", required=True, help="Path to JSONL input file")
    parser.add_argument("--output", required=True, help="Path to JSONL output file")
    parser.add_argument("--limit", type=int, default=None, help="Optional max number of normalized records")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.input)
    target = Path(args.output)

    mapper = choose_mapper(args.lane)
    records = iter_json_records(source)
    normalized = transform(records, mapper, limit=args.limit)
    count = write_json_lines(target, normalized)

    print(f"Lane={args.lane} input={source} output={target} records={count}")


if __name__ == "__main__":
    main()
