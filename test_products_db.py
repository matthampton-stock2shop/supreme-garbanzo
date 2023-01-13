import unittest
import sqlite3
from products_db import init, upsert_product, get_product, get_products, set_products, ValidationError

class DbTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
        init("file::memory:?cache=shared")

    @classmethod
    def tearDownClass(cls):     
        cls.conn.close()  

    def test_upsert_product(self):

        preexisting_abc = get_product("abc")
        self.assertIsNone(preexisting_abc)

        abc = {
            "sku": "abc",
            "attributes": {
                "size": "small",
                "grams": "100",
                "foo": "bar"
            },
        }
        upsert_product(abc)

        inserted_abc = get_product("abc")
        self.assertIsNotNone(inserted_abc)
        self.assertDictEqual(inserted_abc["attributes"], abc["attributes"])

        abc["attributes"]["grams"] = "101"

        upsert_product(abc)

        updated_abc = get_product("abc")
        self.assertIsNotNone(updated_abc)
        self.assertEqual(updated_abc["attributes"]["grams"], "101")

    def test_set_products_get_products(self):
        new_products = [
            {
                "sku": "def",
                "attributes": {
                    "size": "medium",
                    "grams": "120",
                    "foo": "bag"
                    }
            },
            {
                "sku": "ghi",
                "attributes": {
                    "size": "large",
                    "grams": "140",
                    "bah": "bah"
                    }
            },
        ]
        set_products(new_products)

        products = get_products()
        products.sort(key=lambda p: p["sku"])
        self.assertEquals(len(products), 2)
        self.assertEqual(new_products[0]['sku'], products[0]['sku'])
        self.assertDictEqual(new_products[0]['attributes'], products[0]['attributes'])
        self.assertEqual(new_products[1]['sku'], products[1]['sku'])
        self.assertDictEqual(new_products[1]['attributes'], products[1]['attributes'])

    def test_upsert_invalid_product1_fails(self):

        abc = {
            "sku": "abc",
            "junk": "in here",
            "attributes": {
                "size": "small",
                "grams": "100",
                "foo": "bar"
            },
        }
        self.assertRaises(ValidationError, upsert_product, abc)

    def test_upsert_invalid_product2_fails(self):

        abc = {
            "sku_missing": "abc",
            "attributes": {
                "size": "small",
                "grams": "100",
                "foo": "bar"
            },
        }
        self.assertRaises(ValidationError, upsert_product, abc)

    def test_upsert_invalid_product3_fails(self):

        abc = {
            "sku": "abc",
            "attributes": "wrong_type",
        }
        self.assertRaises(ValidationError, upsert_product, abc)                

if __name__ == '__main__':
    unittest.main()
    