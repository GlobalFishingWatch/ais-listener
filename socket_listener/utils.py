"""Utilities package."""
import re
from collections import deque

from typing import Iterable, Generator, List


def pretty_print_args(args: dict) -> str:
    """Returns a dictionary as string, pretty printed."""
    arg_str = "\n".join(f"  {k}={v}" for k, v in args.items())

    return f"Executing with parameters:\n{arg_str}"


# Regex to parse multipart message headers like: $--GPTXT,x,y,z,...
MULTIPART_REGEX = re.compile(
    r'^!AIVDM,(?P<total>\d+),(?P<part>\d+),(?P<seq_id>[^,]*),'
)


def chunked_nmea_it(
    lines: Iterable[str],
    max_lines_per_packet: int = 20
) -> Generator[List[str], None, None]:
    """Splits a stream of NMEA sentences into packets of up to `max_lines_per_packet`
    without splitting multipart messages.

    Args:
        lines:
            An iterable of NMEA sentence strings.

        max_lines_per_packet:
            Maximum number of sentences per packet.

    Yields:
        Lists of NMEA sentences representing one packet.
    """
    packet = []
    multipart_buffer = deque()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        nmea_start = line.find("!AIVDM")
        if nmea_start == -1:
            continue  # skip invalid lines

        core = line[nmea_start:]
        match = MULTIPART_REGEX.match(core)

        if match:
            part = int(match.group("part"))
            total = int(match.group("total"))
            multipart_buffer.append(line)

            if part != total:
                continue  # wait for last part

            # last part received
            multipart = list(multipart_buffer)
            multipart_buffer.clear()

            if packet and len(packet) + len(multipart) > max_lines_per_packet:
                yield packet
                packet = []

            packet.extend(multipart)
            continue

        # single part line
        if packet and len(packet) + 1 > max_lines_per_packet:
            yield packet
            packet = []

        packet.append(line)

    # flush leftovers
    if multipart_buffer:
        packet.extend(multipart_buffer)
        multipart_buffer.clear()

    if packet:
        yield packet
