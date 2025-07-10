"""Utilities package."""
import re
from collections import deque

from typing import Iterable, Generator, List


NMEA_PREFIXES = (
    "ABVDM",
    "ABVDO",
    "AIVDM",
    "AIVDO",
    "ANVDM",
    "ANVDO",
    "BSVDM",
    "BSVDO",
)

# Extract prefix names without the "!" and join with |
nmea_prefixes_pattern = '|'.join(prefix for prefix in NMEA_PREFIXES)

MULTIPART_REGEX = re.compile(
    rf'^!(?:{nmea_prefixes_pattern}),(?P<total>\d+),(?P<part>\d+),(?P<seq_id>[^,]*),'
)


def find_nmea_start(line: str) -> int:
    for prefix in NMEA_PREFIXES:
        pos = line.find(f"!{prefix}")
        if pos != -1:
            return pos

    return -1


def chunked_nmea_it(
    lines: Iterable[str],
    max_lines_per_packet: int = 20
) -> Generator[List[str], None, None]:
    r"""Splits a stream of NMEA sentences into packets of up to `max_lines_per_packet`
    without splitting multipart messages.

    This functions expects an input like:
    ```text
    \s:rMT7892,t:marinetraffic,c:1749945745*45\!AIVDM,1,1,,A,13m0Nj01C@WPIfR1>5d0phnd00SN,0*44
    \s:rMT9999,t:marinetraffic,c:1749945745*41\!AIVDM,2,1,2,B,569@?q00000091Ho@00HDUPTtpOF222222222216>@DB45Vh0<0hCiQBA2@C,0*42
    ```

    So, for single-part sentences we have an empty slot in the tagblock for the .

    Args:
        lines:
            An iterable of NMEA sentence strings.

        max_lines_per_packet:
            Maximum number of sentences per packet.

    Yields:
        Lists of NMEA sentences representing one packet.
    """
    packet = []
    buffer = deque()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        nmea_start = find_nmea_start(line)
        if nmea_start == -1:
            raise ValueError(f"Line with NMEA prefix not recognized: {line}")

        core = line[nmea_start:]
        match = MULTIPART_REGEX.match(core)

        if match:  # Multipart
            part = int(match.group("part"))
            total = int(match.group("total"))
            buffer.append(line)

            if part != total:
                continue  # wait for last part

            # last part received
            multipart = list(buffer)
            buffer.clear()

            if packet and len(packet) + len(multipart) > max_lines_per_packet:
                yield packet
                packet = []

            packet.extend(multipart)
            continue
        else:
            raise ValueError(f"Line was not matched by regex: {line}")

    # flush leftovers
    if buffer:
        raise ValueError("We have buffer leftover")

    if packet:
        yield packet
