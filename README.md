## **VCF to FHIR Converter**

### Introduction

VCF-formatted files are the lingua franca of next-generation sequencing, whereas [HL7 FHIR](https://www.hl7.org/fhir/) is emerging as a standard language for electronic health record interoperability. A growing number of clinical genomics applications are emerging, based on the [HL7 FHIR Genomics standard](http://hl7.org/fhir/uv/genomics-reporting/index.html). Here, we provide an open source utility for converting variants from VCF format into HL7 FHIR Genomics format. A web-based conversion tool leveraging this utility is [HERE](https://vcf-2-fhir.herokuapp.com/). Details of the translation logic are on the wiki. Sample VCF files and corresponding FHIR Genomics instances are in the downloads folder. 

Conceptually, the utility takes a VCF as input and outputs a FHIR Genomics report. We currently convert simple variants (SNVs, Indels), along with zygosity and phase relationships, for autosomes, sex chromosomes, and mitochondrial DNA, as illustrated here: 

![image](https://user-images.githubusercontent.com/46577791/80811245-5665bb00-8b7a-11ea-9b4e-4dc5c10cdce9.png)

### License and Limitations

Software is available for use under an [Apache 2.0 license](https://opensource.org/licenses/Apache-2.0), and is intended solely for experimental use, to help further Genomics-EHR integration exploration. Software is expressly not ready to be used with identifiable patient data or in delivering care to patients. Code issues should be tracked here. Comments and questions can also be directed to info@elimu.io.

### VCF Requirements

- File must conform to VCF Version 4.1 or later.
- Genotype (FORMAT.GT) must be present
- Multi-sample VCFs are allowed, but only the first sample will be converted.
- Filename must be formatted to include certain ordered, dot-delimited parameters.
  - PatientID (required, first): any string without whitespace
  - Build (required, second): one of 'b37' (aka GRCh37, hg19), or ‘b38’ (aka GRCh38, hg38)
  - Gene (required, third): a valid [HGNC gene symbol](https://www.genenames.org/).
  - Sex (optional, fourth): 'M' or 'F' (used in the conversion of chrX and chrY variants)
  - Extra stuff (optional): Anything else, such as local filename, without whitespace
  - Valid filename examples
    - NA120003.b37.CYP2D6.vcf
    - Patient0123.b38.TPMT.M.File012345.vcf
    - Patient0123.b38.TPMT.File012345.vcf
- Submitted VCF files should contain just that slice intended to be converted. While the VCF file may contain variants from multiple chromosomes, or from regions that extend beyond the stated Gene's boundaries, only variants on the same chromosome as the Gene will be converted. 

### Conversion logic

The conversion creates a FHIR Genomics DiagnosticReport that contains a single 'region studied' observation, zero to many 'variant' observations, and zero to many 'sequence phase relationship' observations. The 'region studied' observation includes the NCBI chromosome-level ('NC_') refSeq for the chromosome whose variants were converted. There is one 'variant' observation for each converted VCF row. There is one 'sequence phase relationship' for each pair-wise phase relationship asserted in the VCF file.

The following VCF rows are excluded from conversion: 
- VCF #CHROM is not the one on which the Gene in the filename resides.
- VCF REF is not a simple character string
- VCF ALT is not a simple character string, comma-separated character string, or '.'.. (Rows where ALT is a token (e.g. 'DEL') are excluded).
- VCF FILTER does not equal 'PASS' or '.'.
- VCF INFO.SVTYPE is present. (Structural variants are excluded).
- VCF FORMAT.GT is null ('./.', '.|.', '.', etc).

Variant observations:
- Are reflections of the VCF. No normalization (i.e. conversion into a canonical form) or liftover (i.e. conversion from one build to another) is performed. 
- Use a 1-based coordinate system, so that the variant position in the FHIR Genomics report is the same as VCF POS. 
- Male sex is assumed if not provided (e.g. for determining allelic state of chrX variants)

## Steps to run the converter on you local machine

Install the package
```
python -m pip install --ignore-installed --extra-index-url https://test.pypi.org/simple/ vcf2fhir-openelimu==0.0.3
```

Import the dependency in a script and use as below.
```
import vcf2fhir
oVcf2Fhir = vcf2fhir.Converter('HG00628.b37.UROD.M.vcf', 'HG00628', 'b37', 'M')
oVcf2Fhir.convert(format='json', output_filename='fhir1.json')
```
Note: At this moment you also need to copy the downloads folder from the repository in the same folder as ur script because of dependency on nocall.csv

## Run the tests

```
python setup.py test
```