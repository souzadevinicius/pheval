import unittest

from pheval.post_processing.post_processing import (
    PhEvalGeneResult,
    PhEvalVariantResult,
    ResultSorter,
)


class TestResultSorter(unittest.TestCase):
    def setUp(self) -> None:
        self.gene_results = ResultSorter(
            pheval_results=[
                PhEvalGeneResult(
                    gene_symbol="A4GNT", gene_identifier="ENSG00000118017", score=0.6529
                ),
                PhEvalGeneResult(
                    gene_symbol="MAP3K14", gene_identifier="ENSG00000006062", score=0.9234
                ),
                PhEvalGeneResult(
                    gene_symbol="OR14J1", gene_identifier="ENSG00000204695", score=0.6529
                ),
                PhEvalGeneResult(
                    gene_symbol="PAGE1", gene_identifier="ENSG00000068985", score=0.5235
                ),
            ],
            ranking_method="combinedScore",
        )
        self.variant_results = ResultSorter(
            pheval_results=[
                PhEvalVariantResult(
                    chromosome="5",
                    start=23457444233,
                    end=23457444234,
                    ref="A",
                    alt="C",
                    score=0.9348,
                ),
                PhEvalVariantResult(
                    chromosome="12", start=12754332, end=12754333, ref="T", alt="G", score=0.9999
                ),
                PhEvalVariantResult(
                    chromosome="X", start=93473023, end=93473024, ref="A", alt="G", score=0.1245
                ),
                PhEvalVariantResult(
                    chromosome="8", start=532356, end=532357, ref="A", alt="C", score=0.4578
                ),
            ],
            ranking_method="pValue",
        )

    def test_sort_by_decreasing_score(self):
        self.assertEqual(
            self.gene_results.sort_by_decreasing_score(),
            [
                PhEvalGeneResult(
                    gene_symbol="MAP3K14", gene_identifier="ENSG00000006062", score=0.9234
                ),
                PhEvalGeneResult(
                    gene_symbol="A4GNT", gene_identifier="ENSG00000118017", score=0.6529
                ),
                PhEvalGeneResult(
                    gene_symbol="OR14J1", gene_identifier="ENSG00000204695", score=0.6529
                ),
                PhEvalGeneResult(
                    gene_symbol="PAGE1", gene_identifier="ENSG00000068985", score=0.5235
                ),
            ],
        )

    def test_sort_by_increasing_score(self):
        self.assertEqual(
            self.variant_results.sort_by_increasing_score(),
            [
                PhEvalVariantResult(
                    chromosome="X", start=93473023, end=93473024, ref="A", alt="G", score=0.1245
                ),
                PhEvalVariantResult(
                    chromosome="8", start=532356, end=532357, ref="A", alt="C", score=0.4578
                ),
                PhEvalVariantResult(
                    chromosome="5",
                    start=23457444233,
                    end=23457444234,
                    ref="A",
                    alt="C",
                    score=0.9348,
                ),
                PhEvalVariantResult(
                    chromosome="12", start=12754332, end=12754333, ref="T", alt="G", score=0.9999
                ),
            ],
        )

    def test_sort_pheval_results_not_pvalue(self):
        self.assertEqual(
            self.gene_results.sort_pheval_results(),
            [
                PhEvalGeneResult(
                    gene_symbol="MAP3K14", gene_identifier="ENSG00000006062", score=0.9234
                ),
                PhEvalGeneResult(
                    gene_symbol="A4GNT", gene_identifier="ENSG00000118017", score=0.6529
                ),
                PhEvalGeneResult(
                    gene_symbol="OR14J1", gene_identifier="ENSG00000204695", score=0.6529
                ),
                PhEvalGeneResult(
                    gene_symbol="PAGE1", gene_identifier="ENSG00000068985", score=0.5235
                ),
            ],
        )

    def test_sort_pheval_results_pvalue(self):
        self.assertEqual(
            self.variant_results.sort_pheval_results(),
            [
                PhEvalVariantResult(
                    chromosome="X", start=93473023, end=93473024, ref="A", alt="G", score=0.1245
                ),
                PhEvalVariantResult(
                    chromosome="8", start=532356, end=532357, ref="A", alt="C", score=0.4578
                ),
                PhEvalVariantResult(
                    chromosome="5",
                    start=23457444233,
                    end=23457444234,
                    ref="A",
                    alt="C",
                    score=0.9348,
                ),
                PhEvalVariantResult(
                    chromosome="12", start=12754332, end=12754333, ref="T", alt="G", score=0.9999
                ),
            ],
        )
