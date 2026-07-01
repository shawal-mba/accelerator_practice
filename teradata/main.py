import csv
import sys
import sqlglot
from sqlglot import exp

# Increase the CSV field size limit in case some DDL strings are massive
csv.field_size_limit(sys.maxsize)


def parse_teradata_export_to_csv(input_csv_path: str, output_csv_path: str):
    """
    Reads a Teradata CSV metadata export, extracts the DDL from 'RequestText',
    parses it, and outputs the Column and Data Type mappings to a new CSV.
    """

    # 1. Open the output file so we can write as we parse
    with open(output_csv_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(["Database Name", "Table Name", "Column Name", "Data Type"])

        # 2. Open the input CSV file
        try:
            with open(input_csv_path, "r", encoding="utf-8") as in_f:
                # DictReader lets us easily grab columns by their header names
                reader = csv.DictReader(in_f)

                # 3. Loop through each row in your Teradata export
                for row in reader:
                    db_name = row.get("DataBaseName", "UNKNOWN_DB")
                    # Grab the actual SQL string from the 8th column
                    sql_text = row.get("RequestText", "").strip()

                    if not sql_text:
                        continue

                    # 4. Safely attempt to parse the SQL string
                    try:
                        statements = sqlglot.parse(sql_text, read="teradata")
                    except Exception as e:
                        # Skip this row if sqlglot completely fails to tokenize it
                        print(
                            f"Skipping malformed SQL in {db_name}.{row.get('TableName')}"
                        )
                        continue

                    # 5. Extract table and column data
                    for stmt in statements:
                        if not stmt:
                            continue

                        # Only process CREATE TABLE statements (ignore views, macros, etc.)
                        if (
                            isinstance(stmt, exp.Create)
                            and stmt.args.get("kind") == "TABLE"
                        ):
                            table_exp = stmt.find(exp.Table)
                            # Fallback to the CSV's TableName if the parser can't find it in the SQL
                            table_name = (
                                table_exp.sql(dialect="teradata")
                                if table_exp
                                else row.get("TableName")
                            )

                            # Find all columns inside the CREATE statement
                            for col_def in stmt.find_all(exp.ColumnDef):
                                col_name = col_def.name

                                data_type_exp = col_def.args.get("kind")
                                col_type = (
                                    data_type_exp.sql(dialect="teradata")
                                    if data_type_exp
                                    else "UNKNOWN"
                                )

                                # Write to our output file
                                writer.writerow(
                                    [db_name, table_name, col_name, col_type]
                                )

        except FileNotFoundError:
            print(f"Error: Could not find the file '{input_csv_path}'.")
            return

    print(f"Successfully processed CSV and saved results to '{output_csv_path}'.")


# ==========================================
# Execution
# ==========================================
if __name__ == "__main__":
    # Update these paths to match your actual files
    INPUT_FILE = "./metadata/dbc.TablesV.csv"
    OUTPUT_FILE = "parsed_data_dictionary.csv"

    parse_teradata_export_to_csv(INPUT_FILE, OUTPUT_FILE)
