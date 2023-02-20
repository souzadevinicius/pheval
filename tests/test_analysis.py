import unittest
from collections import defaultdict
from copy import copy
from pathlib import Path, PosixPath

import pandas as pd

from pheval.analyse.analysis import (
    AssessGenePrioritisation,
    AssessVariantPrioritisation,
    GenePrioritisationResult,
    PlotGenerator,
    PrioritisationRankRecorder,
    RankComparisonGenerator,
    RankStats,
    TrackGenePrioritisation,
    TrackPrioritisation,
    TrackVariantPrioritisation,
    VariantPrioritisationResult,
    merge_results,
    parse_pheval_gene_result,
    parse_pheval_variant_result,
)
from pheval.post_processing.post_processing import (
    PhEvalGeneResult,
    PhEvalVariantResult,
    RankedPhEvalGeneResult,
    RankedPhEvalVariantResult,
)
from pheval.utils.phenopacket_utils import GenomicVariant, ProbandCausativeGene


class TestPrioritisationRankRecorder(unittest.TestCase):
    def setUp(self) -> None:
        self.add_new_phenopacket_variant_record = PrioritisationRankRecorder(
            1,
            Path("directory1"),
            VariantPrioritisationResult(
                Path("/path/to/phenopacket-2.json"), GenomicVariant("1", 4896347, "C", "T"), 9
            ),
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Variant": "12_120434_A_G",
                        Path("directory1"): 3,
                    }
                },
            ),
        )
        self.add_new_directory_variant_record = PrioritisationRankRecorder(
            0,
            Path("directory2"),
            VariantPrioritisationResult(
                Path("/path/to/phenopacket-1.json"), GenomicVariant("12", 120434, "A", "G"), 9
            ),
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Variant": "12_120434_A_G",
                        Path("directory1"): 3,
                    }
                },
            ),
        )
        self.add_new_phenopacket_gene_record = PrioritisationRankRecorder(
            1,
            Path("directory1"),
            GenePrioritisationResult(Path("/path/to/phenopacket-2.json"), "GENE", 7),
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Gene": "LARGE1",
                        PosixPath("directory1"): 4,
                    }
                },
            ),
        )
        self.add_new_directory_gene_record = PrioritisationRankRecorder(
            0,
            Path("directory2"),
            GenePrioritisationResult(Path("/path/to/phenopacket-1.json"), "LARGE1", 1),
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Gene": "LARGE1",
                        PosixPath("directory1"): 4,
                    }
                },
            ),
        )

    def test__record_gene_rank_new_directory(self):
        self.assertEqual(
            self.add_new_directory_gene_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Gene": "LARGE1",
                        PosixPath("directory1"): 4,
                    }
                },
            ),
        )
        self.add_new_directory_gene_record.record_rank()
        self.assertEqual(
            self.add_new_directory_gene_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Gene": "LARGE1",
                        PosixPath("directory1"): 4,
                        PosixPath("directory2"): 1,
                    }
                },
            ),
        )

    def test__record_gene_rank_new_phenopacket(self):
        self.assertEqual(
            self.add_new_phenopacket_gene_record.run_comparison,
            defaultdict(
                dict,
                {0: {"Phenopacket": "phenopacket-1.json", "Gene": "LARGE1", Path("directory1"): 4}},
            ),
        )
        self.add_new_phenopacket_gene_record.record_rank()
        self.assertEqual(
            self.add_new_phenopacket_gene_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Gene": "LARGE1",
                        Path("directory1"): 4,
                    },
                    1: {"Phenopacket": "phenopacket-2.json", "Gene": "GENE", Path("directory1"): 7},
                },
            ),
        )

    def test__variant_gene_rank_new_directory(self):
        self.assertEqual(
            self.add_new_directory_variant_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Variant": "12_120434_A_G",
                        Path("directory1"): 3,
                    }
                },
            ),
        )
        self.add_new_directory_variant_record.record_rank()
        self.assertEqual(
            self.add_new_directory_variant_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Variant": "12_120434_A_G",
                        PosixPath("directory1"): 3,
                        PosixPath("directory2"): 9,
                    }
                },
            ),
        )

    def test__variant_gene_rank_new_phenopacket(self):
        self.assertEqual(
            self.add_new_phenopacket_variant_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Variant": "12_120434_A_G",
                        Path("directory1"): 3,
                    }
                },
            ),
        )
        self.add_new_phenopacket_variant_record.record_rank()
        self.assertEqual(
            self.add_new_phenopacket_variant_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Variant": "12_120434_A_G",
                        PosixPath("directory1"): 3,
                    },
                    1: {
                        "Phenopacket": "phenopacket-2.json",
                        "Variant": "1_4896347_C_T",
                        PosixPath("directory1"): 9,
                    },
                },
            ),
        )

    def test_record_rank_gene(self):
        self.add_new_directory_gene_record.record_rank()
        self.assertEqual(
            self.add_new_directory_gene_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Gene": "LARGE1",
                        PosixPath("directory1"): 4,
                        PosixPath("directory2"): 1,
                    }
                },
            ),
        )

    def test_record_rank_variant(self):
        self.add_new_directory_variant_record.record_rank()
        self.assertEqual(
            self.add_new_directory_variant_record.run_comparison,
            defaultdict(
                dict,
                {
                    0: {
                        "Phenopacket": "phenopacket-1.json",
                        "Variant": "12_120434_A_G",
                        PosixPath("directory1"): 3,
                        PosixPath("directory2"): 9,
                    }
                },
            ),
        )


class TestRankStats(unittest.TestCase):
    def setUp(self) -> None:
        self.rank_stats = RankStats()

    def test_add_rank(self):
        self.rank_stats.add_rank(1)
        self.rank_stats.add_rank(3)
        self.rank_stats.add_rank(5)
        self.rank_stats.add_rank(7)
        self.rank_stats.add_rank(10)
        self.assertEqual(
            self.rank_stats,
            RankStats(
                top=1,
                top3=2,
                top5=3,
                top10=5,
                found=5,
                total=0,
                reciprocal_ranks=[1.0, 0.3333333333333333, 0.2, 0.14285714285714285, 0.1],
            ),
        )

    def test_percentage_rank(self):
        self.rank_stats.found = 10
        self.assertTrue(self.rank_stats.percentage_rank(3) == 30)

    def test_percentage_top(self):
        self.rank_stats.top, self.rank_stats.found = 10, 20
        self.assertEqual(self.rank_stats.percentage_top(), 50)

    def test_percentage_top3(self):
        self.rank_stats.top3, self.rank_stats.found = 30, 50
        self.assertEqual(self.rank_stats.percentage_top3(), 60)

    def test_percentage_top5(self):
        self.rank_stats.top5, self.rank_stats.found = 70, 160
        self.assertEqual(self.rank_stats.percentage_top5(), 43.75)

    def test_percentage_top10(self):
        self.rank_stats.top10, self.rank_stats.found = 100, 160
        self.assertEqual(self.rank_stats.percentage_top10(), 62.5)

    def test_percentage_found(self):
        self.rank_stats.found, self.rank_stats.total = 100, 125
        self.assertEqual(self.rank_stats.percentage_found(), 80)

    def test_mean_reciprocal_rank(self):
        self.rank_stats.reciprocal_ranks = [0.2, 0.4, 0.5, 0.6, 0.8]
        self.assertEqual(self.rank_stats.mean_reciprocal_rank(), 0.5)


class TestAssessGenePrioritisation(unittest.TestCase):
    def setUp(self) -> None:
        self.assess_gene_prioritisation = AssessGenePrioritisation(
            phenopacket_path=Path("/path/to/phenopacket.json"),
            results_dir=Path("/path/to/results_dir"),
            standardised_gene_results=[
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=1,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="ZNF804B", gene_identifier="ENSG00000182348", score=0.5777
                    ),
                    rank=2,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="SMCO2", gene_identifier="ENSG00000165935", score=0.5777
                    ),
                    rank=2,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="SPNS1", gene_identifier="ENSG00000169682", score=0.3765
                    ),
                    rank=4,
                ),
            ],
            threshold=0.0,
            score_order="descending",
            proband_causative_genes=[
                ProbandCausativeGene(gene_symbol="PLXNA1", gene_identifier="ENSG00000114554"),
                ProbandCausativeGene(gene_symbol="LARGE1", gene_identifier="ENSG00000133424"),
            ],
        )
        self.assess_gene_prioritisation_ascending_order = AssessGenePrioritisation(
            phenopacket_path=Path("/path/to/phenopacket.json"),
            results_dir=Path("/path/to/results_dir"),
            standardised_gene_results=[
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="SPNS1", gene_identifier="ENSG00000169682", score=0.3765
                    ),
                    rank=1,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="ZNF804B", gene_identifier="ENSG00000182348", score=0.5777
                    ),
                    rank=2,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="SMCO2", gene_identifier="ENSG00000165935", score=0.5777
                    ),
                    rank=2,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=4,
                ),
            ],
            threshold=0.0,
            score_order="ascending",
            proband_causative_genes=[
                ProbandCausativeGene(gene_symbol="PLXNA1", gene_identifier="ENSG00000114554"),
                ProbandCausativeGene(gene_symbol="LARGE1", gene_identifier="ENSG00000133424"),
            ],
        )
        self.gene_rank_stats = RankStats(0, 0, 0, 0, 0)
        self.gene_rank_records = defaultdict(dict)

    def test_record_gene_prioritisation_match(self):
        self.assertEqual(
            self.assess_gene_prioritisation._record_gene_prioritisation_match(
                gene=ProbandCausativeGene(gene_symbol="PLXNA1", gene_identifier="ENSG00000114554"),
                result_entry=RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=1,
                ),
                rank_stats=self.gene_rank_stats,
            ),
            GenePrioritisationResult(
                phenopacket_path=Path("/path/to/phenopacket.json"), gene="PLXNA1", rank=1
            ),
        )

    def test_assess_gene_with_ascending_order_threshold_fails_cutoff(self):
        assess_ascending_order_threshold = copy(self.assess_gene_prioritisation_ascending_order)
        assess_ascending_order_threshold.threshold = 0.1
        self.assertEqual(
            assess_ascending_order_threshold._assess_gene_with_threshold_ascending_order(
                gene=ProbandCausativeGene(gene_symbol="PLXNA1", gene_identifier="ENSG00000114554"),
                result_entry=RankedPhEvalGeneResult(
                    PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=1,
                ),
                rank_stats=self.gene_rank_stats,
            ),
            None,
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=0, reciprocal_ranks=[]),
        )

    def test_assess_gene_with_ascending_order_threshold_meets_cutoff(self):
        assess_ascending_order_threshold = copy(self.assess_gene_prioritisation_ascending_order)
        assess_ascending_order_threshold.threshold = 0.9
        self.assertEqual(
            assess_ascending_order_threshold._assess_gene_with_threshold_ascending_order(
                gene=ProbandCausativeGene(gene_symbol="PLXNA1", gene_identifier="ENSG00000114554"),
                result_entry=RankedPhEvalGeneResult(
                    PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=1,
                ),
                rank_stats=self.gene_rank_stats,
            ),
            GenePrioritisationResult(
                phenopacket_path=Path("/path/to/phenopacket.json"), gene="PLXNA1", rank=1
            ),
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=0, reciprocal_ranks=[1.0]),
        )

    def test_assess_gene_with_threshold_fails_cutoff(self):
        assess_with_threshold = copy(self.assess_gene_prioritisation)
        assess_with_threshold.threshold = 0.9
        self.assertEqual(
            assess_with_threshold._assess_gene_with_threshold(
                gene=ProbandCausativeGene(gene_symbol="PLXNA1", gene_identifier="ENSG00000114554"),
                result_entry=RankedPhEvalGeneResult(
                    PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=1,
                ),
                rank_stats=self.gene_rank_stats,
            ),
            None,
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=0, reciprocal_ranks=[]),
        )

    def test_assess_gene_with_threshold_meets_cutoff(self):
        assess_with_threshold = copy(self.assess_gene_prioritisation)
        assess_with_threshold.threshold = 0.5
        self.assertEqual(
            assess_with_threshold._assess_gene_with_threshold(
                gene=ProbandCausativeGene(gene_symbol="PLXNA1", gene_identifier="ENSG00000114554"),
                result_entry=RankedPhEvalGeneResult(
                    PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=1,
                ),
                rank_stats=self.gene_rank_stats,
            ),
            GenePrioritisationResult(
                phenopacket_path=Path("/path/to/phenopacket.json"), gene="PLXNA1", rank=1
            ),
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=0, reciprocal_ranks=[1.0]),
        )

    def test_assess_gene_prioritisation_no_threshold(self):
        self.assess_gene_prioritisation.assess_gene_prioritisation(
            self.gene_rank_stats, self.gene_rank_records
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=2, reciprocal_ranks=[1.0]),
        )
        self.assertEqual(
            self.gene_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "PLXNA1",
                    Path("/path/to/results_dir"): 1,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "LARGE1",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_gene_prioritisation_threshold_fails_ascending_order_cutoff(self):
        assess_with_threshold = copy(self.assess_gene_prioritisation_ascending_order)
        assess_with_threshold.threshold = 0.01
        assess_with_threshold.assess_gene_prioritisation(
            self.gene_rank_stats, self.gene_rank_records
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=2, reciprocal_ranks=[]),
        )
        self.assertEqual(
            self.gene_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "PLXNA1",
                    Path("/path/to/results_dir"): 0,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "LARGE1",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_gene_prioritisation_threshold_meets_ascending_order_cutoff(self):
        assess_with_threshold = copy(self.assess_gene_prioritisation_ascending_order)
        assess_with_threshold.threshold = 0.9
        assess_with_threshold.assess_gene_prioritisation(
            self.gene_rank_stats, self.gene_rank_records
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=0, top3=0, top5=1, top10=1, found=1, total=2, reciprocal_ranks=[0.25]),
        )
        self.assertEqual(
            self.gene_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "PLXNA1",
                    Path("/path/to/results_dir"): 4,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "LARGE1",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_gene_prioritisation_threshold_fails_cutoff(self):
        assess_with_threshold = copy(self.assess_gene_prioritisation)
        assess_with_threshold.threshold = 0.9
        assess_with_threshold.assess_gene_prioritisation(
            self.gene_rank_stats, self.gene_rank_records
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=2, reciprocal_ranks=[]),
        )
        self.assertEqual(
            self.gene_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "PLXNA1",
                    Path("/path/to/results_dir"): 0,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "LARGE1",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_gene_prioritisation_threshold_meets_cutoff(self):
        assess_with_threshold = copy(self.assess_gene_prioritisation)
        assess_with_threshold.threshold = 0.1
        assess_with_threshold.assess_gene_prioritisation(
            self.gene_rank_stats, self.gene_rank_records
        )
        self.assertEqual(
            self.gene_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=2, reciprocal_ranks=[1.0]),
        )
        self.assertEqual(
            self.gene_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "PLXNA1",
                    Path("/path/to/results_dir"): 1,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Gene": "LARGE1",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )


class TestAssessVariantPrioritisation(unittest.TestCase):
    def setUp(self) -> None:
        variant_results = [
            RankedPhEvalVariantResult(
                PhEvalVariantResult(
                    chromosome="3", start=126730873, end=126730873, ref="G", alt="A", score=0.0484
                ),
                rank=1,
            ),
            RankedPhEvalVariantResult(
                PhEvalVariantResult(
                    chromosome="3", start=126730873, end=126730873, ref="G", alt="A", score=0.0484
                ),
                rank=1,
            ),
            RankedPhEvalVariantResult(
                PhEvalVariantResult(
                    chromosome="3", start=126741108, end=126741108, ref="G", alt="A", score=0.0484
                ),
                rank=1,
            ),
        ]
        self.assess_variant_prioritisation = AssessVariantPrioritisation(
            phenopacket_path=Path("/path/to/phenopacket.json"),
            results_dir=Path("/path/to/results_dir"),
            standardised_variant_results=variant_results,
            threshold=0.0,
            score_order="descending",
            proband_causative_variants=[
                GenomicVariant(chrom="3", pos=126741108, ref="G", alt="A"),
                GenomicVariant(chrom="16", pos=133564345, ref="C", alt="T"),
            ],
        )
        self.assess_variant_prioritisation_ascending_order = AssessVariantPrioritisation(
            phenopacket_path=Path("/path/to/phenopacket.json"),
            results_dir=Path("/path/to/results_dir"),
            standardised_variant_results=variant_results,
            threshold=0.0,
            score_order="ascending",
            proband_causative_variants=[
                GenomicVariant(chrom="3", pos=126741108, ref="G", alt="A"),
                GenomicVariant(chrom="16", pos=133564345, ref="C", alt="T"),
            ],
        )
        self.variant_rank_stats = RankStats()
        self.variant_rank_records = defaultdict(dict)

    def test_record_variant_prioritisation_match(self):
        self.assertEqual(
            self.assess_variant_prioritisation._record_variant_prioritisation_match(
                result_entry=RankedPhEvalVariantResult(
                    PhEvalVariantResult(
                        chromosome="3",
                        start=126741108,
                        end=126741108,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
                rank_stats=self.variant_rank_stats,
            ),
            VariantPrioritisationResult(
                phenopacket_path=Path("/path/to/phenopacket.json"),
                variant=GenomicVariant(chrom="3", pos=126741108, ref="G", alt="A"),
                rank=1,
            ),
        )

    def test_assess_variant_with_ascending_order_threshold_fails_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation_ascending_order)
        assess_with_threshold.threshold = 0.01
        self.assertEqual(
            assess_with_threshold._assess_variant_with_threshold_ascending_order(
                result_entry=RankedPhEvalVariantResult(
                    PhEvalVariantResult(
                        chromosome="3",
                        start=126741108,
                        end=126741108,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
                rank_stats=self.variant_rank_stats,
            ),
            None,
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=0, reciprocal_ranks=[]),
        )

    def test_assess_variant_with_ascending_order_threshold_meets_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation_ascending_order)
        assess_with_threshold.threshold = 0.9
        self.assertEqual(
            assess_with_threshold._assess_variant_with_threshold_ascending_order(
                result_entry=RankedPhEvalVariantResult(
                    PhEvalVariantResult(
                        chromosome="3",
                        start=126741108,
                        end=126741108,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
                rank_stats=self.variant_rank_stats,
            ),
            VariantPrioritisationResult(
                phenopacket_path=Path("/path/to/phenopacket.json"),
                variant=GenomicVariant(chrom="3", pos=126741108, ref="G", alt="A"),
                rank=1,
            ),
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=0, reciprocal_ranks=[1.0]),
        )

    def test_assess_variant_with_threshold_fails_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation)
        assess_with_threshold.threshold = 0.9
        self.assertEqual(
            assess_with_threshold._assess_variant_with_threshold(
                result_entry=RankedPhEvalVariantResult(
                    PhEvalVariantResult(
                        chromosome="3",
                        start=126741108,
                        end=126741108,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
                rank_stats=self.variant_rank_stats,
            ),
            None,
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=0, reciprocal_ranks=[]),
        )

    def test_assess_variant_with_threshold_meets_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation)
        assess_with_threshold.threshold = 0.01
        self.assertEqual(
            assess_with_threshold._assess_variant_with_threshold(
                result_entry=RankedPhEvalVariantResult(
                    PhEvalVariantResult(
                        chromosome="3",
                        start=126741108,
                        end=126741108,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
                rank_stats=self.variant_rank_stats,
            ),
            VariantPrioritisationResult(
                phenopacket_path=Path("/path/to/phenopacket.json"),
                variant=GenomicVariant(chrom="3", pos=126741108, ref="G", alt="A"),
                rank=1,
            ),
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=0, reciprocal_ranks=[1.0]),
        )

    def test_assess_variant_prioritisation_no_threshold(self):
        self.assess_variant_prioritisation.assess_variant_prioritisation(
            self.variant_rank_stats, self.variant_rank_records
        )

        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=2, reciprocal_ranks=[1.0]),
        )
        self.assertEqual(
            self.variant_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "3_126741108_G_A",
                    Path("/path/to/results_dir"): 1,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "16_133564345_C_T",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_variant_prioritisation_fails_ascending_order_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation_ascending_order)
        assess_with_threshold.threshold = 0.01
        assess_with_threshold.assess_variant_prioritisation(
            self.variant_rank_stats, self.variant_rank_records
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=2, reciprocal_ranks=[]),
        )
        self.assertEqual(
            self.variant_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "3_126741108_G_A",
                    Path("/path/to/results_dir"): 0,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "16_133564345_C_T",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_variant_prioritisation_meets_ascending_order_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation_ascending_order)
        assess_with_threshold.threshold = 0.9
        assess_with_threshold.assess_variant_prioritisation(
            self.variant_rank_stats, self.variant_rank_records
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=2, reciprocal_ranks=[1.0]),
        )
        self.assertEqual(
            self.variant_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "3_126741108_G_A",
                    Path("/path/to/results_dir"): 1,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "16_133564345_C_T",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_variant_prioritisation_fails_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation)
        assess_with_threshold.threshold = 0.9
        assess_with_threshold.assess_variant_prioritisation(
            self.variant_rank_stats, self.variant_rank_records
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=0, top3=0, top5=0, top10=0, found=0, total=2, reciprocal_ranks=[]),
        )
        self.assertEqual(
            self.variant_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "3_126741108_G_A",
                    Path("/path/to/results_dir"): 0,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "16_133564345_C_T",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )

    def test_assess_variant_prioritisation_meets_cutoff(self):
        assess_with_threshold = copy(self.assess_variant_prioritisation_ascending_order)
        assess_with_threshold.threshold = 0.1
        assess_with_threshold.assess_variant_prioritisation(
            self.variant_rank_stats, self.variant_rank_records
        )
        self.assertEqual(
            self.variant_rank_stats,
            RankStats(top=1, top3=1, top5=1, top10=1, found=1, total=2, reciprocal_ranks=[1.0]),
        )
        self.assertEqual(
            self.variant_rank_records,
            {
                1: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "3_126741108_G_A",
                    Path("/path/to/results_dir"): 1,
                },
                2: {
                    "Phenopacket": "phenopacket.json",
                    "Variant": "16_133564345_C_T",
                    Path("/path/to/results_dir"): 0,
                },
            },
        )


class TestMergeResults(unittest.TestCase):
    def setUp(self) -> None:
        self.result_1 = {
            1: {
                "Phenopacket": "phenopacket1.json",
                "Gene": "GCDH",
                "/path/to/results_directory1": 1,
            }
        }
        self.result_2 = {
            1: {
                "Phenopacket": "phenopacket1.json",
                "Gene": "GCDH",
                "/path/to/results_directory2": 5,
            }
        }

    def test_merge_results(self):
        self.assertEqual(
            merge_results(self.result_1, self.result_2),
            {
                1: {
                    "Phenopacket": "phenopacket1.json",
                    "Gene": "GCDH",
                    "/path/to/results_directory1": 1,
                    "/path/to/results_directory2": 5,
                }
            },
        )


class TestRankComparisonGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gene_rank_comparisons = RankComparisonGenerator(
            defaultdict(
                dict,
                {
                    1: {
                        "Phenopacket": "phenopacket1.json",
                        "Gene": "GCDH",
                        "/path/to/results_directory1": 1,
                        "/path/to/results_directory2": 5,
                    }
                },
            )
        )
        self.variant_rank_comparisons = RankComparisonGenerator(
            defaultdict(
                dict,
                {
                    1: {
                        "Phenopacket": "phenopacket1.json",
                        "Variant": "3_12563453454_C_T",
                        "/path/to/results_directory1": 9,
                        "/path/to/results_directory2": 3,
                    }
                },
            )
        )

    def test_generate_gene_dataframe(self):
        result = pd.DataFrame(
            [
                {
                    "Phenopacket": "phenopacket1.json",
                    "Gene": "GCDH",
                    "/path/to/results_directory1": 1,
                    "/path/to/results_directory2": 5,
                }
            ]
        )
        result.index += 1
        self.assertTrue(result.equals(self.gene_rank_comparisons._generate_dataframe()))

    def test_generate_variant_dataframe(self):
        result = pd.DataFrame(
            [
                {
                    "Phenopacket": "phenopacket1.json",
                    "Variant": "3_12563453454_C_T",
                    "/path/to/results_directory1": 9,
                    "/path/to/results_directory2": 3,
                }
            ]
        )
        result.index += 1
        self.assertTrue(result.equals(self.variant_rank_comparisons._generate_dataframe()))

    def test_calculate_gene_rank_difference(self):
        result = pd.DataFrame(
            [
                {
                    "Phenopacket": "phenopacket1.json",
                    "Gene": "GCDH",
                    "/path/to/results_directory1": 1,
                    "/path/to/results_directory2": 5,
                    "rank_decrease": 4,
                }
            ]
        )
        result.index += 1
        self.assertTrue(result.equals(self.gene_rank_comparisons._calculate_rank_difference()))

    def test_calculate_variant_rank_difference(self):
        result = pd.DataFrame(
            [
                {
                    "Phenopacket": "phenopacket1.json",
                    "Variant": "3_12563453454_C_T",
                    "/path/to/results_directory1": 9,
                    "/path/to/results_directory2": 3,
                    "rank_decrease": -6,
                }
            ]
        )
        result.index += 1
        self.assertTrue(result.equals(self.variant_rank_comparisons._calculate_rank_difference()))


class TestParsePhEvalGeneResult(unittest.TestCase):
    def test_parse_pheval_gene_result(self):
        self.assertEqual(
            parse_pheval_gene_result(
                pd.DataFrame(
                    [
                        {
                            "gene_symbol": "PLXNA1",
                            "gene_identifier": "ENSG00000114554",
                            "score": 0.8764,
                            "rank": 1,
                        },
                        {
                            "gene_symbol": "ZNF804B",
                            "gene_identifier": "ENSG00000182348",
                            "score": 0.5777,
                            "rank": 2,
                        },
                        {
                            "gene_symbol": "SMCO2",
                            "gene_identifier": "ENSG00000165935",
                            "score": 0.5777,
                            "rank": 2,
                        },
                        {
                            "gene_symbol": "SPNS1",
                            "gene_identifier": "ENSG00000169682",
                            "score": 0.3765,
                            "rank": 4,
                        },
                    ]
                )
            ),
            [
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="PLXNA1", gene_identifier="ENSG00000114554", score=0.8764
                    ),
                    rank=1,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="ZNF804B", gene_identifier="ENSG00000182348", score=0.5777
                    ),
                    rank=2,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="SMCO2", gene_identifier="ENSG00000165935", score=0.5777
                    ),
                    rank=2,
                ),
                RankedPhEvalGeneResult(
                    pheval_gene_result=PhEvalGeneResult(
                        gene_symbol="SPNS1", gene_identifier="ENSG00000169682", score=0.3765
                    ),
                    rank=4,
                ),
            ],
        )


class TestParsePhEvalVariantResult(unittest.TestCase):
    def test_parse_pheval_variant_result(self):
        self.assertEqual(
            parse_pheval_variant_result(
                pd.DataFrame(
                    [
                        {
                            "chromosome": "3",
                            "start": 126730873,
                            "end": 126730873,
                            "ref": "G",
                            "alt": "A",
                            "gene": "PLXNA1",
                            "score": 0.0484,
                            "rank": 1,
                        },
                        {
                            "chromosome": "3",
                            "start": 126730873,
                            "end": 126730873,
                            "ref": "G",
                            "alt": "A",
                            "gene": "PLXNA1",
                            "score": 0.0484,
                            "rank": 1,
                        },
                        {
                            "chromosome": "3",
                            "start": 126741108,
                            "end": 126741108,
                            "ref": "G",
                            "alt": "A",
                            "gene": "PLXNA1",
                            "score": 0.0484,
                            "rank": 1,
                        },
                    ]
                )
            ),
            [
                RankedPhEvalVariantResult(
                    pheval_variant_result=PhEvalVariantResult(
                        chromosome="3",
                        start=126730873,
                        end=126730873,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
                RankedPhEvalVariantResult(
                    pheval_variant_result=PhEvalVariantResult(
                        chromosome="3",
                        start=126730873,
                        end=126730873,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
                RankedPhEvalVariantResult(
                    pheval_variant_result=PhEvalVariantResult(
                        chromosome="3",
                        start=126741108,
                        end=126741108,
                        ref="G",
                        alt="A",
                        score=0.0484,
                    ),
                    rank=1,
                ),
            ],
        )


class TestPlotGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gene_plot_generator = PlotGenerator(gene_analysis=True)
        self.variant_plot_generator = PlotGenerator(gene_analysis=False)
        self.track_prioritisation = TrackPrioritisation(
            gene_prioritisation=TrackGenePrioritisation(
                results_dir=Path("/path/to/results_dir"),
                ranks={},
                rank_stats=RankStats(
                    top=1,
                    top3=2,
                    top5=3,
                    top10=9,
                    found=20,
                    total=30,
                    reciprocal_ranks=[1, 1 / 3, 1 / 5, 1 / 10, 1 / 50],
                ),
            ),
            variant_prioritisation=TrackVariantPrioritisation(
                results_dir=Path("/path/to/results_dir"),
                ranks={},
                rank_stats=RankStats(
                    top=1,
                    top3=2,
                    top5=3,
                    top10=4,
                    found=5,
                    total=2,
                    reciprocal_ranks=[1, 1 / 3, 1 / 5, 1 / 10, 1 / 12],
                ),
            ),
        )

    def test__retrieve_prioritisation_data_gene(self):
        self.assertEqual(
            self.gene_plot_generator._retrieve_prioritisation_data(self.track_prioritisation),
            TrackGenePrioritisation(
                results_dir=Path("/path/to/results_dir"),
                ranks={},
                rank_stats=RankStats(
                    top=1,
                    top3=2,
                    top5=3,
                    top10=9,
                    found=20,
                    total=30,
                    reciprocal_ranks=[1, 0.3333333333333333, 0.2, 0.1, 0.02],
                ),
            ),
        )

    def test__retrieve_prioritisation_data_variant(self):
        self.assertEqual(
            self.variant_plot_generator._retrieve_prioritisation_data(self.track_prioritisation),
            TrackVariantPrioritisation(
                results_dir=PosixPath("/path/to/results_dir"),
                ranks={},
                rank_stats=RankStats(
                    top=1,
                    top3=2,
                    top5=3,
                    top10=4,
                    found=5,
                    total=2,
                    reciprocal_ranks=[1, 0.3333333333333333, 0.2, 0.1, 0.08333333333333333],
                ),
            ),
        )

    def test__generate_stacked_bar_plot_data(self):
        self.gene_plot_generator._generate_stacked_bar_plot_data(self.track_prioritisation)
        self.assertEqual(
            self.gene_plot_generator.stats,
            [
                {
                    "2-3": 5.0,
                    "4-5": 5.0,
                    "6-10": 30.0,
                    ">10": 21.66666666666667,
                    "FO/NP": 33.33333333333333,
                    "Run": "results_dir",
                    "Top": 5.0,
                }
            ],
        )

    def test__generate_stats_mrr_bar_plot_data(self):
        self.gene_plot_generator._generate_stats_mrr_bar_plot_data(self.track_prioritisation)
        self.assertEqual(
            self.gene_plot_generator.mrr,
            [{"Rank": "MRR", "Percentage": 0.33066666666666666, "Run": "results_dir"}],
        )

    def test__generate_cumulative_bar_plot_data(self):
        self.gene_plot_generator._generate_cumulative_bar_plot_data(self.track_prioritisation)
        self.assertEqual(
            self.gene_plot_generator.stats,
            [
                {"Rank": "Top", "Percentage": 0.05, "Run": "results_dir"},
                {"Rank": "Top3", "Percentage": 0.1, "Run": "results_dir"},
                {"Rank": "Top5", "Percentage": 0.15, "Run": "results_dir"},
                {"Rank": "Top10", "Percentage": 0.45, "Run": "results_dir"},
                {"Rank": "Found", "Percentage": 0.6666666666666667, "Run": "results_dir"},
                {"Rank": "FO/NP", "Percentage": 0.33333333333333326, "Run": "results_dir"},
                {"Rank": "MRR", "Percentage": 0.33066666666666666, "Run": "results_dir"},
            ],
        )

    def test__generate_non_cumulative_bar_plot_data(self):
        self.gene_plot_generator._generate_non_cumulative_bar_plot_data(self.track_prioritisation)
        self.assertEqual(
            self.gene_plot_generator.stats,
            [
                {"Rank": "Top", "Percentage": 0.05, "Run": "results_dir"},
                {"Rank": "2-3", "Percentage": 0.05, "Run": "results_dir"},
                {"Rank": "4-5", "Percentage": 0.05, "Run": "results_dir"},
                {"Rank": "6-10", "Percentage": 0.3, "Run": "results_dir"},
                {"Rank": ">10", "Percentage": 0.2166666666666667, "Run": "results_dir"},
                {"Rank": "FO/NP", "Percentage": 0.33333333333333326, "Run": "results_dir"},
                {"Rank": "MRR", "Percentage": 0.33066666666666666, "Run": "results_dir"},
            ],
        )
