"""Contains generator classes for bool"""

import random

from .base import GenFunction


class BoolGenFunction(GenFunction):
    """Generate values for bool"""

    def get_common_value(self):
        """Get common value"""
        return random.random() < 0.5
