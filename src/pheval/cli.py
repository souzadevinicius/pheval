"""PhEval CLI Module """
import logging

import click

from pheval.analyse.analysis import benchmark, benchmark_comparison
from pheval.prepare.update_phenopacket import (
    update_phenopacket_command,
    update_phenopackets_command,
)

from .cli_pheval import run
from .cli_pheval_utils import scramble_semsim, semsim_comparison
from .prepare.create_noisy_phenopackets import (
    scramble_phenopacket_command,
    scramble_phenopackets_command,
)
from .prepare.create_spiked_vcf import create_spiked_vcf_command, create_spiked_vcfs_command

info_log = logging.getLogger("info")


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
def main(verbose=1, quiet=False) -> None:
    """main CLI method for PhEval

    Args:
        verbose (int, optional): Verbose flag.
        quiet (bool, optional): Queit Flag.
    """
    if verbose >= 2:
        info_log.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        info_log.setLevel(level=logging.INFO)
    else:
        info_log.setLevel(level=logging.WARNING)
    if quiet:
        info_log.setLevel(level=logging.ERROR)


@click.group()
def pheval():
    """pheval"""


pheval.add_command(run)


@click.group()
def pheval_utils():
    """pheval_utils"""


pheval_utils.add_command(scramble_semsim)
pheval_utils.add_command(semsim_comparison)
pheval_utils.add_command(scramble_phenopackets_command)
pheval_utils.add_command(scramble_phenopacket_command)
pheval_utils.add_command(update_phenopacket_command)
pheval_utils.add_command(update_phenopackets_command)
pheval_utils.add_command(create_spiked_vcfs_command)
pheval_utils.add_command(create_spiked_vcf_command)
pheval_utils.add_command(benchmark)
pheval_utils.add_command(benchmark_comparison)


if __name__ == "__main__":
    main()
