"""Contains generator classes for datetime"""

import random
from datetime import datetime, timedelta

from .base import GenFunction


class TimestampzGenFunction(GenFunction):
    """Generate values for timestampz"""

    def get_common_value(self):
        """Get common value"""
        start_date = datetime(1970, 1, 1)
        end_date = datetime.now()
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds())),
        )
        return random_date.isoformat()
