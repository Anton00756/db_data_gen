"""Contains generator classes for string"""

import random
import string

from .base import GenFunction


class VarcharGenFunction(GenFunction):
    """Generate values for varchar"""

    LETTERS = string.printable

    def get_special_values(self):
        """Get list of special values. Can be overridden"""
        return ['', ''.join(random.choice(VarcharGenFunction.LETTERS) for _ in range(self.column_info.max_length))]

    def get_common_value(self):
        """Get common value"""
        return ''.join(
            random.choice(VarcharGenFunction.LETTERS) for _ in range(random.randint(0, self.column_info.max_length))
        )


class TextGenFunction(GenFunction):
    """Generate values for text"""

    LETTERS = string.printable
    MAX_LENGTH = 4096

    def get_special_values(self):
        """Get list of special values. Can be overridden"""
        return ['', ''.join(random.choice(TextGenFunction.LETTERS) for _ in range(TextGenFunction.MAX_LENGTH))]

    def get_common_value(self):
        """Get common value"""
        return ''.join(
            random.choice(TextGenFunction.LETTERS) for _ in range(random.randint(0, TextGenFunction.MAX_LENGTH))
        )
