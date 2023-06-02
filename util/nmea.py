from ais_tools.tagblock import split_tagblock
from ais_tools.tagblock import decode_tagblock
from ais_tools.tagblock import encode_tagblock
from ais_tools.tagblock import join_tagblock
from ais_tools.ais import DecodeError


def update_tagblock(nmea, source, timestamp):
    tagblock_str, nmea = split_tagblock(nmea)
    if tagblock_str:
        tagblock = decode_tagblock(tagblock_str)
        tagblock['tagblock_text'] = source
        if 'tagblock_timestamp' not in tagblock:
            tagblock['tagblock_timestamp'] = int(timestamp)
    else:
        tagblock = dict(tagblock_text=source, tagblock_timestamp=int(timestamp))
    tagblock_str = encode_tagblock(**tagblock)
    return join_tagblock(tagblock_str, nmea)


def format_nmea(messages, source_ip_lookup):
    for message, source, timestamp in messages:
        source = source_ip_lookup.get(source, source)
        lines = [line for line in message.split('\n') if line]
        for line in lines:
            try:
                line = update_tagblock(line, source, timestamp)
            except DecodeError:
                pass  # If we are unable to decode an existing tagblock, then just pass through the
                # original message unmodified
            yield line

