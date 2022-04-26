from __future__ import annotations

import re
from urllib.parse import quote, unquote


class Baggage(object):
    '''baggage regular expression reference implementation'''
    _DELIMITER_FORMAT_RE = re.compile('[ \t]*,[ \t]*')
    entries: list[BaggageEntry] = []

    def __init__(self, entries: list[BaggageEntry] | None = None):
        if entries is not None:
            self.entries = entries

    @classmethod
    def from_string(cls, value: str) -> Baggage:
        '''parse a valid baggage string into a Baggage class'''
        if not isinstance(value, str):
            raise ValueError('value must be a string')

        # list-member 0*179( OWS "," OWS list-member )
        value = re.split(Baggage._DELIMITER_FORMAT_RE, value)
        return Baggage([BaggageEntry.from_string(s) for s in value])

    def to_string(self) -> str:
        '''
        Serialize a Baggage class into an HTML header string

        Only the first 180 entries will be serialized even if more than 180 entries exist in the list.
        Entries will only be included until the limit of 8192 bytes is reached.
        Entries which serialize longer than the 4096 byte limit per entry are skipped.
        '''
        out = ""
        for i, entry in enumerate(self.entries):
            entry_str = entry.to_string()

            # Prepend delimiter on all but the first entry
            if i > 0:
                out += ","
            out += entry_str

        return out


class BaggageEntry(object):
    '''baggage entry class for baggage reference implementation'''
    #  token = 1*tchar
    #  tchar = "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
    _KEY_FORMAT = r'[a-zA-Z0-9!#$%&\'*+\-.\^_`|~]+'
    #  baggage-octet = %x21 / %x23-2B / %x2D-3A / %x3C-5B / %x5D-7E
    #  value = *baggage-octet
    _VALUE_FORMAT = r'[\x23-\x2b\x2d-\x3a\x3c-\x5b\x5d-\x7e\x21]*'

    # list-member = key OWS "=" OWS value *( OWS ";" OWS property )
    _DELIMITER_FORMAT_RE = re.compile(r'[ \t]*;[ \t]*')
    _KV_FORMAT_RE = re.compile(
        r'^(%s)[ \t]*=[ \t]*(%s)$' % (_KEY_FORMAT, _VALUE_FORMAT))
    _KEY_RE = re.compile(r'^%s$' % _KEY_FORMAT)

    def __init__(self, key: str, value: str, properties: list[BaggageEntryProperty] = None):
        self.key = key
        self.value = value
        self.properties = properties or []

    @classmethod
    def from_string(cls, value: str) -> BaggageEntry:
        '''parse a single baggage entry into a BaggageEntry class'''
        if not isinstance(value, str):
            raise ValueError('value must be a string')

        split_strs = re.split(BaggageEntry._DELIMITER_FORMAT_RE, value)
        kv = split_strs[0]
        property_strs = split_strs[1:]

        kv_match = re.match(BaggageEntry._KV_FORMAT_RE, kv.rstrip(" \t"))

        if kv_match is None:
            raise ValueError('failed to parse baggage entry key-value pair \'%s\'' % kv)

        key, value = kv_match[1], kv_match[2]

        properties = []

        for s in property_strs:
            key_match = re.match(BaggageEntry._KEY_RE, s)
            kv_match = re.match(BaggageEntry._KV_FORMAT_RE, s)
            if key_match is not None:
                properties.append(BaggageEntryProperty(s))
            elif kv_match is not None:
                properties.append(BaggageEntryProperty(
                    kv_match[1], kv_match[2]))
            else:
                raise ValueError('property %s could not be parsed')

        return cls(key, unquote(value), properties)

    def to_string(self) -> str:
        '''serialize a BaggageEntry class into a string'''
        s = "%s=%s" % (self.key, quote(self.value))
        for prop in self.properties:
            s += ";%s" % prop.to_string()
        return s


class BaggageEntryProperty(object):
    def __init__(self, key: str, value: str = None) -> None:
        self.key = key
        self.value = value

    def to_string(self):
        if self.value is None:
            return self.key

        return '%s=%s' % (self.key, self.value)
