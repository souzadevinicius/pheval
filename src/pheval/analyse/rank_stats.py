import csv
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import List


@dataclass
class RankStats:
    """Store statistics related to ranking.

    Attributes:
        top (int): Count of top-ranked matches.
        top3 (int): Count of matches within the top 3 ranks.
        top5 (int): Count of matches within the top 5 ranks.
        top10 (int): Count of matches within the top 10 ranks.
        found (int): Count of found matches.
        total (int): Total count of matches.
        reciprocal_ranks (List[float]): List of reciprocal ranks.
        relevant_ranks List[List[int]]: Nested list of ranks for the known entities for all cases in a run.
        mrr (float): Mean Reciprocal Rank (MRR). Defaults to None.
    """

    top: int = 0
    top3: int = 0
    top5: int = 0
    top10: int = 0
    found: int = 0
    total: int = 0
    reciprocal_ranks: List = field(default_factory=list)
    relevant_result_ranks: List[List[int]] = field(default_factory=list)
    mrr: float = None

    def add_rank(self, rank: int) -> None:
        """
        Add rank for matched result.

        Args:
            rank (int): The rank value to be added.

        Notes:
            This method updates the internal attributes of the RankStats object based on the provided rank value.
            It calculates various statistics such as the count of top ranks (1, 3, 5, and 10),
            the total number of ranks found,and the reciprocal rank.
            This function modifies the object's state by updating the internal attributes.
        """
        self.reciprocal_ranks.append(1 / rank)
        self.found += 1
        if rank == 1:
            self.top += 1
        if rank != "" and rank <= 3:
            self.top3 += 1
        if rank != "" and rank <= 5:
            self.top5 += 1
        if rank != "" and rank <= 10:
            self.top10 += 1

    def percentage_rank(self, value: int) -> float:
        """
        Calculate the percentage rank.

        Args:
            value (int): The value for which the percentage rank needs to be calculated.

        Returns:
            float: The calculated percentage rank based on the provided value and the total count.
        """
        return 100 * value / self.total

    def percentage_top(self) -> float:
        """
        Calculate the percentage of top matches.

        Returns:
            float: The percentage of top matches compared to the total count.
        """
        return self.percentage_rank(self.top)

    def percentage_top3(self) -> float:
        """
        Calculate the percentage of matches within the top 3.

        Returns:
            float: The percentage of matches within the top 3 compared to the total count.
        """
        return self.percentage_rank(self.top3)

    def percentage_top5(self) -> float:
        """
        Calculate the percentage of matches within the top 5.

        Returns:
            float: The percentage of matches within the top 5 compared to the total count.
        """
        return self.percentage_rank(self.top5)

    def percentage_top10(self) -> float:
        """
        Calculate the percentage of matches within the top 10.

        Returns:
            float: The percentage of matches within the top 10 compared to the total count.
        """
        return self.percentage_rank(self.top10)

    def percentage_found(self) -> float:
        """
        Calculate the percentage of matches found.

        Returns:
            float: The percentage of matches found compared to the total count.
        """
        return self.percentage_rank(self.found)

    @staticmethod
    def percentage_difference(percentage_value_1: float, percentage_value_2: float) -> float:
        """
        Calculate the percentage difference between two percentage values.

        Args:
            percentage_value_1 (float): The first percentage value.
            percentage_value_2 (float): The second percentage value.

        Returns:
            float: The difference between the two percentage values.
        """
        return percentage_value_1 - percentage_value_2

    def mean_reciprocal_rank(self) -> float:
        """
        Calculate the Mean Reciprocal Rank (MRR) for the stored ranks.

        The Mean Reciprocal Rank is computed as the mean of the reciprocal ranks
        for the found cases.

        If the total number of cases differs from the number of found cases,
        this method extends the reciprocal ranks list with zeroes for missing cases.

        Returns:
            float: The calculated Mean Reciprocal Rank.
        """
        if len(self.reciprocal_ranks) != self.total:
            missing_cases = self.total - self.found
            self.reciprocal_ranks.extend([0] * missing_cases)
            return mean(self.reciprocal_ranks)
        return mean(self.reciprocal_ranks)

    def return_mean_reciprocal_rank(self) -> float:
        """
        Retrieve or calculate the Mean Reciprocal Rank (MRR).

        If a pre-calculated MRR value exists (stored in the 'mrr' attribute), this method returns that value.
        Otherwise, it computes the Mean Reciprocal Rank using the 'mean_reciprocal_rank' method.

        Returns:
            float: The Mean Reciprocal Rank value.
        """
        if self.mrr is not None:
            return self.mrr
        else:
            return self.mean_reciprocal_rank()

    @staticmethod
    def _calculate_average_precision(number_of_relevant_entities_at_k: int,
                                     precision_at_k: float) -> float:
        """
        Calculate the Average Precision at k.

        Average Precision at k (AP@k) is a metric used to evaluate the precision of a ranked retrieval system.
        It measures the precision at each relevant position up to k and takes the average.

        Args:
            number_of_relevant_entities_at_k (int): The count of relevant entities in the top-k predictions.
            precision_at_k (float): The precision at k - the sum of the precision values at each relevant position.

        Returns:
            float: The Average Precision at k, ranging from 0.0 to 1.0.
                   A higher value indicates better precision in the top-k predictions.
        """
        try:
            return (
                    1 / number_of_relevant_entities_at_k
            ) * precision_at_k
        except ZeroDivisionError:
            return 0

    def mean_average_precision_at_k(self, k: int) -> float:
        """
        Calculate the Mean Average Precision at k.

        Mean Average Precision at k (MAP@k) is a performance metric for ranked data.
        It calculates the average precision at k for each result rank and then takes the mean across all queries.

        Args:
            k (int): The number of top predictions to consider for precision calculation.

        Returns:
            float: The Mean Average Precision at k, ranging from 0.0 to 1.0.
                   A higher value indicates better performance in ranking relevant entities higher in the predictions.
        """
        cumulative_average_precision_scores = 0
        for result_ranks in self.relevant_result_ranks:
            precision_at_k, number_of_relevant_entities_at_k = 0, 0
            for rank in result_ranks:
                if 0 < rank <= k:
                    number_of_relevant_entities_at_k += 1
                    precision_at_k += number_of_relevant_entities_at_k / rank
                cumulative_average_precision_scores += self._calculate_average_precision(
                    number_of_relevant_entities_at_k, precision_at_k)
        return (1 / self.total) * cumulative_average_precision_scores


class RankStatsWriter:
    """Class for writing the rank stats to a file."""

    def __init__(self, file: Path):
        """
        Initialise the RankStatsWriter class
        Args:
            file (Path): Path to the file where rank stats will be written
        """
        self.file = open(file, "w")
        self.writer = csv.writer(self.file, delimiter="\t")
        self.writer.writerow(
            [
                "results_directory_path",
                "top",
                "top3",
                "top5",
                "top10",
                "found",
                "total",
                "mean_reciprocal_rank",
                "percentage_top",
                "percentage_top3",
                "percentage_top5",
                "percentage_top10",
                "percentage_found",
                "MAP@1",
                "MAP@3",
                "MAP@5",
                "MAP@10",
            ]
        )

    def write_row(self, directory: Path, rank_stats: RankStats) -> None:
        """
        Write summary rank statistics row for a run to the file.

        Args:
            directory (Path): Path to the results directory corresponding to the run
            rank_stats (RankStats): RankStats instance containing rank statistics corresponding to the run

        Raises:
            IOError: If there is an error writing to the file.
        """
        try:
            self.writer.writerow(
                [
                    directory,
                    rank_stats.top,
                    rank_stats.top3,
                    rank_stats.top5,
                    rank_stats.top10,
                    rank_stats.found,
                    rank_stats.total,
                    rank_stats.mean_reciprocal_rank(),
                    rank_stats.percentage_top(),
                    rank_stats.percentage_top3(),
                    rank_stats.percentage_top5(),
                    rank_stats.percentage_top10(),
                    rank_stats.percentage_found(),
                    rank_stats.mean_average_precision_at_k(1),
                    rank_stats.mean_average_precision_at_k(3),
                    rank_stats.mean_average_precision_at_k(5),
                    rank_stats.mean_average_precision_at_k(10),
                ]
            )
        except IOError:
            print("Error writing ", self.file)

    def close(self) -> None:
        """
        Close the file used for writing rank statistics.

        Raises:
            IOError: If there's an error while closing the file.
        """
        try:
            self.file.close()
        except IOError:
            print("Error closing ", self.file)
