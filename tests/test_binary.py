import unittest

from allocator import Binary
from errors import NotBinaryNumberException


class TestBinary(unittest.TestCase):

    def test_init(self):
        data = '1111'
        self.assertEqual(data, Binary(data).value)

    def test_not_binary_sting(self):
        data = '123'
        with self.assertRaises(NotBinaryNumberException):
            Binary(data)


if __name__ == '__main__':
    unittest.main()