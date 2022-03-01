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
        self.assertEqual(entry.property_key, None)
        self.assertEqual(entry.property_value, None)

    def test_parse_multiple(self):
        baggage = Baggage().from_string("SomeKey=SomeValue,SomeKey2=SomeValue2")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.property_key, None)
        self.assertEqual(entry1.property_value, None)
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.property_key, None)
        self.assertEqual(entry2.property_value, None)

    def test_parse_multiple_ows(self):
        baggage = Baggage().from_string(
            "SomeKey \t = \t SomeValue \t , \t SomeKey2 \t = \t SomeValue2 \t ")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.property_key, None)
        self.assertEqual(entry1.property_value, None)
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.property_key, None)
        self.assertEqual(entry2.property_value, None)

    def test_parse_multiple_property(self):
        baggage = Baggage().from_string(
            "SomeKey=SomeValue;SomeProp,SomeKey2=SomeValue2;SomeProp2")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.property_key, "SomeProp")
        self.assertEqual(entry1.property_value, None)
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.property_key, "SomeProp2")
        self.assertEqual(entry2.property_value, None)

    def test_parse_multiple_property_ows(self):
        baggage = Baggage().from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomeProp \t , \t SomeKey2 \t = \t SomeValue2 \t ; \t SomeProp2")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.property_key, "SomeProp")
        self.assertEqual(entry1.property_value, None)
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.property_key, "SomeProp2")
        self.assertEqual(entry2.property_value, None)

    def test_parse_multiple_kv_property(self):
        baggage = Baggage().from_string(
            "SomeKey=SomeValue;SomePropKey=SomePropValue,SomeKey2=SomeValue2;SomePropKey2=SomePropValue2")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.property_key, "SomePropKey")
        self.assertEqual(entry1.property_value, "SomePropValue")
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.property_key, "SomePropKey2")
        self.assertEqual(entry2.property_value, "SomePropValue2")

    def test_parse_multiple_kv_property_ows(self):
        baggage = Baggage().from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomePropKey=SomePropValue \t , \t SomeKey2 \t = \t SomeValue2 \t ; \t SomePropKey2 \t = \t SomePropValue2")
        self.assertEqual(len(baggage.entries), 2)
        entry1 = baggage.entries[0]
        entry2 = baggage.entries[1]
        self.assertEqual(entry1.key, "SomeKey")
        self.assertEqual(entry1.value, "SomeValue")
        self.assertEqual(entry1.property_key, "SomePropKey")
        self.assertEqual(entry1.property_value, "SomePropValue")
        self.assertEqual(entry2.key, "SomeKey2")
        self.assertEqual(entry2.value, "SomeValue2")
        self.assertEqual(entry2.property_key, "SomePropKey2")
        self.assertEqual(entry2.property_value, "SomePropValue2")


class BaggageEntryTest(unittest.TestCase):
    def test_ctor_default(self):
        entry = BaggageEntry("SomeKey", "SomeValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(entry.property_key, None)
        self.assertEqual(entry.property_value, None)

    def test_parse_simple(self):
        entry = BaggageEntry.from_string("SomeKey=SomeValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(entry.property_key, None)
        self.assertEqual(entry.property_value, None)

    def test_parse_multiple_equals(self):
        entry = BaggageEntry.from_string("SomeKey=SomeValue=equals")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue=equals")
        self.assertEqual(entry.property_key, None)
        self.assertEqual(entry.property_value, None)

    def test_parse_percent_encoded(self):
        value = "\t \"\';=asdf!@#$%^&*()"
        encoded_value = urllib.parse.quote(value)
        entry = BaggageEntry.from_string("SomeKey=%s" % (encoded_value))
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, value)
        self.assertEqual(entry.to_string(), "SomeKey=%09%20%22%27%3B%3Dasdf%21%40%23%24%25%5E%26%2A%28%29")

    def test_parse_property(self):
        entry = BaggageEntry.from_string("SomeKey=SomeValue;SomeProp")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(entry.property_key, "SomeProp")
        self.assertEqual(entry.property_value, None)

    def test_parse_kv_property(self):
        entry = BaggageEntry.from_string(
            "SomeKey=SomeValue;SomePropKey=SomePropValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(entry.property_key, "SomePropKey")
        self.assertEqual(entry.property_value, "SomePropValue")

    def test_parse_simple_ows(self):
        entry = BaggageEntry.from_string("SomeKey \t = \t SomeValue \t ")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(entry.property_key, None)
        self.assertEqual(entry.property_value, None)

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
        self.assertEqual(entry.property_key, "SomeProp")
        self.assertEqual(entry.property_value, None)

    def test_parse_kv_property_ows(self):
        entry = BaggageEntry.from_string(
            "SomeKey \t = \t SomeValue \t ; \t SomePropKey \t = \t SomePropValue")
        self.assertEqual(entry.key, "SomeKey")
        self.assertEqual(entry.value, "SomeValue")
        self.assertEqual(entry.property_key, "SomePropKey")
        self.assertEqual(entry.property_value, "SomePropValue")

# TODO update this when limits change to a minimum not a maximum
class LimitsTest(unittest.TestCase):
    def test_serialize_too_many_pairs(self):
        '''limit 180 entries'''
        baggage = Baggage([BaggageEntry("key%s" % x, "value") for x in range(200)])
        baggage_str = baggage.to_string()
        entry_strs = baggage_str.split(",")
        self.assertEqual(len(entry_strs), 180)

    def test_serialize_long_header(self):
        '''limit 4096 bytes'''
        long_value = '01234567890123456789'
        baggage = Baggage([BaggageEntry("key%s" % x, long_value) for x in range(200)])
        baggage_str = baggage.to_string()
        self.assertLessEqual(len(baggage_str), 4096)

if __name__ == '__main__':
    unittest.main()
