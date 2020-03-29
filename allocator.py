#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""Contains an allocator class and exceptions that may occur in it"""
from typing import Tuple, Iterator

from math import log2, ceil
from collections import Counter

from utilities.timer import clock
from errors import *


class Binary:
    """Creates instances of binary numbers only"""

    def __init__(self, binary: str) -> None:
        binary = self.shorten(binary)
        counter = Counter(binary)
        if counter['0'] + counter['1'] != len(binary):
            raise NotBinaryNumberException

        self.value = binary

    @staticmethod
    def shorten(binary: str) -> str:
        return binary if '0b' not in binary else binary[2:]

    def __eq__(self, other) -> bool:
        return True if self.value == self.shorten(other.value) else False

    def __repr__(self) -> str:
        return f'{self.value}'


def calculate_size(start_addr: Binary, end_addr: Binary) -> int:
    return int((int(end_addr.value, 2) - int(start_addr.value, 2)) / 255)


class Block:
    """Memory block"""

    def __init__(self, start_addr: str, end_addr: str, occupied_volume: int = 0) -> None:
        self.start_addr = Binary(start_addr)
        self.end_addr = Binary(end_addr)
        self.size = calculate_size(self.start_addr, self.end_addr)

        if self.size <= 0:
            raise NotCorrectAddressesException('The final address is less than or equal to the initial')

        if occupied_volume > self.size:
            raise OutOfMemoryError(f'The occupied space can not be more allocated: {occupied_volume=} > {self.size=}')
        self.occupied_volume = occupied_volume

    def __repr__(self) -> str:
        return f'[{self.start_addr} ... {self.end_addr}], {self.size=}, {self.occupied_volume=}'


class Page(list):
    """Page of memory"""

    def __init__(self, start_addr: str, end_addr: str, occupied_volume: int = 0) -> None:
        super().__init__([])
        self.start_addr = Binary(start_addr)
        self.end_addr = Binary(end_addr)
        if calculate_size(self.start_addr, self.end_addr) <= 0:
            raise NotCorrectAddressesException('The final address is less than or equal to the initial')

        self.occupied_volume = occupied_volume

    def append(self, block: Block) -> None:
        super().append(block)
        self.occupied_volume += block.size

    def remove(self, block: Block) -> None:
        super().remove(block)
        self.occupied_volume -= block.size

    def __repr__(self):
        return super().__repr__() + f' <{self.start_addr=}, {self.end_addr=}>'


class Allocator:
    """Contains functions for working with memory"""

    address = '0b0'
    pages = []
    free_blocks = []

    def __init__(self, memory: int, pages_count: int, page_size: int) -> None:
        self.memory = (256 * memory) - 1  # Ob11111111 -> 255

        div = log2(page_size)
        self.page_size = 2 ** ceil(div)

        if self.page_size * pages_count != memory:
            raise MemoryAllocationError

        for _ in range(pages_count):
            start, end = self._calculate_addresses(self.page_size)
            self.pages.append(Page(start, end))

    @staticmethod
    def end_address(start: str, size: int) -> str:
        return bin(int(start, 2) + (size * 255) + (size - 1))  # 1 b size + bit bias

    def _calculate_addresses(self, size: int) -> Tuple[str, str]:
        start = self.address
        end = self.end_address(start, size)
        self.address = bin(int(end, 2) + 1)
        return start, end

    @clock
    def alloc(self, size: int, occupied_volume: int = 0) -> Page:
        """Allocates a block of memory"""
        if size > self.page_size:
            raise OutOfMemoryError(
                f'Allocated space cannot be larger than the memory page size: {size=} > {self.page_size=}')

        for index, block_info in enumerate(self.free_blocks):
            if (block := block_info.get('BLOCK')).size == size:
                page = block_info.get('PAGE')
                page.append(Block(block.start_addr.value, block.end_addr.value, occupied_volume))
                del self.free_blocks[index]
                return page

        for page in self.pages:
            if (self.page_size - page.occupied_volume) >= size:
                start_addr = bin(int(page[-1].end_addr.value, 2) + 1) if page else page.start_addr.value
                end_addr = self.end_address(start_addr, size)
                page.append(Block(start_addr, end_addr, occupied_volume))
                return page

        raise OutOfMemoryError('There is no free space to allocate a block of memory')

    def _find_block(self, address: Binary) -> Tuple[Block, Page]:
        for page in self.pages:
            for block in page:
                if block.start_addr.value == address.value:
                    return block, page
        else:
            raise BlockNotFoundException

    def _change_blocks(self, block: Block, page: Page, new_size: int) -> Page:
        page.remove(block)
        if self.page_size - page.occupied_volume >= new_size - block.size:  # difference in free space
            end_addr = self.end_address(block.start_addr.value, new_size)
            page.append(Block(block.start_addr.value, end_addr, block.occupied_volume))
            return page
        else:
            self.alloc(new_size, block.occupied_volume)

    @clock
    def realloc(self, address: Binary, new_size: int) -> Page:
        """Resizes the selected block at address"""
        if address is not None:
            block, page = self._find_block(address)
            return self._change_blocks(block, page, new_size)
        else:
            return self.alloc(new_size)

    @clock
    def free(self, address: Binary) -> None:
        """Frees block memory at address"""
        block, page = self._find_block(address)
        page.remove(block)
        self.free_blocks.append({'BLOCK': Block(block.start_addr.value, block.end_addr.value), 'PAGE': page})

    @clock
    def dump(self) -> Iterator[Page]:
        """Displays existing blocks"""
        for page in self.pages:
            yield page


if __name__ == '__main__':
    allocator = Allocator(32, 4, 8)
    al2 = Allocator(32, 4, 8)
    allocator.alloc(6)
    allocator.alloc(3)
    allocator.alloc(2)
    allocator.alloc(3)
    allocator.alloc(6)
    allocator.realloc(Binary('0b11000000000'), 1)
    allocator.free(Binary('0b100000000000'))
    allocator.alloc(3)
    print()
    for p in allocator.dump():
        print(p)
