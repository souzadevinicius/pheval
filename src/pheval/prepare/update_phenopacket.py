from collections import defaultdict
from pathlib import Path
from typing import Union

from phenopackets import Family, Phenopacket

from pheval.utils.file_utils import all_files
from pheval.utils.phenopacket_utils import (
    GeneIdentifierUpdater,
    PhenopacketRebuilder,
    PhenopacketUtil,
    create_hgnc_dict,
    phenopacket_reader,
    write_phenopacket,
)


def update_outdated_gene_context(
    phenopacket_path: Path, gene_identifier: str, hgnc_data: defaultdict
) -> Union[Phenopacket, Family]:
    """
    Update the gene context of the Phenopacket.

    Args:
        phenopacket_path (Path): The path to the Phenopacket file.
        gene_identifier (str): Identifier to update the gene context.
        hgnc_data (defaultdict): The HGNC data used for updating.

    Returns:
        Union[Phenopacket, Family]: The updated Phenopacket or Family.
    """
    phenopacket = phenopacket_reader(phenopacket_path)
    interpretations = PhenopacketUtil(phenopacket).interpretations()
    updated_interpretations = GeneIdentifierUpdater(
        hgnc_data=hgnc_data, gene_identifier=gene_identifier
    ).update_genomic_interpretations_gene_identifier(interpretations)

    return PhenopacketRebuilder(phenopacket).update_interpretations(updated_interpretations)


def create_updated_phenopacket(
    gene_identifier: str, phenopacket_path: Path, output_dir: Path
) -> None:
    """
    Update the gene context within the interpretations for a Phenopacket and writes the updated Phenopacket.

    Args:
        gene_identifier (str): Identifier used to update the gene context.
        phenopacket_path (Path): The path to the input Phenopacket file.
        output_dir (Path): The directory where the updated Phenopacket will be written.
    """
    hgnc_data = create_hgnc_dict()
    updated_phenopacket = update_outdated_gene_context(phenopacket_path, gene_identifier, hgnc_data)
    write_phenopacket(updated_phenopacket, output_dir.joinpath(phenopacket_path.name))


def create_updated_phenopackets(
    gene_identifier: str, phenopacket_dir: Path, output_dir: Path
) -> None:
    """
    Update the gene context within the interpretations for a directory of Phenopackets
    and writes the updated Phenopackets.

    Args:
        gene_identifier (str): Identifier used to update the gene context.
        phenopacket_dir (Path): The path to the input Phenopacket directory.
        output_dir (Path): The directory where the updated Phenopackets will be written.
    """
    hgnc_data = create_hgnc_dict()
    for phenopacket_path in all_files(phenopacket_dir):
        updated_phenopacket = update_outdated_gene_context(
            phenopacket_path, gene_identifier, hgnc_data
        )
        write_phenopacket(updated_phenopacket, output_dir.joinpath(phenopacket_path.name))


def update_phenopackets(
    gene_identifier: str, phenopacket_path: Path, phenopacket_dir: Path, output_dir: Path
) -> None:
    """
    Update the gene identifiers in either a single phenopacket or a directory of phenopackets.

    Args:
        gene_identifier (str): The gene identifier to be updated.
        phenopacket_path (Path): The path to a single Phenopacket file.
        phenopacket_dir (Path): The directory containing multiple Phenopacket files.
        output_dir (Path): The output directory to save the updated Phenopacket files.
    """
    output_dir.mkdir(exist_ok=True)
    if phenopacket_path is not None:
        create_updated_phenopacket(gene_identifier, phenopacket_path, output_dir)
    elif phenopacket_dir is not None:
        create_updated_phenopackets(gene_identifier, phenopacket_dir, output_dir)
