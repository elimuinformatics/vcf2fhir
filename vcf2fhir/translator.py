import vcf
import sys
from .jsonGenerator import _getFhirJSON
class Converter(object):
    def __init__(self, vcf_filename, ref_build, patient_id = None, sex='F', conv_region_filename=None):
        if not (vcf_filename):
            raise Exception('You must provide vcf_filename')
        if not ref_build:
            raise Exception('You must provide build number')
        self.vcf_filename = vcf_filename
        try:
            self._vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
        except Exception:
            raise Exception
        if not patient_id:
            patient_id = self._vcf_reader.samples[0]
        self.patient_id = patient_id
        self.sex = sex 
        self.ref_build = ref_build
    def convert(self, format='json', output_filename='fhir.json'):
        try:
            _getFhirJSON(self._vcf_reader,self.patient_id, self.ref_build,  noCall=False, gender=self.sex, output_filename=output_filename)
        except Exception:
            raise Exception
            return False
        return True
