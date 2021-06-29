# v0.0.1 - v0.0.16

Converts VCF variants into a [FHIR Genomics Diagnostic Report](http://hl7.org/fhir/uv/genomics-reporting/index.html). 

## Added
* In scope are simple variants (SNVs, Indels), along with zygosity and phase relationships, for autosomes, sex chromosomes, and mitochondrial DNA.
* Supports VCF file (text-based or bgzipped) and optionally tabix files for query.
* Supports genome build ('GRCh37' or 'GRCh38');
* Optionally supports a query region in the form of .bed or dictionary that indicates the region(s) to convert.
* Optionally supports inclusion of  'region-studied' observations that detail which portions of the conversion region were studied, and of those studied regions, which portions were deemed uncallable.
