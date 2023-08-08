from pathlib import Path
from typing import Type

import pandas as pd

from pheval.post_processing.post_processing import PhEvalResult


def _read_standardised_result(standardised_result_path: Path) -> dict:
    """Read the standardised result output and return a list of dictionaries."""
    return pd.read_csv(standardised_result_path, delimiter="\t").to_dict("records")


def parse_pheval_result(data_class_type: Type, pheval_result: [dict]) -> [PhEvalResult]:
    """Parse PhEval result into specified dataclass type."""
    return [data_class_type(**row) for row in pheval_result]
