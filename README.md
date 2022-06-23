## **VCF to FHIR Converter**

### Introduction

VCF-formatted files are the lingua franca of next-generation sequencing, whereas [HL7 FHIR](https://www.hl7.org/fhir/) is emerging as a standard language for electronic health record interoperability. A growing number of clinical genomics applications are emerging, based on the [HL7 FHIR Genomics standard](http://hl7.org/fhir/uv/genomics-reporting/index.html). Here, we provide an open source utility for converting variants from VCF format into HL7 FHIR Genomics format. Details of the translation logic are on the [manual page](docs/Manual.md). Additional information and case studies are described in our [BMC Bioinformatics article](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-021-04039-1). Conceptually, the utility takes a VCF as input and outputs a [FHIR Genomics report](http://hl7.org/fhir/uv/genomics-reporting/index.html). 

### Install
Install and add [Ubuntu WSL](https://www.microsoft.com/en-in/p/ubuntu-1804-lts/9n9tngvndl3q?rtc=1&activetab=pivot:overviewtab) to the [windows terminal](https://www.microsoft.com/en-in/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab). (Only for windows users!)

Before installing vcf2fhir you need to install cython and wheel.
```
pip install cython wheel
```
Now, install vcf2fhir binary from pip.
```
pip install vcf2fhir
```

### Quick Examples
(some sample VCF files are [here](https://github.com/elimuinformatics/vcf2fhir/tree/master/vcf2fhir/test))

```python
>>> import vcf2fhir
>>> vcf_fhir_converter = vcf2fhir.Converter('sample.vcf', 'GRCh37')
>>> vcf_fhir_converter.convert()
```

### Logging

You can use python standard [logging](https://docs.python.org/3/library/logging.html) to enable logs. Two loggers ('vcf2fhir.general') and ('vcf2fhir.invalidrecord') are available to configure.
* **vcf2fhir.general**: standard library logs. 
* **vcf2fhir.invalidrecord**: logs all the records from vcf file which are in conversion region but are not converted to fhir format.

```python
>>> import logging
# create logger
>>> logger = logging.getLogger('vcf2fhir.invalidrecord')
>>> logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
>>> ch = logging.FileHandler('invalidrecord.log')
>>> ch.setLevel(logging.DEBUG)
# create formatter
>>> formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
>>> ch.setFormatter(formatter)
# add ch to logger
>>> logger.addHandler(ch)
```


### Documentation

You can find the detailed documantation of the package on the official website [here](https://vcf2fhir.readthedocs.io/en/latest/).

### Scope

Software converts simple (SNV, MNV, Indel) and structural (CNV, DEL, DUP, INV, INS) variants from VCF to FHIR format. Clinical annotations, where supplied, are incorporated into the FHIR representation.

* Not supported
    * **Alt contigs**: Software does not support conversion of variants aligned to Alt contigs. We recommend caution in using this software against VCFs generated with an alternate-locus aware variant caller, as variants mapped to Alt contigs will not be converted.
    * **Query liftover**: Software assumes that regions (e.g. conversion region, studied region) and VCF are based on the same genomic build.
    * **Chromosome synonyms (e.g. '1' vs. 'chr1')**: Software assumes that chromosome representation is consistent between regions (e.g. in BED files) and VCF. For instance, if VCF uses 'chr1', then BED file must also use 'chr1' 


### License and Limitations

Software is available for use under an [Apache 2.0 license](https://opensource.org/licenses/Apache-2.0), and is intended solely for experimental use, to help further Genomics-EHR integration exploration. Software is expressly not ready to be used with identifiable patient data or in delivering care to patients. Code issues should be tracked here. Comments and questions can also be directed to info@elimu.io or srikarchamala@gmail.com.

