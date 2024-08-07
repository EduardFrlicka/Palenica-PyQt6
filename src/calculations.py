from typing import List
from constants import DILUTE_TARGETS


def calculate_dillute_table(
    distilling_percentages: List[float],
    dilute_targets: List[float] = DILUTE_TARGETS,
) -> List[List[str]]:
    return [
        [
            (
                f"{(distilling_percentage / dilute_target - 1) * 10:.1f}"
                if distilling_percentage / dilute_target > 1
                else "-"
            )
            for dilute_target in dilute_targets
        ]
        for distilling_percentage in distilling_percentages
    ]
