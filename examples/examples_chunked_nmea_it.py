from pathlib import Path
from socket_listener.utils import chunked_nmea_it


def check_missing_or_extra_lines(input_lines, packets):
    reconstructed_lines = [line for packet in packets for line in packet]

    # Compare lengths
    print(f"Original input lines:       {len(input_lines)}")
    print(f"Reconstructed packet lines: {len(reconstructed_lines)}")

    # Check for missing
    input_set = set(input_lines)
    reconstructed_set = set(reconstructed_lines)

    missing_lines = input_set - reconstructed_set
    extra_lines = reconstructed_set - input_set

    print(f"Missing lines: {len(missing_lines)}")
    print(f"Extra lines:   {len(extra_lines)}")


def main():
    input_dir = "~/sources/sandbox/marinetraffic/uncompressed/"
    input_file = "marinetraffic_20250615_000225_a1c06c29-8a6c-4611-92b1-13ceccc7d5d9.nmea"
    input_path = Path(input_dir).expanduser() / Path(input_file)

    input_lines = input_path.read_text().splitlines()
    packets = list(chunked_nmea_it(input_lines, max_lines_per_packet=20))

    check_missing_or_extra_lines(input_lines, packets)


if __name__ == "__main__":
    main()
