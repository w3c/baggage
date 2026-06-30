import unittest
import urllib.parse

from baggage import Baggage, BaggageEntry

# Number of iterations for tests that exercise random behavior
_ITERATIONS = 20


class BaggageTest(unittest.TestCase):
    def test_ctor_default(self):
        baggage = Baggage()
        self.assertEqual(baggage.entries, [])

    def test_parse_simple(self):
        baggage = Baggage().from_string("SomeKey=SomeValue")
        self.assertEqual(len(baggage.entries), 1)
        entry = baggage.entries[0]
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 0)

    def test_parse_multiple(self):
        baggage = Baggage().from_string(
            "SomeKey=SomeValue;SomeProp,SomeKey2=SomeValue2;ValueProp=PropVal")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]

        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(len(entry1.properties), 1)
        self.assertEqual(entry1.properties[0].key, "SomeProp")
        self.assertEqual(entry1.properties[0].value, None)

        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(len(entry2.properties), 1)
        self.assertEqual(entry2.properties[0].key, "ValueProp")
        self.assertEqual(entry2.properties[0].value, "PropVal")

    def test_parse_multiple_ows(self):
        baggage = Baggage().from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomeProp \t , \t SomeKey2 \t = \t SomeValue2 \t ; \t ValueProp \t = \t PropVal")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]

        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(len(entry1.properties), 1)
        self.assertEqual(entry1.properties[0].key, "SomeProp")
        self.assertEqual(entry1.properties[0].value, None)

        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(len(entry2.properties), 1)
        self.assertEqual(entry2.properties[0].key, "ValueProp")
        self.assertEqual(entry2.properties[0].value, "PropVal")

    def test_parse_multiple_kv_property(self):
        baggage = Baggage().from_string(
            "SomeKey=SomeValue;SomePropKey=SomePropValue,SomeKey2=SomeValue2;SomePropKey2=SomePropValue2")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.properties[0].key, "SomePropKey")
        self.assertEqual(entry1.properties[0].value, "SomePropValue")
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.properties[0].key, "SomePropKey2")
        self.assertEqual(entry2.properties[0].value, "SomePropValue2")

    def test_parse_multiple_kv_property_ows(self):
        baggage = Baggage().from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomePropKey=SomePropValue \t , \t SomeKey2 \t = \t SomeValue2 \t ; \t SomePropKey2 \t = \t SomePropValue2")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.properties[0].key, "SomePropKey")
        self.assertEqual(entry1.properties[0].value, "SomePropValue")
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.properties[0].key, "SomePropKey2")
        self.assertEqual(entry2.properties[0].value, "SomePropValue2")


class BaggageEntryTest(unittest.TestCase):
    def test_ctor_default(self):
        entry = BaggageEntry("SomeKey", "SomeValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 0)

    def test_parse_simple(self):
        entry = BaggageEntry.from_string("SomeKey=SomeValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 0)

    def test_parse_multiple_equals(self):
        entry = BaggageEntry.from_string("SomeKey=SomeValue=equals")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue=equals")
        self.assertEqual(len(entry.properties), 0)

    def test_parse_percent_encoded(self):
        value = "\t \"\';=asdf!@#$%^&*()"
        encoded_value = urllib.parse.quote(value)
        # Verify that parsing a baggage header received from upstream via from_string decodes the baggage value with
        # respect to percent-encoding.
        entry = BaggageEntry.from_string("SomeKey=%s" % (encoded_value))
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, value)
        # Verify that serializing a baggage header via to_string before sending it downstream applies percent-encoding.
        self.assertEqual(entry.to_string(
        ), "SomeKey=%09%20%22%27%3B%3Dasdf%21%40%23%24%25%5E%26%2A%28%29")

    def test_parse_property(self):
        entry = BaggageEntry.from_string("SomeKey=SomeValue;SomeProp")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 1)
        self.assertEqual(entry.properties[0].key, "SomeProp")

    def test_parse_multi_property(self):
        entry = BaggageEntry.from_string(
            "SomeKey=SomeValue;SomeProp;SecondProp=PropValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 2)
        self.assertEqual(entry.properties[0].key, "SomeProp")
        self.assertEqual(entry.properties[0].value, None)
        self.assertEqual(entry.properties[1].key, "SecondProp")
        self.assertEqual(entry.properties[1].value, 'PropValue')

    def test_parse_multiple_properties_same_name(self):
        entry = BaggageEntry.from_string(
            "SomeKey=SomeValue;SomeProp;SomeProp=PropValue;SomeProp=AnotherPropValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 3)
        self.assertEqual(entry.properties[0].key, "SomeProp")
        self.assertEqual(entry.properties[0].value, None)
        self.assertEqual(entry.properties[1].key, "SomeProp")
        self.assertEqual(entry.properties[1].value, "PropValue")
        self.assertEqual(entry.properties[2].key, "SomeProp")
        self.assertEqual(entry.properties[2].value, "AnotherPropValue")

    def test_parse_kv_property(self):
        entry = BaggageEntry.from_string(
            "SomeKey=SomeValue;SomePropKey=SomePropValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 1)
        self.assertEqual(entry.properties[0].key, "SomePropKey")
        self.assertEqual(entry.properties[0].value, "SomePropValue")

    def test_parse_simple_ows(self):
        entry = BaggageEntry.from_string("SomeKey \t = \t SomeValue \t ")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 0)

    def test_parse_percent_encoded_ows(self):
        value = "\t \"\';=asdf!@#$%^&*()"
        encoded_value = urllib.parse.quote(value)
        entry = BaggageEntry.from_string(
            "SomeKey \t = \t %s \t " % (encoded_value))
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, value)

    def test_parse_property_ows(self):
        entry = BaggageEntry.from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomeProp")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 1)
        self.assertEqual(entry.properties[0].key, "SomeProp")

    def test_parse_multi_property_ows(self):
        entry = BaggageEntry.from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomeProp \t ; \t SecondProp \t = \t PropValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 2)
        self.assertEqual(entry.properties[0].key, "SomeProp")
        self.assertEqual(entry.properties[0].value, None)
        self.assertEqual(entry.properties[1].key, "SecondProp")
        self.assertEqual(entry.properties[1].value, 'PropValue')

    def test_parse_kv_property_ows(self):
        entry = BaggageEntry.from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomePropKey \t = \t SomePropValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 1)
        self.assertEqual(entry.properties[0].key, "SomePropKey")
        self.assertEqual(entry.properties[0].value, "SomePropValue")

    def test_parse_percent_encoded_property(self):
        property_value = "\t \"\';=asdf!@#$%^&*()"
        encoded_property_value = urllib.parse.quote(property_value)
        # Verify that parsing a baggage header received from upstream via from_string decodes the property value with
        # respect to percent-encoding.
        entry = BaggageEntry.from_string("SomeKey=SomeValue;SomePropKey=%s" % (encoded_property_value))
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(len(entry.properties), 1)
        self.assertEqual(entry.properties[0].key, "SomePropKey")
        self.assertEqual(entry.properties[0].value, property_value)
        # Verify that serializing a baggage header via to_string before sending it downstream applies percent-encoding
        # to the property value if necessary.
        self.assertEqual(entry.to_string(),
          "SomeKey=SomeValue;SomePropKey=%09%20%22%27%3B%3Dasdf%21%40%23%24%25%5E%26%2A%28%29")

    def test_parse_property_without_value_no_percent_decoding(self):
        # This looks like an upstream participant percent-encoded the inner OWS and the equals character of a property
        # key-value pair. The correct behavior is to treat this as one property of the form `key`, and to not ttempt to
        # decode it back into a key-value shaped property (`key OWS "=" OWS value`).
        entry = BaggageEntry.from_string(
            "SomeKey=SomeValue;ValueProp%20%09%20%3D%20%09%20PropVal")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(entry.properties[0].key, "ValueProp%20%09%20%3D%20%09%20PropVal")
        self.assertEqual(entry.properties[0].value, None)

class InvalidEntryTest(unittest.TestCase):
    '''Behavior for invalid baggage-string is undefined per spec.
    Implementation may preserve the entry as-is or drop it.'''

    def test_just_key_no_equals(self):
        '''A bare key without = is not valid per ABNF. The serialized result
        MUST be either the original string (preserved) or empty (dropped).'''
        for run in range(_ITERATIONS):
            with self.subTest(iteration=run):
                baggage = Baggage.from_string("justKey")
                baggage_str = baggage.to_string()
                self.assertIn(baggage_str, ["justKey", ""])

    def test_just_key_among_valid_entries(self):
        '''An invalid entry among valid ones: valid entries MUST be preserved,
        invalid entry is either kept as-is or dropped.'''
        for run in range(_ITERATIONS):
            with self.subTest(iteration=run):
                baggage = Baggage.from_string("k1=v1,justKey,k2=v2")
                keys = [e.key for e in baggage.entries]
                # Valid entries must always be present
                self.assertIn("k1", keys)
                self.assertIn("k2", keys)
                # justKey is either preserved or dropped
                if "justKey" in keys:
                    self.assertEqual(len(baggage.entries), 3)
                else:
                    self.assertEqual(len(baggage.entries), 2)
                # Serialized form must only contain valid entries or preserved raw entries
                baggage_str = baggage.to_string()
                self.assertIn("k1=v1", baggage_str)
                self.assertIn("k2=v2", baggage_str)


class EmptyValueTest(unittest.TestCase):
    '''value = *baggage-octet allows zero-length values'''

    def test_parse_empty_value(self):
        '''key= is valid per ABNF: value = *baggage-octet (zero or more)'''
        entry = BaggageEntry.from_string("SomeKey=")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "")
        self.assertEqual(len(entry.properties), 0)

    def test_parse_empty_value_with_property(self):
        entry = BaggageEntry.from_string("SomeKey=;SomeProp")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "")
        self.assertEqual(len(entry.properties), 1)
        self.assertEqual(entry.properties[0].key, "SomeProp")

    def test_parse_empty_value_ows(self):
        entry = BaggageEntry.from_string("SomeKey \t = \t ")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "")

    def test_serialize_empty_value(self):
        baggage = Baggage([BaggageEntry("SomeKey", "")])
        baggage_str = baggage.to_string()
        self.assertEqual(baggage_str, "SomeKey=")

    def test_roundtrip_empty_value(self):
        baggage = Baggage.from_string("SomeKey=")
        self.assertEqual(len(baggage.entries), 1)
        self.assertEqual(baggage.entries[0].key, "SomeKey")
        self.assertEqual(baggage.entries[0].value, "")
        self.assertEqual(baggage.to_string(), "SomeKey=")


class DuplicateKeysTest(unittest.TestCase):
    '''Uniqueness of keys between multiple list-members in a baggage-string is not guaranteed.'''

    def test_parse_duplicate_keys(self):
        '''Both entries with the same key MUST be preserved.'''
        baggage = Baggage.from_string("key=value1,key=value2")
        self.assertEqual(len(baggage.entries), 2)
        self.assertEqual(baggage.entries[0].key, "key")
        self.assertEqual(baggage.entries[0].value, "value1")
        self.assertEqual(baggage.entries[1].key, "key")
        self.assertEqual(baggage.entries[1].value, "value2")

    def test_parse_duplicate_keys_preserves_order(self):
        '''The order of duplicate entries SHOULD be preserved.'''
        baggage = Baggage.from_string("k=first,k=second,k=third")
        self.assertEqual(len(baggage.entries), 3)
        self.assertEqual(baggage.entries[0].value, "first")
        self.assertEqual(baggage.entries[1].value, "second")
        self.assertEqual(baggage.entries[2].value, "third")

    def test_parse_duplicate_keys_with_different_properties(self):
        baggage = Baggage.from_string("key=value1;prop1,key=value2;prop2=val")
        self.assertEqual(len(baggage.entries), 2)
        self.assertEqual(baggage.entries[0].properties[0].key, "prop1")
        self.assertEqual(baggage.entries[1].properties[0].key, "prop2")
        self.assertEqual(baggage.entries[1].properties[0].value, "val")


class InvalidUtf8ReplacementTest(unittest.TestCase):
    '''When decoding the value, percent-encoded octet sequences that do not
    match the UTF-8 encoding scheme MUST be replaced with the replacement
    code point (U+FFFD).'''

    def test_invalid_utf8_single_continuation_byte(self):
        '''%80 is not a valid UTF-8 start byte, MUST be replaced with U+FFFD.'''
        entry = BaggageEntry.from_string("key=%80")
        self.assertEqual(entry.value, "\ufffd")

    def test_invalid_utf8_truncated_sequence(self):
        '''%C3 without continuation byte is invalid UTF-8, MUST be replaced with U+FFFD.'''
        entry = BaggageEntry.from_string("key=%C3")
        self.assertEqual(entry.value, "\ufffd")

    def test_invalid_utf8_surrounded_by_valid(self):
        '''Invalid byte in the middle of valid ASCII should only affect the invalid part.'''
        entry = BaggageEntry.from_string("key=hello%80world")
        self.assertEqual(entry.value, "hello\ufffdworld")

    def test_invalid_utf8_in_property_value(self):
        '''Property values MUST also replace invalid UTF-8 with U+FFFD.'''
        entry = BaggageEntry.from_string("key=value;prop=%80")
        self.assertEqual(entry.properties[0].value, "\ufffd")


class SpecExamplesTest(unittest.TestCase):
    '''Test the examples from the specification itself.'''

    def test_example_single_header(self):
        '''Spec example: userId=alice,serverNode=DF%2028,isProduction=false'''
        baggage = Baggage.from_string(
            "userId=alice,serverNode=DF%2028,isProduction=false")
        self.assertEqual(len(baggage.entries), 3)
        self.assertEqual(baggage.entries[0].key, "userId")
        self.assertEqual(baggage.entries[0].value, "alice")
        self.assertEqual(baggage.entries[1].key, "serverNode")
        self.assertEqual(baggage.entries[1].value, "DF 28")
        self.assertEqual(baggage.entries[2].key, "isProduction")
        self.assertEqual(baggage.entries[2].value, "false")

    def test_example_unicode_value(self):
        '''Spec example: userId=Am%C3%A9lie,serverNode=DF%2028,isProduction=false'''
        baggage = Baggage.from_string(
            "userId=Am%C3%A9lie,serverNode=DF%2028,isProduction=false")
        self.assertEqual(len(baggage.entries), 3)
        self.assertEqual(baggage.entries[0].key, "userId")
        self.assertEqual(baggage.entries[0].value, "Am\u00e9lie")
        self.assertEqual(baggage.entries[1].key, "serverNode")
        self.assertEqual(baggage.entries[1].value, "DF 28")
        self.assertEqual(baggage.entries[2].key, "isProduction")
        self.assertEqual(baggage.entries[2].value, "false")

    def test_example_with_properties(self):
        '''Spec example: key1=value1;property1;property2, key2 = value2, key3=value3; propertyKey=propertyValue'''
        baggage = Baggage.from_string(
            "key1=value1;property1;property2, key2 = value2, key3=value3; propertyKey=propertyValue")
        self.assertEqual(len(baggage.entries), 3)

        self.assertEqual(baggage.entries[0].key, "key1")
        self.assertEqual(baggage.entries[0].value, "value1")
        self.assertEqual(len(baggage.entries[0].properties), 2)
        self.assertEqual(baggage.entries[0].properties[0].key, "property1")
        self.assertEqual(baggage.entries[0].properties[1].key, "property2")

        self.assertEqual(baggage.entries[1].key, "key2")
        self.assertEqual(baggage.entries[1].value, "value2")
        self.assertEqual(len(baggage.entries[1].properties), 0)

        self.assertEqual(baggage.entries[2].key, "key3")
        self.assertEqual(baggage.entries[2].value, "value3")
        self.assertEqual(len(baggage.entries[2].properties), 1)
        self.assertEqual(baggage.entries[2].properties[0].key, "propertyKey")
        self.assertEqual(baggage.entries[2].properties[0].value, "propertyValue")

    def test_example_ows_in_values(self):
        '''Spec example: values and names might begin and end with spaces.'''
        baggage = Baggage.from_string("userId =   alice")
        self.assertEqual(baggage.entries[0].key, "userId")
        self.assertEqual(baggage.entries[0].value, "alice")

    def test_example_multiple_headers_combined(self):
        '''Spec: multiple baggage headers combined per RFC 7230 comma-folding.'''
        # When multiple headers arrive, the HTTP layer combines them as:
        # "userId=alice, serverNode=DF%2028, isProduction=false"
        baggage = Baggage.from_string(
            "userId=alice, serverNode=DF%2028, isProduction=false")
        self.assertEqual(len(baggage.entries), 3)
        self.assertEqual(baggage.entries[0].key, "userId")
        self.assertEqual(baggage.entries[0].value, "alice")
        self.assertEqual(baggage.entries[1].key, "serverNode")
        self.assertEqual(baggage.entries[1].value, "DF 28")
        self.assertEqual(baggage.entries[2].key, "isProduction")
        self.assertEqual(baggage.entries[2].value, "false")


class RoundTripTest(unittest.TestCase):
    '''Parse then serialize should preserve key/value semantics.'''

    def test_roundtrip_simple(self):
        original = "key=value"
        baggage = Baggage.from_string(original)
        result = Baggage.from_string(baggage.to_string())
        self.assertEqual(result.entries[0].key, "key")
        self.assertEqual(result.entries[0].value, "value")

    def test_roundtrip_percent_encoded_value(self):
        '''Values requiring percent-encoding should survive a round-trip.'''
        baggage = Baggage.from_string("key=hello%20world")
        self.assertEqual(baggage.entries[0].value, "hello world")
        result = Baggage.from_string(baggage.to_string())
        self.assertEqual(result.entries[0].value, "hello world")

    def test_roundtrip_unicode_value(self):
        '''Multi-byte UTF-8 values should survive a round-trip.'''
        baggage = Baggage.from_string("key=Am%C3%A9lie")
        self.assertEqual(baggage.entries[0].value, "Am\u00e9lie")
        result = Baggage.from_string(baggage.to_string())
        self.assertEqual(result.entries[0].value, "Am\u00e9lie")

    def test_roundtrip_multiple_entries_with_properties(self):
        original = "k1=v1;p1;p2=pv2,k2=v2;p3=pv3"
        baggage = Baggage.from_string(original)
        result = Baggage.from_string(baggage.to_string())
        self.assertEqual(len(result.entries), 2)
        self.assertEqual(result.entries[0].key, "k1")
        self.assertEqual(result.entries[0].value, "v1")
        self.assertEqual(len(result.entries[0].properties), 2)
        self.assertEqual(result.entries[0].properties[0].key, "p1")
        self.assertEqual(result.entries[0].properties[0].value, None)
        self.assertEqual(result.entries[0].properties[1].key, "p2")
        self.assertEqual(result.entries[0].properties[1].value, "pv2")
        self.assertEqual(result.entries[1].key, "k2")
        self.assertEqual(result.entries[1].value, "v2")
        self.assertEqual(result.entries[1].properties[0].key, "p3")
        self.assertEqual(result.entries[1].properties[0].value, "pv3")

    def test_roundtrip_preserves_entry_count(self):
        baggage = Baggage.from_string("a=1,b=2,c=3,d=4,e=5")
        result = Baggage.from_string(baggage.to_string())
        self.assertEqual(len(result.entries), 5)
        for i, expected in enumerate([("a","1"),("b","2"),("c","3"),("d","4"),("e","5")]):
            self.assertEqual(result.entries[i].key, expected[0])
            self.assertEqual(result.entries[i].value, expected[1])


class LimitsTest(unittest.TestCase):
    def test_serialize_at_least_64(self):
        '''A platform MUST propagate all list-members up to at least 64 list-members including any list-members added by the platform.'''
        baggage = Baggage([BaggageEntry("key%s" % x, "value")
                          for x in range(64)])
        baggage_str = baggage.to_string()
        entry_strs = baggage_str.split(",")
        self.assertEqual(len(entry_strs), 64)

    def test_serialize_long_entry(self):
        '''A platform MUST propagate all list-members including any list-members added by the platform if the resulting baggage-string would be 8192 bytes or less.'''
        long_value = '0123456789' * 819
        baggage = Baggage([BaggageEntry("a", long_value)])
        # a 1 character
        # = 1 character
        # 0123456789 10 characters * 819 = 8190 characters
        # total 8192 characters
        baggage_str = baggage.to_string()
        self.assertEqual(len(baggage_str), 8192)

    def test_serialize_many_entries(self):
        # 512 entries with 15 bytes + 1 trailing comma
        baggage = Baggage(
            [BaggageEntry("{:03d}".format(x), '0123456789a') for x in range(512)])

        # last entry is 16 bytes
        baggage_str = baggage.to_string() + 'b'
        self.assertEqual(len(baggage_str), 8192)

if __name__ == '__main__':
    unittest.main()
