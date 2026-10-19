import argparse
import csv
import json
from pathlib import Path
from random import Random

CATEGORIES = ["infusion", "monitor", "imaging", "laboratory", "sterilization"]
DEPARTMENTS = ["Demo Ward", "Demo ICU", "Demo Imaging", "Demo Laboratory"]
STATUSES = ["active", "active", "active", "maintenance", "retired"]


def generate_devices(count: int, seed: int) -> list[dict[str, str]]:
    random = Random(seed)
    return [
        {
            "asset_code": f"DEMO-{index + 1:06d}",
            "name": f"Demo {random.choice(CATEGORIES).title()} Device {index + 1}",
            "category": random.choice(CATEGORIES),
            "department": random.choice(DEPARTMENTS),
            "manufacturer": f"Demo Manufacturer {random.randint(1, 12)}",
            "model": f"DM-{random.randint(100, 999)}",
            "status": random.choice(STATUSES),
        }
        for index in range(count)
    ]


def write_output(records: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".json":
        output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    elif output.suffix.lower() == ".csv":
        with output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    else:
        raise ValueError("Output extension must be .csv or .json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate privacy-safe hospital demo devices")
    parser.add_argument("--count", type=int, choices=[1000, 10000, 100000], default=1000)
    parser.add_argument("--seed", type=int, default=20261017)
    parser.add_argument("--output", type=Path, default=Path("data/demo_devices.csv"))
    args = parser.parse_args()
    write_output(generate_devices(args.count, args.seed), args.output)
    print(f"generated={args.count} output={args.output}")


if __name__ == "__main__":
    main()
