import csv
import xml.etree.ElementTree as ET

BEFORE_XML = "./MAP_before_Test_3.xml"
AFTER_XML = "./MAP_After_Test_3.xml"


def parse_xml(xmlfilename: str):
    tree = ET.parse(xmlfilename)
    root = tree.getroot()

    parsed_items = []

    for obj in root.findall(".//Object"):
        obj_class = obj.attrib.get("class", "Unknown_Class")

        obj_data = {"object_class": obj_class.split(".")[-1], "fields": {}}

        for field in obj.findall("Field"):
            field_name = field.attrib.get("name", "Unknown_field")

            field_value = (
                field.text.strip() if field.text and field.text.strip() else None
            )
            obj_data["fields"][field_name] = field_value
        parsed_items.append(obj_data)
    return parsed_items

def save_csv(items, filename):
    all_fields = set()
    for item in items:
        all_fields.update(item["fields"].keys())
    sorted_fields = sorted(all_fields)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["object_class"] + sorted_fields)
        for item in items:
            row = [item["object_class"]]
            row.extend(item["fields"].get(f, "") for f in sorted_fields)
            writer.writerow(row)

def main():
    before_items = parse_xml(BEFORE_XML)
    after_items = parse_xml(AFTER_XML)
    save_csv(before_items, "before_output.csv")
    save_csv(after_items, "after_output.csv")
    print(f"Saved {len(before_items)} items to before_output.csv")
    print(f"Saved {len(after_items)} items to after_output.csv")


if __name__ == "__main__":
    main()
