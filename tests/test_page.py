import unittest

from allocator import Block
from errors import NotCorrectAddressesException


class TestPage(unittest.TestCase):

    def test_not_correct_addresses(self):
        start_addr = bin(10)
        end_addr = bin(2)
        with self.assertRaises(NotCorrectAddressesException):
            Block(start_addr, end_addr)


if __name__ == '__main__':
    unittest.main()