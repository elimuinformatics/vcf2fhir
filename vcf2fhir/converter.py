import vcf
import pyranges
from .json_generator import _get_fhir_json
import logging
import sys
general_logger = logging.getLogger('vcf2fhir.general')

class Converter(object):
    """Converter for a VCF v >4.1 file."""
    def __init__(self, vcf_filename=None, ref_build=None, patient_id = None, has_tabix=False, conv_region_filename=None, conv_region_dict = None, region_studied_filename= None, nocall_filename = None):
        """ 
        Create a new Converter Object to convert a VCF file.

        Parameters
        ----------
        vcf_filename : str (Required)
            Path to text-based or bgzipped VCF file containing variants to be converted into FHIR format.
            Valid path and filename without whitespace. VCF file must conform to VCF Version 4.1 or later. 
            FORMAT.GT must be present. Multi-sample VCFs are allowed, but only the first sample will be converted.
        ref_build : str (Required)
            Genome Reference Consortium genome assembly to which variants in the VCF were called. Must be one of 'GRCh37' or 'GRCh38'.
        patient_id : str (Optional)
            Patient who's VCF file is being processed. Alphanumeric string without whitespace. Default value is first sample name.
        has_tabix : bool (Optional)
            If tabix file exist for the vcf than set it to True. Tabix file should have the same name as vcf file, with a '.tbi' extension,
            and must be in the same folder. Default value is False.
        conv_region_filename : str (Optional)
            Path to conversion region bed file. Subset of the VCF file to be converted into FHIR. If absent, the entire VCF file is converted. Must be a valid BED file
        conv_region_dict: dict (Optional)
            Conversion region can also be provided using dict. If 'conv_region_filename' is provided
            it will be ignored. 
            Format:  {"Chromosome": ["chr1", "chr2"], "Start": [100, 200], "End": [150, 201]}
        region_studied_filename : str (Optional)
            Path to region studied bed file. Subset of patient's genome that was studied in the generation of the VCF file. If present, only studied regions are converted. Must be a valid BED file, with first 3 columns: <chr> <start> <stop>.
        nocall_filename : str (Optional)
            Path to no call bed file. Subset of studied region that is deemed noncallable. If present, only studied regions minus noncallable regions are converted. Must be a valid BED file, with first 3 columns: <chr> <start> <stop>.

        Returns
        -------
        Object
        An Instance of Conveter that helps to convert vcf file.

        Examples
        --------

        """
        super(Converter, self).__init__()
        if not (vcf_filename):
            raise Exception('You must provide vcf_filename')
        if not ref_build or ref_build not in ["GRCh37", "GRCh38"]:
            raise Exception('You must provide build number ("GRCh37" or "GRCh38")')
        if nocall_filename and not region_studied_filename:
            raise Exception ("Please also provide region_studied_filename when nocall_filename is provided")
        self.vcf_filename = vcf_filename
        try:
            self._vcf_reader = vcf.Reader(filename=vcf_filename)
        except FileNotFoundError:
            raise
        except :
            self._generate_exception("Please provide valid  'vcf_filename'")
        if not patient_id:
            patient_id = self._vcf_reader.samples[0]
        if nocall_filename:
            try:
                self.nocall_region = pyranges.read_bed(nocall_filename)
            except FileNotFoundError:
                raise
            except:
                self._generate_exception("Please provide valid  'nocall_filename'")
        else:
            self.nocall_region = pyranges.PyRanges()
        if conv_region_filename:
            try:
                self.conversion_region = pyranges.read_bed(conv_region_filename)
            except FileNotFoundError:
                raise
            except:
                self._generate_exception( "Please provide valid 'conv_region_filename'")
        elif conv_region_dict:      
            try:
                self._fix_conv_region_zero_based(conv_region_dict)
                self.conversion_region = pyranges.from_dict(conv_region_dict)
            except FileNotFoundError:
                raise
            except:
                self._generate_exception("Please provide valid 'conv_region_dict'")
        else:
            self.conversion_region = None         
        if region_studied_filename:
            try:
                self.region_studied = pyranges.read_bed(region_studied_filename)
            except FileNotFoundError:
                raise
            except:
                self._generate_exception("Please provide valid 'region_studied_filename'")
        else:
            self.region_studied = None
        self.has_tabix = has_tabix
        self.patient_id = patient_id
        self.ref_build = ref_build
        self.nocall_filename = nocall_filename
        self.conv_region_filename = conv_region_filename
        general_logger.info("Converter class instantiated successfully")
    def convert(self, output_filename='fhir.json'):
        """ Returns True on success

        Parameters
        ----------
        output_filename : str, default fhir.json
            Path to output fhir json.

        Returns
        ----------
        bool True on successful conversion

        """
        try:
            general_logger.info("Starting VCF to FHIR Conversion")
            _get_fhir_json(self._vcf_reader, self.ref_build, self.patient_id, self.has_tabix, self.conversion_region, self.region_studied, self.nocall_region, output_filename)
        except:
            general_logger.error("Error in converting vcf file", exc_info=True)
            return False
        return True

    def _fix_conv_region_zero_based(self, conv_region_dict):
        i = 0
        for start in conv_region_dict["Start"]:
            conv_region_dict["Start"][i] = start - 1
            i += 1
        i = 0
        for end in conv_region_dict["End"]:
            conv_region_dict["End"][i] = end - 1
            i += 1

    def _generate_exception(self, msg):
        general_logger.error(msg, exc_info=True)
        raise Exception (msg, sys.exc_info)

