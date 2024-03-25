import base64
import binascii
import struct


def validate_pubkey(pub_key: str) -> bool:

    split = pub_key.split(" ")
    if len(split) < 2:
        return False
    type, key_string = split[0:2]
    try:
        data = base64.b64decode(key_string, validate=True)
    except binascii.Error:
        return False
    int_len = 4
    if len(data) < int_len:
        return False
    str_len = struct.unpack(">I", data[:int_len])[0]  # this should return 7
    return data[int_len : int_len + str_len].decode() == type
