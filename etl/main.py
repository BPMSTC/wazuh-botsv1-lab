import argparse
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List

from mappers.iis_mapper import map_iis_record
from mappers.sysmon_mapper import map_sysmon_record
from mappers.winevent_mapper import map_winevent_record

Mapper = Callable[[dict], dict]


def iter_json_lines(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            yield json.loads(text)


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


def transform(records: Iterable[dict], mapper: Mapper) -> List[dict]:
    output: List[dict] = []
    for record in records:
        mapped = mapper(record)
        if mapped:
            output.append(mapped)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize BOTSv1 sourcetype exports.")
    parser.add_argument("--lane", required=True, choices=["sysmon", "winevent", "iis"])
    parser.add_argument("--input", required=True, help="Path to JSONL input file")
    parser.add_argument("--output", required=True, help="Path to JSONL output file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.input)
    target = Path(args.output)

    mapper = choose_mapper(args.lane)
    records = iter_json_lines(source)
    normalized = transform(records, mapper)
    count = write_json_lines(target, normalized)

    print(f"Lane={args.lane} input={source} output={target} records={count}")


if __name__ == "__main__":
    main()
