"""Contains generator classes for bytes"""

import os
import random

from .base import GenFunction


class ByteaGenFunction(GenFunction):
    """Generate values for bytea"""

    MAX_LENGTH = 512

    def get_special_values(self):
        """Get list of special values. Can be overridden"""
        return [bytes(), os.urandom(ByteaGenFunction.MAX_LENGTH)]

    def get_common_value(self):
        """Get common value"""
        return os.urandom(random.randint(0, ByteaGenFunction.MAX_LENGTH))
