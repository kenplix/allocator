import unittest
from typing import Any

from allocator import Block, Page, Allocator
from errors import OutOfMemoryError, MemoryAllocationError


class TestAllocator(unittest.TestCase):

    @staticmethod
    def mock_allocator():
        return Allocator(memory=32, pages_count=4, page_size=8)

    def equality_test(self, first: Any, second: Any):
        """Comparison of equivalence of objects in depth"""
        for attr in first.__dict__:
            if '__eq__' in type(first.__dict__[attr]).__dict__:
                self.assertEqual(first.__dict__[attr], second.__dict__[attr])
            else:
                self.equality_test(first.__dict__[attr], second.__dict__[attr])

    def test_alloc(self):
        size = 6
        start_addr = bin(0)
        page_end_addr = Allocator.end_address(start_addr, size=8)
        block_end_addr = Allocator.end_address(start_addr, size=size)

        test_page = Page(start_addr=start_addr, end_addr=page_end_addr)
        test_block = Block(start_addr=start_addr, end_addr=block_end_addr)
        test_page.append(test_block)

        alloc_page = self.mock_allocator().alloc(size)
        self.equality_test(test_block, alloc_page[0])
        self.equality_test(test_page, alloc_page)

    def test_alloc_error(self):
        size = 8
        occupied_volume = 9
        with self.assertRaises(OutOfMemoryError):
            self.mock_allocator().alloc(size=size, occupied_volume=occupied_volume)

    def test_memory_allocation_error(self):
        with self.assertRaises(MemoryAllocationError):
            Allocator(memory=32, pages_count=8, page_size=8)


if __name__ == '__main__':
    unittest.main()
