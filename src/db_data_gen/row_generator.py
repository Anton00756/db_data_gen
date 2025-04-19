"""Contains class to generate row values"""

from types import GeneratorType
from typing import List, Optional, Tuple, Union

from .generation_functions import GenFunction


class RowGenerator:
    """Class to generate row values"""

    def __init__(
        self,
        generators: List[Union[GenFunction, GeneratorType]],
        uniqueness_skip_mode: bool,
        unique_groups: List[List[int]],
    ):
        self.generators = generators
        self.uniqueness_skip_mode = uniqueness_skip_mode
        self.generated_records_count = 0

        self._unique_groups = {tuple(group): set() for group in unique_groups}

    def _check_unique_values_of_row(self, row: list) -> Tuple[bool, Optional[tuple]]:
        """Check row values for uniqueness"""
        for group, group_values in self._unique_groups.items():
            if len(group) == 1:
                if row[group[0]] in group_values:
                    return False, group
            elif tuple(row[index] for index in group) in group_values:
                return False, group
        for group, group_values in self._unique_groups.items():
            if len(group) == 1:
                group_values.add(row[group[0]])
            else:
                group_values.add(tuple(row[index] for index in group))
        return (True, None)

    def generate(self, records_count: int):
        """Generate row values"""
        for _ in range(records_count):
            self.generated_records_count += 1
            row = list(
                next(generator) if isinstance(generator, GeneratorType) else generator.get_value()
                for generator in self.generators
            )
            uniqueness_result = self._check_unique_values_of_row(row)
            if uniqueness_result[0]:
                yield row
                continue
            if self.uniqueness_skip_mode:
                continue
            while not uniqueness_result[0]:
                for index in uniqueness_result[1]:
                    row[index] = (
                        next(self.generators[index])
                        if isinstance(self.generators[index], GeneratorType)
                        else self.generators[index].get_value()
                    )
                uniqueness_result = self._check_unique_values_of_row(row)
            yield row
