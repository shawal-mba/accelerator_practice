import csv
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, fields, field
from typing import Optional

BEFORE_XML = "./MAP_before_Test_3.xml"
AFTER_XML = "./MAP_After_Test_3.xml"
MODELS_PATH = "./models.py"


def parse_xml(xmlfilename: str):
    tree = ET.parse(xmlfilename)
    root = tree.getroot()

    parsed_items = []

    for obj in root.findall(".//Object"):
        obj_class = obj.attrib.get("class", "Unknown_Class")

        obj_data = {"object_class": obj_class.split(".")[-1], "fields": {}}

        for field_el in obj.findall("Field"):
            field_name = field_el.attrib.get("name", "Unknown_field")

            field_value = (
                field_el.text.strip()
                if field_el.text and field_el.text.strip()
                else None
            )
            obj_data["fields"][field_name] = field_value
        parsed_items.append(obj_data)
    return parsed_items


def discover_classes(xmlfilename: str) -> dict[str, set[str]]:
    items = parse_xml(xmlfilename)
    class_fields: dict[str, set[str]] = {}
    for item in items:
        cls = item["object_class"]
        if cls not in class_fields:
            class_fields[cls] = set()
        class_fields[cls].update(item["fields"].keys())
    return class_fields


def generate_models(all_class_fields: dict[str, set[str]], output_path: str):
    sorted_classes = sorted(all_class_fields.keys())

    lines = [
        "# AUTO-GENERATED - DO NOT EDIT",
        "# Regenerate by running: python main.py",
        "",
        "from dataclasses import dataclass, field",
        "from typing import Optional",
        "",
        "",
    ]

    for cls_name in sorted_classes:
        field_names = sorted(all_class_fields[cls_name])
        lines.append(f'@dataclass')
        lines.append(f"class {cls_name}:")
        lines.append(f'    object_class: str = "{cls_name}"')
        for fname in field_names:
            safe_name = fname.lower()
            lines.append(f"    {safe_name}: Optional[str] = None")
        lines.append("")
        lines.append("    @classmethod")
        lines.append("    def from_dict(cls, data: dict) -> \"{}\"".format(cls_name))
        lines.append("        return cls(**{")
        lines.append('            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}')
        lines.append("        })")
        lines.append("")
        lines.append("")
        lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))


def save_csv_per_class(items: list[dict], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    grouped: dict[str, list[dict]] = {}
    for item in items:
        cls = item["object_class"]
        if cls not in grouped:
            grouped[cls] = []
        grouped[cls].append(item)

    for cls_name, cls_items in sorted(grouped.items()):
        all_fields = set()
        for item in cls_items:
            all_fields.update(item["fields"].keys())
        sorted_fields = sorted(all_fields)

        filepath = os.path.join(output_dir, f"{cls_name}.csv")
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["object_class"] + sorted_fields)
            for item in cls_items:
                row = [item["object_class"]]
                row.extend(item["fields"].get(f, "") for f in sorted_fields)
                writer.writerow(row)

        print(f"  {cls_name}.csv: {len(cls_items)} rows")


def main():
    print("Discovering classes from XML files...")
    before_classes = discover_classes(BEFORE_XML)
    after_classes = discover_classes(AFTER_XML)

    all_class_fields: dict[str, set[str]] = {}
    for class_fields in [before_classes, after_classes]:
        for cls, flds in class_fields.items():
            if cls not in all_class_fields:
                all_class_fields[cls] = set()
            all_class_fields[cls].update(flds)

    print(f"Found {len(all_class_fields)} classes: {', '.join(sorted(all_class_fields.keys()))}")

    print(f"\nGenerating models.py...")
    generate_models(all_class_fields, MODELS_PATH)
    print(f"Saved {MODELS_PATH}")

    print(f"\nParsing and saving per-class CSVs...")
    before_items = parse_xml(BEFORE_XML)
    after_items = parse_xml(AFTER_XML)

    print(f"\nBefore XML ({len(before_items)} total objects):")
    save_csv_per_class(before_items, "output/before")

    print(f"\nAfter XML ({len(after_items)} total objects):")
    save_csv_per_class(after_items, "output/after")

    print("\nDone.")


if __name__ == "__main__":
    main()
