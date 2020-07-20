import vcf
import pyranges
from .jsonGenerator import _getFhirJSON
import logging
general_logger = logging.getLogger('vcf2fhir.general')

class Converter(object):
    """Converter for a VCF v >4.1 file."""
    def __init__(self, vcf_filename=None, ref_build=None, patient_id = None, conv_region_filename=None, conv_region_dict = None, region_studied_filename= None, nocall_filename = None):
        """ 
        Create a new Converter Object to convert a VCF file.

        Parameters
        ----------
        vcf_filename : str
            Path to vcf file
        ref_build : str
            Genomic reference build number, expected values are ("GRCh37" or "GRCh38")
        patient_id : (str, Default sample name)
            A string representing patiend id.
        conv_region_filename : str
            Path to conversion region bed file.
        conv_region_dict: dict
            Conversion region can also be provided using dict.
            Format:  {"Chromosome": ["chr1", "chr2"], "Start": [100, 200], "End": [150, 201]}
        region_studied_filename : str
            Path to region studied bed file
        nocall_filename : str
            Path to non callable region bed file

        Returns
        -------
        Object
        An Instance of Conveter that helps to convert vcf file.
        """
        super(Converter, self).__init__()
        if not (vcf_filename):
            raise Exception('You must provide vcf_filename')
        if not ref_build or ref_build not in ["GRCh37", "GRCh38"]:
            raise Exception('You must provide build number ("GRCh37" or "GRCh38")')
        if (nocall_filename or region_studied_filename) and not (conv_region_filename or conv_region_dict):
            raise Exception ("Please provdie the conv_region_filename or conv_region_dict")
        self.vcf_filename = vcf_filename
        self._vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
        if not patient_id:
            patient_id = self._vcf_reader.samples[0]
        if nocall_filename:
            self.nocall_region = pyranges.read_bed(nocall_filename)
        else:
            self.nocall_region = pyranges.PyRanges()
        if conv_region_filename:
            self.conversion_region = pyranges.read_bed(conv_region_filename)
        elif conv_region_dict:
            self._fix_conv_region(conv_region_dict)
            self.conversion_region = pyranges.from_dict(conv_region_dict)
        else:
            self.conversion_region = None         
        if region_studied_filename:
            self.region_studied = pyranges.read_bed(region_studied_filename)
        else:
            self.region_studied = pyranges.PyRanges()
        self.patient_id = patient_id
        self.ref_build = ref_build
        self.nocall_filename = nocall_filename
        self.conv_region_filename = conv_region_filename
        general_logger.info("Converter class instantiated successfully")
    def convert(self, output_filename='fhir.json'):
        try:
            general_logger.info("Starting VCF to FHIR Conversion")
            _getFhirJSON(self._vcf_reader, self.ref_build, self.patient_id, output_filename, self.conversion_region, self.region_studied, self.nocall_region)
        except Exception as e:
            general_logger.error("Exception occurred", exc_info=True)
            return False
        return True

    def _fix_conv_region(self, conv_region_dict):
        i = 0
        for start in conv_region_dict["Start"]:
            conv_region_dict["Start"][i] = start - 1
            i += 1
        i = 0
        for end in conv_region_dict["End"]:
            conv_region_dict["End"][i] = end - 1
            i += 1

