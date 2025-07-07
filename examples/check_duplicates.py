from pathlib import Path
from collections import Counter

input_dir = "~/sources/sandbox/marinetraffic/uncompressed/"
input_file = "marinetraffic_20250615_000225_a1c06c29-8a6c-4611-92b1-13ceccc7d5d9.nmea"
input_path = Path(input_dir).expanduser() / Path(input_file)


def check_duplicates(lines):
    counter = Counter(lines)
    duplicates = {line: count for line, count in counter.items() if count > 1}
    if duplicates:
        print(f"Found {len(duplicates)} duplicated lines:")
    else:
        print("No duplicated lines found.")


with open(input_path, 'r', encoding='utf-8') as f:
    raw_lines = [line.strip() for line in f if line.strip()]

check_duplicates(raw_lines)
