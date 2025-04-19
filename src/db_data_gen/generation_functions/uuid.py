"""Contains generator classes for uuid"""

from uuid import uuid4

from .base import GenFunction


class UUIDGenFunction(GenFunction):
    """Generate values for uuid"""

    def get_common_value(self):
        """Get common value"""
        return str(uuid4())
