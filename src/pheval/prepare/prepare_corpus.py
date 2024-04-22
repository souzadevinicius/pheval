import logging
from pathlib import Path

from pheval.prepare.create_spiked_vcf import create_spiked_vcf
from pheval.prepare.update_phenopacket import create_updated_phenopacket
from pheval.utils.file_utils import all_files
from pheval.utils.phenopacket_utils import PhenopacketUtil, phenopacket_reader

info_log = logging.getLogger("info")


def prepare_corpus(
    phenopacket_dir: Path,
    variant_analysis: bool,
    gene_analysis: bool,
    disease_analysis: bool,
    gene_identifier: str,
    hg19_template_vcf: Path,
    hg38_template_vcf: Path,
    output_dir: Path,
) -> None:
    """
    Prepare a corpus of Phenopackets for analysis, optionally checking for complete variant records and updating
    gene identifiers.

    Args:
        phenopacket_dir (Path): The path to the directory containing Phenopackets.
        variant_analysis (bool): If True, check for complete variant records in the Phenopackets.
        gene_analysis (bool): If True, check for complete gene records in the Phenopackets.
        disease_analysis (bool): If True, check for complete disease records in the Phenopackets.
        gene_identifier (str): Identifier for updating gene identifiers, if applicable.
        hg19_template_vcf (Path): Path to the hg19 template VCF file (optional).
        hg38_template_vcf (Path): Path to the hg38 template VCF file (optional).
        output_dir (Path): The directory to save the prepared Phenopackets and, optionally, VCF files.
    """
    output_dir.joinpath("phenopackets").mkdir(exist_ok=True, parents=True)
    for phenopacket_path in all_files(phenopacket_dir):
        phenopacket_util = PhenopacketUtil(phenopacket_reader(phenopacket_path))
        if variant_analysis:
            if phenopacket_util.check_incomplete_variant_record():
                info_log.warning(
                    f"Removed {phenopacket_path.name} from the corpus due to missing variant fields."
                )
                continue
        if gene_analysis:
            if phenopacket_util.check_incomplete_gene_record():
                info_log.warning(
                    f"Removed {phenopacket_path.name} from the corpus due to missing gene fields."
                )
                continue
        if disease_analysis:
            if phenopacket_util.check_incomplete_disease_record():
                info_log.warning(
                    f"Removed {phenopacket_path.name} from the corpus due to missing disease fields."
                )
                continue
        if gene_identifier:
            create_updated_phenopacket(
                gene_identifier, phenopacket_path, output_dir.joinpath("phenopackets")
            )
        if hg19_template_vcf or hg38_template_vcf:
            output_dir.joinpath("vcf").mkdir(exist_ok=True)
            create_spiked_vcf(
                output_dir.joinpath("vcf"), phenopacket_path, hg19_template_vcf, hg38_template_vcf
            )
