MAKEFLAGS 				+= --warn-undefined-variables
SHELL 					:= bash
.DEFAULT_GOAL			:= help
URIBASE					:=	http://purl.obolibrary.org/obo
TEST_DATA				:=	testdata
TMP_DATA				:=	data/tmp
ROOT_DIR				:=	/tmp/pheval
NAME					:= $(shell python -c 'import tomli; print(tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["name"])')
VERSION					:= $(shell python -c 'import tomli; print(tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"])')
H2_JAR					:= ./h2-1.4.199.jar
help: info
	@echo ""
	@echo "help"
	@echo "make pheval -- this runs the entire pipeline including corpus preparation and pheval run"
	@echo "make semsim -- generate all configured similarity profiles"
	@echo "make semsim-shuffle -- generate new ontology terms to the semsim process"
	@echo "make semsim-scramble -- scramble semsim profile"
	@echo "make semsim-convert -- convert all semsim profiles into exomiser SQL format"
	@echo "make semsim-ingest -- takes all the configured semsim profiles and loads them into the exomiser databases"

	@echo "make clean -- removes corpora and pheval results"
	@echo "make help -- show this help"
	@echo ""

info:
	@echo "Project: $(NAME)"
	@echo "Version: $(VERSION)"

.PHONY: prepare-inputs
prepare-inputs: configurations/exomiser-13.2.0-default/config.yaml

configurations/exomiser-13.2.0-default/config.yaml:
	rm -rf $(ROOT_DIR)/$(shell dirname $@)
	mkdir -p $(ROOT_DIR)/$(shell dirname $@)
	ln -s /home/data/exomiser/exomiser-cli-13.2.0-distribution/exomiser-cli-13.2.0/* $(ROOT_DIR)/$(shell dirname $@)
	ln -s /home/data/phenotype/* $(ROOT_DIR)/$(shell dirname $@)

configurations/exomiser-13.2.0/default/2302_phenotype/2302_phenotype.h2.db: $(TMP_DATA)/semsim1.sql
	test -d configurations/exomiser-13.2.0/default/ || mkdir -p configurations/exomiser-13.2.0/default/
	test -d configurations/exomiser-13.2.0/default/2302_phenotype/ || cp -rf /home/data/phenotype configurations/exomiser-13.2.0/default/2302_phenotype/
	java -cp $(H2_JAR) org.h2.tools.RunScript -user sa -url jdbc:h2:$(ROOT_DIR)/configurations/exomiser-13.2.0/default/2302_phenotype/2302_phenotype  -script $<

semsim-ingest: configurations/exomiser-13.2.0/default/2302_phenotype/2302_phenotype.h2.db


.PHONY: prepare-corpora


results/exomiser-13.2.0-default/small_test-scrambled-0.5/results.yml: configurations/exomiser-13.2.0-default/config.yaml corpora/small_test/scrambled-0.5/corpus.yml
	rm -rf $(ROOT_DIR)/$(shell dirname $@)
	mkdir -p $(ROOT_DIR)/$(shell dirname $@)
	pheval run \
	 --input-dir $(ROOT_DIR)/configurations/exomiser-13.2.0-default \
	 --testdata-dir $(ROOT_DIR)/corpora/small_test/scrambled-0.5 \
	 --runner exomiserphevalrunner \
	 --tmp-dir data/tmp/ \
	 --version 13.2.0 \
	 --output-dir $(ROOT_DIR)/$(shell dirname $@)

	touch $@

.PHONY: run-exomiser-13.2.0-default-small_test-scrambled-0.5

run-exomiser-13.2.0-default-small_test-scrambled-0.5:
	$(MAKE) results/exomiser-13.2.0-default/small_test-scrambled-0.5/results.yml


pheval-run: run-exomiser-13.2.0-default-small_test-scrambled-0.5






# corpora/small_test/default/corpus.yml: $(TEST_DATA)/template_vcf/template_exome_hg19.vcf.gz


corpora/small_test/scrambled-0.5/corpus.yml: corpora/small_test/default/corpus.yml $(TEST_DATA)/template_vcf/template_exome_hg19.vcf.gz
	test -d $(ROOT_DIR)/corpora/small_test/scrambled-0.5/ || mkdir -p $(ROOT_DIR)/corpora/small_test/scrambled-0.5/
	test -L $(ROOT_DIR)/corpora/small_test/scrambled-0.5/template_exome_hg19.vcf.gz || ln -s $(ROOT_DIR)/$(TEST_DATA)/template_vcf/template_exome_hg19.vcf.gz $(ROOT_DIR)/corpora/small_test/scrambled-0.5/template_exome_hg19.vcf.gz

	pheval-utils create-spiked-vcfs \
	 --template-vcf-path $(ROOT_DIR)/corpora/small_test/scrambled-0.5/template_exome_hg19.vcf.gz  \
	 --phenopacket-dir=$(shell dirname $<)/phenopackets \
	 --output-dir $(ROOT_DIR)/$(shell dirname $@)/vcf

	test -d $(shell dirname $@)/phenopackets || mkdir -p $(shell dirname $@)/phenopackets
	pheval-utils scramble-phenopackets \
	 --scramble-factor 0.5 \
	 --output-dir $(ROOT_DIR)/$(shell dirname $@)/phenopackets \
	 --phenopacket-dir=$(shell dirname $<)/phenopackets

	touch $@

prepare-corpora: corpora/small_test/scrambled-0.5/corpus.yml


corpora/small_test/scrambled-0.7/corpus.yml: corpora/small_test/default/corpus.yml $(TEST_DATA)/template_vcf/template_exome_hg19.vcf.gz
	test -d $(ROOT_DIR)/corpora/small_test/scrambled-0.7/ || mkdir -p $(ROOT_DIR)/corpora/small_test/scrambled-0.7/
	test -L $(ROOT_DIR)/corpora/small_test/scrambled-0.7/template_exome_hg19.vcf.gz || ln -s $(ROOT_DIR)/$(TEST_DATA)/template_vcf/template_exome_hg19.vcf.gz $(ROOT_DIR)/corpora/small_test/scrambled-0.7/template_exome_hg19.vcf.gz

	pheval-utils create-spiked-vcfs \
	 --template-vcf-path $(ROOT_DIR)/corpora/small_test/scrambled-0.7/template_exome_hg19.vcf.gz  \
	 --phenopacket-dir=$(shell dirname $<)/phenopackets \
	 --output-dir $(ROOT_DIR)/$(shell dirname $@)/vcf

	test -d $(shell dirname $@)/phenopackets || mkdir -p $(shell dirname $@)/phenopackets
	pheval-utils scramble-phenopackets \
	 --scramble-factor 0.7 \
	 --output-dir $(ROOT_DIR)/$(shell dirname $@)/phenopackets \
	 --phenopacket-dir=$(shell dirname $<)/phenopackets

	touch $@

prepare-corpora: corpora/small_test/scrambled-0.7/corpus.yml




corpora/small_test/no_phenotype/corpus.yml: $(TEST_DATA)/template_vcf/template_exome_hg19.vcf.gz
	echo "error $@ needs to be configured manually" && false




.PHONY: pheval
pheval:
	$(MAKE) prepare-inputs
	$(MAKE) prepare-corpora
	$(MAKE) pheval-run

include ./resources/custom.Makefile