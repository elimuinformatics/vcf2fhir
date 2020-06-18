import vcf
import sys
from .jsonGenerator import _getFhirJSON
class Converter(object):
    def __init__(self, vcf_filename=None, ref_build=None, patient_id = None, sex='F', no_call_filename = None, conv_region_filename=None):
        super(Converter, self).__init__()
        if not (vcf_filename):
            raise Exception('You must provide vcf_filename')
        if not ref_build or ref_build not in ["GRCh37", "GRCh38"]:
            raise Exception('You must provide build number ("GRCh37" or "GRCh38)')
        self.vcf_filename = vcf_filename
        self._vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
        if not patient_id:
            patient_id = self._vcf_reader.samples[0]
        self.patient_id = patient_id
        self.sex = sex 
        self.ref_build = ref_build
        self.no_call_filename = no_call_filename
        self.conv_region_filename = conv_region_filename
    def convert(self, output_filename='fhir.json'):
        try:
            _getFhirJSON(self._vcf_reader, self.ref_build, self.patient_id, self.sex, output_filename, self.no_call_filename, self.conv_region_filename)
        except Exception:
            raise Exception
            return False
        return True
