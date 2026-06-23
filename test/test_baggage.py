import unittest
import urllib.parse

from baggage import Baggage, BaggageEntry


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

class LimitsTest(unittest.TestCase):
    _MAX_ENTRIES = 64
    _MAX_BYTES = 8192
    _ITERATIONS = 20

    def test_serialize_at_least_64(self):
        '''A platform MUST propagate all list-members up to at least 64 list-members including any list-members added by the platform.'''
        entries = [BaggageEntry("key%s" % x, "value") for x in range(64)]
        original_kvs = {(e.key, e.value) for e in entries}
        for run in range(self._ITERATIONS):
            with self.subTest(iteration=run):
                baggage = Baggage(entries)
                baggage_str = baggage.to_string()
                result = Baggage.from_string(baggage_str)
                result_kvs = {(e.key, e.value) for e in result.entries}
                self.assertEqual(len(result_kvs), 64)
                self.assertTrue(result_kvs.issubset(original_kvs))

    def test_serialize_long_entry(self):
        '''A platform MUST propagate all list-members including any list-members added by the platform if the resulting baggage-string would be 8192 bytes or less.'''
        long_value = '0123456789' * 819
        entries = [BaggageEntry("a", long_value)]
        original_kvs = {(e.key, e.value) for e in entries}
        for run in range(self._ITERATIONS):
            with self.subTest(iteration=run):
                baggage = Baggage(entries)
                baggage_str = baggage.to_string()
                result = Baggage.from_string(baggage_str)
                result_kvs = {(e.key, e.value) for e in result.entries}
                self.assertEqual(len(baggage_str), 8192)
                self.assertTrue(result_kvs.issubset(original_kvs))

    def test_serialize_many_entries(self):
        '''When limits are exceeded, result is either all entries or a truncated subset within limits.'''
        entries = [BaggageEntry("{:03d}".format(x), '0123456789a') for x in range(512)]
        original_kvs = {(e.key, e.value) for e in entries}
        for run in range(self._ITERATIONS):
            with self.subTest(iteration=run):
                baggage = Baggage(entries)
                baggage_str = baggage.to_string()
                result = Baggage.from_string(baggage_str)
                result_kvs = {(e.key, e.value) for e in result.entries}
                self.assertTrue(result_kvs.issubset(original_kvs))
                if len(result_kvs) < len(original_kvs):
                    self.assertLessEqual(len(result_kvs), self._MAX_ENTRIES)
                    self.assertLessEqual(len(baggage_str.encode('utf-8')), self._MAX_BYTES)

    def test_serialize_over_64_entries(self):
        '''When entry count exceeds 64, result is either all entries or a truncated subset within limits.'''
        entries = [BaggageEntry("key%s" % x, "val") for x in range(100)]
        original_kvs = {(e.key, e.value) for e in entries}
        for run in range(self._ITERATIONS):
            with self.subTest(iteration=run):
                baggage = Baggage(entries)
                baggage_str = baggage.to_string()
                result = Baggage.from_string(baggage_str)
                result_kvs = {(e.key, e.value) for e in result.entries}
                self.assertTrue(result_kvs.issubset(original_kvs))
                if len(result_kvs) < len(original_kvs):
                    self.assertLessEqual(len(result_kvs), self._MAX_ENTRIES)
                    self.assertLessEqual(len(baggage_str.encode('utf-8')), self._MAX_BYTES)


if __name__ == '__main__':
    unittest.main()
