"""Contains generator classes for int"""

import random

from .base import GenFunction


def create_int_generator(num: int):
    """Int factory"""
    border_value = 2 ** (8 * num - 1)

    class IntGenFunction(GenFunction):
        """Generate values for int"""

        def get_special_values(self):
            """Get list of special values. Can be overridden"""
            return [-border_value, 0, border_value - 1]

        def get_common_value(self):
            """Get common value"""
            return random.randint(-border_value, border_value - 1)

    return IntGenFunction


Int2GenFunction = create_int_generator(2)
Int4GenFunction = create_int_generator(4)
Int8GenFunction = create_int_generator(8)
