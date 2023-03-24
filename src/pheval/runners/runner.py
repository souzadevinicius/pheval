"""Runners Module"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from pheval.config_parser import parse_input_dir_config


@dataclass
class PhEvalRunner(ABC):
    """PhEvalRunner Class"""

    input_dir: Path
    testdata_dir: Path
    tmp_dir: Path
    output_dir: Path
    config_file: Path
    version: str
    directory_path = None
    input_dir_config = None
    __raw_results_dir = "raw_results/"
    __pheval_gene_results_dir = "pheval_gene_results/"
    __pheval_variant_results_dir = "pheval_variant_results/"
    __tool_input_commands_dir = "tool_input_commands/"

    def __post_init__(self):
        self.input_dir_config = parse_input_dir_config(self.input_dir)

    def _get_tool(self):
        return self.input_dir_config.tool

    def _get_phenotype_only(self):
        return self.input_dir_config.phenotype_only

    @property
    def tool_input_commands_dir(self):
        return Path(self.output_dir).joinpath(self.__tool_input_commands_dir)

    @tool_input_commands_dir.setter
    def tool_input_commands_dir(self, directory_path):
        self.directory_path = Path(directory_path)

    @property
    def raw_results_dir(self):
        return Path(self.output_dir).joinpath(self.__raw_results_dir)

    @raw_results_dir.setter
    def raw_results_dir(self, directory_path):
        self.directory_path = Path(directory_path)

    @property
    def pheval_gene_results_dir(self):
        return Path(self.output_dir).joinpath(self.__pheval_gene_results_dir)

    @pheval_gene_results_dir.setter
    def pheval_gene_results_dir(self, directory_path):
        self.directory_path = Path(directory_path)

    @property
    def pheval_variant_results_dir(self):
        return Path(self.output_dir).joinpath(self.__pheval_variant_results_dir)

    @pheval_variant_results_dir.setter
    def pheval_variant_results_dir(self, directory_path):
        self.directory_path = Path(directory_path)

    def build_output_directory_structure(self):
        """build output directory structure"""
        self.tool_input_commands_dir.mkdir()
        self.raw_results_dir.mkdir()
        self.pheval_gene_results_dir.mkdir()
        if not self._get_phenotype_only():
            self.pheval_variant_results_dir.mkdir()

    @abstractmethod
    def prepare(self) -> str:
        """prepare"""

    @abstractmethod
    def run(self):
        """run"""

    @abstractmethod
    def post_process(self):
        """post_process"""


class DefaultPhEvalRunner(PhEvalRunner):
    """DefaultPhEvalRunner

    Args:
        PhEvalRunner (PhEvalRunner): Abstract PhEvalRunnerClass
    """

    input_dir: Path
    testdata_dir: Path
    tmp_dir: Path
    output_dir: Path
    config_file: Path
    version: str

    def prepare(self):
        print("preparing")

    def run(self):
        print("running")

    def post_process(self):
        print("post processing")
