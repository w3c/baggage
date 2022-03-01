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
        '''serialize a Baggage class into an HTML header string'''
        return ",".join([x.to_string() for x in self.entries])


class BaggageEntry(object):
    '''baggage entry class for baggage reference implementation'''
    #  token = 1*tchar
    #  tchar = "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
    _KEY_FORMAT = r'[a-zA-Z0-9!#$%&\'*+\-.\^_`|~]+'
    #  baggage-octet = %x21 / %x23-2B / %x2D-3A / %x3C-5B / %x5D-7E
    #  value = *baggage-octet
    _VALUE_FORMAT = r'[\x23-\x2b\x2d-\x3a\x3c-\x5b\x5d-\x7e\x21]*'
    _KV_FORMAT = r'(%s)[ \t]*=[ \t]*(%s)' % (_KEY_FORMAT, _VALUE_FORMAT)
    # list-member = key OWS "=" OWS value *( OWS ";" OWS property )
    _ENTRY_FORMAT_RE = re.compile(
        r'^%s[ \t]*(?:;[ \t]*(%s|%s))?$' % (_KV_FORMAT,
                                            _KV_FORMAT,
                                            _KEY_FORMAT))

    def __init__(self, key: str, value: str, property_key: str | None = None, property_value: str | None = None):
        self.key = key
        self.value = value
        self.property_key = property_key
        self.property_value = property_value

    @classmethod
    def from_string(cls, value: str) -> BaggageEntry:
        '''parse a single baggage entry into a BaggageEntry class'''
        if not isinstance(value, str):
            raise ValueError('value must be a string')

        match = re.match(BaggageEntry._ENTRY_FORMAT_RE, value)
        if match is None:
            raise ValueError('failed to parse baggage entry \'%s\'' % (value))

        key = match[1]
        value = match[2]
        property_key = match[3]
        if match[4] is not None:
            property_key = match[4]
        property_value = match[5]

        return cls(key, unquote(value), property_key, property_value)

    def to_string(self) -> str:
        '''serialize a BaggageEntry class into a string'''
        if self.property_key is not None:
            if self.property_value is not None:
                return "%s=%s;%s=%s" % (self.key, quote(self.value), self.property_key, self.property_value)
            return "%s=%s;%s" % (self.key, quote(self.value), self.property_key)
        return "%s=%s" % (self.key, quote(self.value))
