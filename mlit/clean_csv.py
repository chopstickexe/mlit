import argparse
import csv
import io

from .crawler import Normalizer


def clean_csv(input_data: str) -> str:
    """
    Clean CSV data by removing extra whitespace from all fields.
    
    Args:
        input_data: CSV data as string
        
    Returns:
        Cleaned CSV data as string
    """
    input_file = io.StringIO(input_data)
    output_file = io.StringIO()
    
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)
    
    for row in reader:
        cleaned_row = [Normalizer.remove_spaces(field) for field in row]
        writer.writerow(cleaned_row)
    
    result = output_file.getvalue()
    input_file.close()
    output_file.close()
    
    return result


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("original_path", help="path to the original csv")
    parser.add_argument("new_path", help="path to the generated csv")
    return parser.parse_args()


def main():
    args = get_args()
    original_path = args.original_path
    new_path = args.new_path

    with open(original_path, newline="", encoding="UTF-8") as of, open(
        new_path, "w", encoding="UTF-8"
    ) as nf:
        reader = csv.DictReader(of)
        writer = csv.DictWriter(nf, fieldnames=reader.fieldnames)
        writer.writeheader()
        for record in reader:
            new_record = {}
            for k, v in record.items():
                v = Normalizer.remove_spaces(v)
                new_record[k] = v
            writer.writerow(new_record)


if __name__ == "__main__":
    main()
