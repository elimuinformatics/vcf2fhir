import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vcf2fhir-openelimu",
    version="0.0.8",
    author="",
    test_suite='vcf2fhir.test.test_vcf2fhir.suite',
    author_email="info@elimu.io",
    description="Convert .vcf files to HL7 FHIR standard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openelimu/VCF-2-FHIR",
    packages=['vcf2fhir', 'vcf2fhir.test'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ],
    install_requires=[
        'fhirclient==3.2.0',
        'pandas==0.24.2',
        'pytz==2019.3',
        'pyVCF==0.6.8',
        'pysam==0.16.0',
        'pyranges==0.0.79'
    ],
    python_requires='>=3.6',
)