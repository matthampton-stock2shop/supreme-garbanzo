import unittest
import urllib.request
import sqlite3
from app import hello_world, init_db, upsert_product, get_products



class UnitTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
        init_db("file::memory:?cache=shared")

    @classmethod
    def tearDownClass(cls):     
        cls.conn.close()  

    def test_hello(self):
        d = hello_world()
        self.assertEqual(d, "<p>Hello, World!</p>")

    def test_upsert_product(self):
        upsert_product(
            "abc",
            {
            "size": "small",
            "grams": "100",
            "foo": "bar"
            }
        )

        product = next(filter(lambda p: p["sku"]=="abc", get_products()), None)
        self.assertIsNotNone(product)
        self.assertDictEqual(product["attributes"], {
            "size": "small",
            "grams": "100",
            "foo": "bar"
            })


        upsert_product(
            "abc",
            {
            "size": "small",
            "grams": "101",
            "foo": "bar"
            }
        )

class IntegrationTests(unittest.TestCase):

    def test_post_and_then_get(self):
        with urllib.request.urlopen('http://127.0.0.1:5000') as f:
            d = f.read().decode('utf-8')
        self.assertEqual(d, "<p>Hello, World!</p>")


if __name__ == '__main__':
    unittest.main()