# v0.1.0 (2021-09-22)

This is our first minor version release with support for structural variant conversion and incorporation of clinical annotations. For more details follow [Readme](README.md). We would love to hear your feedback! If you find any issue please open an [Issue](https://github.com/elimuinformatics/vcf2fhir/issues/new/choose).

## Added
* Support for Structural Variants ([#86](https://github.com/elimuinformatics/vcf2fhir/pull/86)).
* Support for Clinical Annotations ([#89](https://github.com/elimuinformatics/vcf2fhir/pull/89)).

# v0.0.17 (2021-06-30)

## Added
* Exposed a new parameter to configure ratio for determining Homoplasmic vs Heteroplasmic ([#19](https://github.com/elimuinformatics/vcf2fhir/issues/19)).

## Changed
* Build process to PEP 517 ([#18](https://github.com/elimuinformatics/vcf2fhir/issues/18)).

## Fixed
* Excluded records with incorrect CHROM values in vcf file ([#19](https://github.com/elimuinformatics/vcf2fhir/issues/19)).
* Removed 'Human reference sequence assembly version' component from variant observation ([#36](https://github.com/elimuinformatics/vcf2fhir/issues/36)).
* Case where conversion region is not studied ([#66](https://github.com/elimuinformatics/vcf2fhir/issues/66)).
* FHIR validation errors and warnings ([#77](https://github.com/elimuinformatics/vcf2fhir/pull/77)).

# v0.0.1 - v0.0.16

Converts VCF variants into a [FHIR Genomics Diagnostic Report](http://hl7.org/fhir/uv/genomics-reporting/index.html). 

## Added
* In scope are simple variants (SNVs, Indels), along with zygosity and phase relationships, for autosomes, sex chromosomes, and mitochondrial DNA.
* Supports VCF file (text-based or bgzipped) and optionally tabix files for query.
* Supports genome build ('GRCh37' or 'GRCh38');
* Optionally supports a query region in the form of .bed or dictionary that indicates the region(s) to convert.
* Optionally supports inclusion of  'region-studied' observations that detail which portions of the conversion region were studied, and of those studied regions, which portions were deemed uncallable.
