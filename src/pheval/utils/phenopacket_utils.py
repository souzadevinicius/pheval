import json
import os
from collections import defaultdict

import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from google.protobuf.json_format import MessageToJson, Parse
from phenopackets import Family, File, Phenopacket, PhenotypicFeature

from pheval.prepare.custom_exceptions import IncorrectFileFormatError


class IncompatibleGenomeAssemblyError(Exception):
    """Exception raised for incompatible genome assembly."""

    def __init__(self, assembly, phenopacket, message="Incompatible Genome Assembly"):
        self.assembly: str = assembly
        self.phenopacket: Path = phenopacket
        self.message: str = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} -> {self.assembly} in {self.phenopacket}"


@dataclass
class VariantData:
    chrom: str
    pos: int
    ref: str
    alt: str
    gene: Optional[str] = None


@dataclass
class ProbandCausativeVariant:
    phenopacket: Path
    proband_id: str
    assembly: str
    variant: VariantData
    genotype: str


def read_hgnc_data() -> pd.DataFrame:
    return pd.read_csv(os.path.dirname(__file__).replace("utils", "resources/hgnc_complete_set_2022-10-01.txt"),
                       delimiter="\t", dtype=str)


def create_hgnc_dict() -> defaultdict:
    hgnc_df = read_hgnc_data()
    hgnc_data = defaultdict(dict)
    for index, row in hgnc_df.iterrows():
        previous_names = []
        hgnc_data[row["symbol"]]["ensembl_id"] = row["ensembl_gene_id"]
        hgnc_data[row["symbol"]]["hgnc_id"] = row["hgnc_id"]
        hgnc_data[row["symbol"]]["entrez_id"] = row["entrez_id"]
        previous = str(row["prev_symbol"]).split("|")
        for p in previous:
            previous_names.append(p.strip('"'))
        hgnc_data[row["symbol"]]["previous_symbol"] = previous_names
    return hgnc_data


def phenopacket_reader(file: Path):
    """Reads a phenopacket file, returning its contents."""
    file = open(file, "r")
    phenopacket = json.load(file)
    file.close()
    if "proband" in phenopacket:
        return Parse(json.dumps(phenopacket), Family())
    else:
        return Parse(json.dumps(phenopacket), Phenopacket())


class PhenopacketUtil:
    """Retrieves relevant data from a phenopacket."""

    def __init__(self, phenopacket_contents: Phenopacket):
        self.phenopacket_contents = phenopacket_contents

    def phenotypic_features(self) -> list[PhenotypicFeature]:
        """Retrieves a list of all HPO terms."""
        if hasattr(self.phenopacket_contents, "proband"):
            return self.phenopacket_contents.proband.phenotypic_features
        else:
            return self.phenopacket_contents.phenotypic_features

    def remove_excluded_phenotypic_features(self) -> list[PhenotypicFeature]:
        """Removes any HPO terms labelled as excluded."""
        phenotypic_features = []
        all_phenotypic_features = self.phenotypic_features()
        for p in all_phenotypic_features:
            if p.excluded:
                continue
            phenotypic_features.append(p)
        return phenotypic_features

    def interpretations(self) -> list:
        """Returns all interpretations of a phenopacket."""
        if hasattr(self.phenopacket_contents, "proband"):
            return self.phenopacket_contents.proband.interpretations
        else:
            return self.phenopacket_contents.interpretations

    def causative_variants(self, file: Path) -> list[ProbandCausativeVariant]:
        """Returns a list of all causative variants listed in a phenopacket."""
        all_variants = []
        interpretation = self.interpretations()
        for i in interpretation:
            for g in i.diagnosis.genomic_interpretations:
                vcf_record = g.variant_interpretation.variation_descriptor.vcf_record
                genotype = g.variant_interpretation.variation_descriptor.allelic_state
                variant_data = ProbandCausativeVariant(
                    file,
                    self.phenopacket_contents.subject.id,
                    vcf_record.genome_assembly,
                    VariantData(
                        vcf_record.chrom,
                        vcf_record.pos,
                        vcf_record.ref,
                        vcf_record.alt,
                        g.variant_interpretation.variation_descriptor.gene_context.symbol,
                    ),
                    genotype.label,
                )
                all_variants.append(variant_data)
        return all_variants

    def files(self) -> list:
        """Returns all files associated with a phenopacket."""
        return self.phenopacket_contents.files

    def vcf_file_data(self, phenopacket: Path, vcf_dir: Path) -> File:
        """Retrieves the genome assembly and vcf name from a phenopacket."""
        compatible_genome_assembly = ["GRCh37", "hg19", "GRCh38", "hg38"]
        vcf_data = [file for file in self.files() if file.file_attributes["fileFormat"] == "VCF"][0]
        if not Path(vcf_data.uri).name.endswith(".vcf") and not Path(vcf_data.uri).name.endswith(
                ".vcf.gz"
        ):
            raise IncorrectFileFormatError(Path(vcf_data.uri), ".vcf or .vcf.gz file")
        if vcf_data.file_attributes["genomeAssembly"] not in compatible_genome_assembly:
            raise IncompatibleGenomeAssemblyError(
                vcf_data.file_attributes["genomeAssembly"], phenopacket
            )
        vcf_data.uri = str(vcf_dir.joinpath(Path(vcf_data.uri).name))
        return vcf_data

    def diagnosed_genes(self) -> list[str]:
        """Returns a unique list of all causative genes from a phenopacket."""
        pheno_interpretation = self.interpretations()
        genes = []
        for i in pheno_interpretation:
            for g in i.diagnosis.genomic_interpretations:
                genes.append(g.variant_interpretation.variation_descriptor.gene_context.symbol)
        genes = list(set(genes))
        return genes

    def diagnosed_variants(self) -> list[VariantData]:
        """Returns a list of all variants from a phenopacket - for use in assess-prioritisation."""
        variants = []
        pheno_interpretation = self.interpretations()
        for i in pheno_interpretation:
            for g in i.diagnosis.genomic_interpretations:
                variant = VariantData(
                    chrom=g.variant_interpretation.variation_descriptor.vcf_record.chrom,
                    pos=g.variant_interpretation.variation_descriptor.vcf_record.pos,
                    ref=g.variant_interpretation.variation_descriptor.vcf_record.ref,
                    alt=g.variant_interpretation.variation_descriptor.vcf_record.alt,
                    gene=g.variant_interpretation.variation_descriptor.gene_context.symbol,
                )
                variants.append(variant)
        return variants


class PhenopacketRebuilder:
    """Rebuilds a Phenopacket."""

    def __init__(self, phenopacket_contents):
        self.phenopacket_contents = phenopacket_contents

    def add_randomised_hpo(self, randomised_hpo):
        """Adds randomised phenotypic profile to phenopacket."""
        if hasattr(self.phenopacket_contents, "proband"):
            del self.phenopacket_contents.proband.phenotypic_features[:]
            self.phenopacket_contents.proband.phenotypic_features.extend(randomised_hpo)
        else:
            del self.phenopacket_contents.phenotypic_features[:]
            self.phenopacket_contents.phenotypic_features.extend(randomised_hpo)

    def add_created_vcf_path(self, vcf_path: Path, genome_assembly: str):
        phenopacket_files = [
            file
            for file in self.phenopacket_contents.files
            if file.file_attributes["fileFormat"] != "VCF"
        ]
        vcf_file_entry = File(
            uri=os.path.abspath(vcf_path),
            file_attributes={"fileFormat": "VCF", "genomeAssembly": genome_assembly},
        )
        phenopacket_files.append(vcf_file_entry)
        del self.phenopacket_contents.files[:]
        self.phenopacket_contents.files.extend(phenopacket_files)

    def create_json_message(self) -> str:
        """Creates json message for writing to file."""
        return MessageToJson(self.phenopacket_contents)

    def write_phenopacket(self, output_file: Path):
        phenopacket = self.create_json_message()
        with open(output_file, "w") as outfile:
            outfile.write(phenopacket)
        outfile.close()


class PhenopacketUpdater:
    def __init__(self, phenopacket_contents: Phenopacket, hgnc_data: defaultdict, gene_identifier: str):
        self.phenopacket_contents = phenopacket_contents
        self.hgnc_data = hgnc_data
        self.gene_identifier = gene_identifier

    def update_identifier(self, gene_symbol: str) -> str:
        if gene_symbol in self.hgnc_data.keys():
            return self.hgnc_data[gene_symbol][self.gene_identifier]
        else:
            for _symbol, data in self.hgnc_data.items():
                for prev_symbol in data["previous_symbol"]:
                    if prev_symbol == gene_symbol:
                        return data[self.gene_identifier]

    def update_gene_symbol(self, gene_symbol: str) -> str:
        if gene_symbol in self.hgnc_data.keys():
            return gene_symbol
        else:
            for symbol, data in self.hgnc_data.items():
                for prev_symbol in data["previous_symbol"]:
                    if prev_symbol == gene_symbol:
                        return symbol

    def update_gene_context_phenopacket(self) -> Phenopacket:
        for i in self.phenopacket_contents.interpretations:
            for g in i.diagnosis.genomic_interpretations:
                g.variant_interpretation.variation_descriptor.gene_context.symbol = self.update_gene_symbol(
                    g.variant_interpretation.variation_descriptor.gene_context.symbol)
                g.variant_interpretation.variation_descriptor.gene_context.value_id = self.update_identifier(
                    g.variant_interpretation.variation_descriptor.gene_context.symbol)
        return self.phenopacket_contents

    def update_gene_context_family(self) -> Phenopacket:
        for i in self.phenopacket_contents.proband.interpretations:
            for g in i.diagnosis.genomic_interpretations:
                g.variant_interpretation.variation_descriptor.gene_context.symbol = self.update_gene_symbol(
                    g.variant_interpretation.variation_descriptor.gene_context.symbol)
                g.variant_interpretation.variation_descriptor.gene_context.value_id = self.update_identifier(
                    g.variant_interpretation.variation_descriptor.gene_context.symbol)
        return self.phenopacket_contents

    def update_phenopacket_interpretations(self) -> Phenopacket:
        if hasattr(self.phenopacket_contents, "proband"):
            return self.update_gene_context_family()
        else:
            return self.update_gene_context_phenopacket()
