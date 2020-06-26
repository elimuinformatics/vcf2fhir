import vcf
import pyranges
from .jsonGenerator import _getFhirJSON
class Converter(object):
    def __init__(self, vcf_filename=None, ref_build=None, patient_id = None, conv_region_filename=None, region_studied_filename= None, nocall_filename = None):
        super(Converter, self).__init__()
        if not (vcf_filename):
            raise Exception('You must provide vcf_filename')
        if not ref_build or ref_build not in ["GRCh37", "GRCh38"]:
            raise Exception('You must provide build number ("GRCh37" or "GRCh38)')
        self.vcf_filename = vcf_filename
        self._vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
        if not patient_id:
            patient_id = self._vcf_reader.samples[0]
        if region_studied_filename is not None:
            self.region_studied = pyranges.read_bed(region_studied_filename)
        else:
            self.region_studied = None
        if nocall_filename is not None:
            self.nocall_region = pyranges.read_bed(nocall_filename)
        else:
            self.nocall_region = ""
        if conv_region_filename is not None:
            self.conversion_region = pyranges.read_bed(conv_region_filename)
        else:
            self.conversion_region = ""
        self.patient_id = patient_id
        self.ref_build = ref_build
        self.nocall_filename = nocall_filename
        self.conv_region_filename = conv_region_filename
    def convert(self, output_filename='fhir.json'):
        try:
            _getFhirJSON(self._vcf_reader, self.ref_build, self.patient_id, output_filename, self.conversion_region, self.region_studied, self.nocall_region)
        except Exception:
            raise Exception
            return False
        return True
