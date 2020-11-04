import argparse
import csv
from crawler import Normalizer

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("original_path", help="path to the original csv")
    parser.add_argument("new_path", help="path to the generated csv")
    return parser.parse_args()

def main():
    args = get_args()
    original_path = args.original_path
    new_path = args.new_path

    
    with open(original_path, newline="", encoding="UTF-8") as of, open(new_path, "w", encoding="UTF-8") as nf:
        reader = csv.DictReader(of)
        writer = csv.DictWriter(nf, fieldnames = reader.fieldnames)
        for record in reader:
            new_record = {}
            for k, v in record.items():
                v = Normalizer.remove_spaces(v)
                new_record[k] = v
            writer.writerow(new_record)


if __name__ == "__main__":
    main()