import unittest

from allocator import Block, Allocator
from errors import NotCorrectAddressesException, OutOfMemoryError


class TestBlock(unittest.TestCase):

    def test_not_correct_addresses(self):
        start_addr = bin(10)
        end_addr = bin(2)
        with self.assertRaises(NotCorrectAddressesException):
            Block(start_addr, end_addr)

    def test_out_of_memory(self):
        start_addr = bin(0)
        end_addr = Allocator.end_address(start_addr, size=8)
        with self.assertRaises(OutOfMemoryError):
            Block(start_addr, end_addr, occupied_volume=9)


if __name__ == '__main__':
    unittest.main()