#!/usr/bin/env python3
"""Create wheat-only preview copies of Hay Day recipe CSVs.

This script does NOT edit source CSVs. It reads data/*_goods.csv and writes
transformed copies under wheat_only_preview/data/.
For each product, all ingredient quantities are added together and represented
as Wheat. Product metadata (time, price, XP, unlock level, IDs, etc.) is kept.
This is an offline data-preview tool; it does not modify or affect the live game.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "wheat_only_preview" / "data"


def transform_file(source: Path, destination: Path) -> tuple[int, int, str]:
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    if len(rows) < 2:
        return 0, 0, "too few rows"

    header = rows[0]
    if "Name" not in header or "Requirement" not in header or "RequirementAmount" not in header:
        return 0, 0, "not a recipe table"

    name_i = header.index("Name")
    req_i = header.index("Requirement")
    amount_i = header.index("RequirementAmount")

    output = rows[:2]  # Keep column names and the source type-definition row.
    current: list[list[str]] = []
    changed = 0
    skipped = 0

    def flush_product(block: list[list[str]]) -> None:
        nonlocal changed, skipped
        if not block:
            return

        ingredient_rows: list[tuple[list[str], int]] = []
        for row in block:
            if len(row) <= max(req_i, amount_i):
                continue
            requirement = row[req_i].strip()
            amount_text = row[amount_i].strip()
            if requirement:
                try:
                    amount = int(amount_text)
                except (TypeError, ValueError):
                    skipped += 1
                    output.extend(block)
                    return
                ingredient_rows.append((row, amount))

        if not ingredient_rows:
            skipped += 1
            output.extend(block)
            return

        product_row = block[0][:]
        total_amount = sum(amount for _, amount in ingredient_rows)
        product_row[req_i] = "Wheat"
        product_row[amount_i] = str(total_amount)
        output.append(product_row)
        changed += 1

    for row in rows[2:]:
        if not row or not any(cell.strip() for cell in row):
            continue
        name = row[name_i].strip() if len(row) > name_i else ""
        if name:
            flush_product(current)
            current = [row]
        elif current:
            current.append(row)
        else:
            # Preserve any non-product rows that occur outside a product block.
            output.append(row)

    flush_product(current)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(output)

    return changed, skipped, "processed"


def main() -> None:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"Could not find source folder: {SOURCE_DIR}")

    total_products = 0
    total_skipped = 0
    processed_files = 0
    ignored_files = 0

    for source in sorted(SOURCE_DIR.glob("*_goods.csv")):
        destination = OUTPUT_DIR / source.name
        changed, skipped, status = transform_file(source, destination)
        if status == "processed":
            processed_files += 1
            total_products += changed
            total_skipped += skipped
            print(f"{source.name}: {changed} products converted; {skipped} left unchanged")
        else:
            ignored_files += 1
            print(f"{source.name}: skipped ({status})")

    print("\nPreview generation complete.")
    print(f"Files processed: {processed_files}")
    print(f"Files ignored: {ignored_files}")
    print(f"Products converted: {total_products}")
    print(f"Products left unchanged: {total_skipped}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
