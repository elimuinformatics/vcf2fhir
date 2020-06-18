import os
import datetime
import pandas as pd
import random, string
import pytz

class _Utilities(object):

    """
    /**
     * generates current date into fhir format 
     * @return date
     */
    """
    def getFhirDate(): 
        z = datetime.datetime.now(pytz.timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S%z")
        return z[:-2]+':'+z[-2:]
        