from ais_tools.tagblock import split_tagblock
from ais_tools.tagblock import decode_tagblock
from ais_tools.tagblock import encode_tagblock
from ais_tools.tagblock import join_tagblock
from ais_tools.ais import DecodeError


def update_tagblock(nmea, source, timestamp, ip_address):
    tagblock_str, nmea = split_tagblock(nmea)
    if tagblock_str:
        tagblock = decode_tagblock(tagblock_str)
        tagblock['tagblock_text'] = source
        if 'tagblock_timestamp' not in tagblock:
            tagblock['tagblock_timestamp'] = int(timestamp)
        if 'tagblock_station' not in tagblock:
            tagblock['tagblock_station'] = ip_address
    else:
        tagblock = dict(tagblock_text=source,
                        tagblock_station=ip_address,
                        tagblock_timestamp=int(timestamp))
    tagblock_str = encode_tagblock(**tagblock)
    return join_tagblock(tagblock_str, nmea)


def format_nmea(messages, source):
    for message, addr, timestamp, port in messages:
        lines = (line.strip() for line in message.split('\n'))
        lines = (line for line in lines if line)
        for line in lines:
            try:
                line = update_tagblock(line, source, timestamp, addr)
            except DecodeError:
                pass  # If we are unable to decode an existing tagblock, then just pass through the
                # original message unmodified
            yield line
