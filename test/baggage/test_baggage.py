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
        entry = BaggageEntry.from_string("SomeKey=%s" % (encoded_value))
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, value)
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

# TODO update this when limits change to a minimum not a maximum


class LimitsTest(unittest.TestCase):
    def test_serialize_too_many_entries(self):
        '''limit 180 entries'''
        baggage = Baggage([BaggageEntry("key%s" % x, "value")
                          for x in range(200)])
        baggage_str = baggage.to_string()
        entry_strs = baggage_str.split(",")
        self.assertEqual(len(entry_strs), 180)

    def test_serialize_long_entry(self):
        long_value = '01234567890' * 500
        baggage = Baggage([
            BaggageEntry("key1", "short_value"),
            BaggageEntry("key2", long_value),
            BaggageEntry("key3", "short_value_again"),
        ])
        baggage_str = baggage.to_string()
        self.assertEqual(
            baggage_str, "key1=short_value,key3=short_value_again")

    def test_serialize_long_header(self):
        '''limit 8192 bytes'''
        long_value = '012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789'
        baggage = Baggage([BaggageEntry("key%s" % x, long_value)
                          for x in range(100)])
        baggage_str = baggage.to_string()
        # ensure not all entries were serialized
        self.assertLess(len(baggage_str.split(",")), 100)
        self.assertLessEqual(len(baggage_str), 8192)


if __name__ == '__main__':
    unittest.main()
