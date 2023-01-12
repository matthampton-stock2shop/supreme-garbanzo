import unittest
import urllib.request

class IntegrationTests(unittest.TestCase):

    def test_post_and_then_get(self):
        with urllib.request.urlopen('http://127.0.0.1:5000') as f:
            d = f.read().decode('utf-8')
        self.assertEqual(d, "<p>Hello, World!</p>")


if __name__ == '__main__':
    unittest.main()