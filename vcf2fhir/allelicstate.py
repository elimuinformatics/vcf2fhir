import pandas as pd


def getAllelicState(f, gender):
    allelicState = ''
    allelicCode = ''
    # Using  the first sample
    sampleVal = f.samples[0].data.GT
    allele = sampleVal.split('/')
    allelePipe = sampleVal.split('|')
    if len(allelePipe) == 2:
        x = allelePipe[0]
        y = allelePipe[1]
    if len(allele) == 2:
        x = allele[0]
        y = allele[1]
    else:
        if gender == 'M' and f.CHROM == 'MT':
            allelicState = 'Homoplasmic'
            allelicCode = 'LA6704-6'

    if gender == 'F':
        if f.CHROM != 'Y' and f.CHROM != 'MT':
            if x != y:
                allelicState = 'heterozygous'
                allelicCode = 'LA6706-1'
            else:
                allelicState = 'homozygous'
                allelicCode = 'LA6705-3'
    elif gender == 'M':
        if f.CHROM == 'Y' or f.CHROM == 'X':
            allelicState = 'hemizygous'
            allelicCode = 'LA6707-9'
        elif f.CHROM == 'MT':
            if x != y:
                allelicState = 'heteroplasmic'
                allelicCode = 'LA6703-8'

            # elif formatVal['GT'] in ["0","1"]:
                #allelicState = 'Homoplasmic'
                #allelicCode = 'LA6704-6'
            else:
                allelicState = 'homoplasmic'
                allelicCode = 'LA6704-6'
        else:
            if x != y:
                allelicState = 'heterozygous'
                allelicCode = 'LA6706-1'
            else:
                allelicState = 'homozygous'
                allelicCode = 'LA6705-3'    
    return {'ALLELE': allelicState, 'CODE' : allelicCode}

