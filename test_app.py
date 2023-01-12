import unittest
import urllib.request
import json

class AppIntegrationTests(unittest.TestCase):

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

        with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/products', json.dumps(new_products).encode("utf-8"), {'Content-Type': 'application/json'})) as f:
            r = json.load(f)
        self.assertDictEqual(r,  {"ok": True})

        with urllib.request.urlopen('http://127.0.0.1:5000/products') as f:
            products = json.load(f)
        products.sort(key=lambda p: p["sku"])
        self.assertEquals(len(products), 2)
        self.assertEqual(new_products[0]['sku'], products[0]['sku'])
        self.assertDictEqual(new_products[0]['attributes'], products[0]['attributes'])
        self.assertEqual(new_products[1]['sku'], products[1]['sku'])
        self.assertDictEqual(new_products[1]['attributes'], products[1]['attributes'])        


if __name__ == '__main__':
    unittest.main()
    