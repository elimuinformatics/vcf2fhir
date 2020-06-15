import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vcf2fhir-openelimu",
    version="0.0.3",
    author="",
    test_suite='vcf2fhir.test.test.suite',
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
        'certifi==2020.4.5.1',
        'chardet==3.0.4',
        'click==7.1.1',
        'fhirclient==3.2.0',
        'gunicorn==20.0.4',
        'idna==2.9',
        'isodate==0.6.0',
        'itsdangerous==1.1.0',
        'Jinja2==2.11.1',
        'MarkupSafe==1.1.1',
        'numpy==1.18.2',
        'pandas==0.24.2',
        'python-dateutil==2.8.1',
        'pytz==2019.3',
        'requests==2.23.0',
        'six==1.14.0',
        'urllib3==1.25.8',
        'Werkzeug==1.0.1',
        'xmljson==0.2.0',
        'xmltodict==0.12.0',
        'pyVCF'
    ],
    python_requires='>=3.6',
)