from ..models import *
from django.conf import settings

#####################################################################################################################

def generateHash(imagePath):
    try:
        with open(imagePath, 'rb') as f:
            imageData = f.read()

        import hashlib
        hashObject = hashlib.md5()
        hashObject.update(imageData)
        hashResult = hashObject.hexdigest()

        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f"generateHash(imagePath) returned: {hashResult}\n") 
        return hashResult

    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in generateHash(imagePath) function.\n{e}\n')

#####################################################################################################################

def clean(ocrResult_2DList):
    minConfidence = 25.00
    goodTexts = []
    try:
        for i in range(len(ocrResult_2DList)):
            confidence = format(ocrResult_2DList[i][2]*100, '.2f')
            if (len(ocrResult_2DList[i][1]) > 3) and (float(confidence) > minConfidence):
                goodTexts.append(ocrResult_2DList[i][1].lower())

        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f"clean(ocrResult_2DList) returned: {goodTexts}\n") 
        return goodTexts

    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in clean(ocrResult) function.\n{e}\n')

#####################################################################################################################

def identifyDrugs(text_List):
    names = []
    try:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write('\n------------------------------------------------------------------------\n')
            log.write(f"identifying drugs...\n") 
            log.write('------------------------------------------------------------------------\n')
        for sentence in text_List: 
            fuzzyResult = lookup(sentence)
            names.append(fuzzyResult)

        drugs = [item for item in names if item != '']

        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f"\nidentifyDrugs(text_List) returned: {drugs}\n") 

        return drugs

    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in identifyDrugs(text) function.\n{e}\n')

#####################################################################################################################

def lookup(query_String):
    import os
    from django.conf import settings
    ndcPath = os.path.join(settings.BASE_DIR, 'MRS', 'logs', 'ndc_generic-names.txt')
    from thefuzz import fuzz

    bestMatch = ''
    matchRatio = 0
    try:
        with open(ndcPath, "r") as data:
            for line in data:
                similarity = fuzz.ratio(query_String, line.rstrip())
                if similarity > 85 and similarity > matchRatio:
                    matchRatio = similarity
                    bestMatch = line.rstrip()

        with open(settings.LOG_FILE_URL, 'a') as log:
            if not bestMatch:
                log.write(f"{query_String} => Not a drug\n")
            else:
                log.write(f"{query_String} => Is a drug\n")
        return bestMatch

    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in lookup(query) function.\n{e}\n')

#####################################################################################################################

def generateDictionaryOfDrugs(genericNames_List):
    drugs = {}
    initialized = 0
    try:
        for name in genericNames_List:
            medIndex = 0
            with open(settings.LOG_FILE_URL, 'a') as log:
                log.write('------------------------------------------------------------------------\n')
                log.write(f'Checking availability of {name} in database...\n')
            if Medicine.objects.filter(generic_name=name).exists():
                dbResponse = Medicine.objects.get(generic_name=name)
                drug_info = {
                    'generic_name': dbResponse.generic_name,
                    'purpose': dbResponse.purpose,
                    'do_not_use': dbResponse.do_not_use
                }
                drugs[medIndex] = drug_info
                medIndex +=1

            else:
                with open(settings.LOG_FILE_URL, 'a') as log:
                    log.write(f'{name} not found in database! Requesting OpenFDA...\n')
                drugs[medIndex] = queryFDA(name)
                medIndex +=1

        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'generateDictionaryOfDrugs(genericNames_List) returned: {drugs}\n')
        return drugs

    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in generateElementData(genericNames_List) function.\n{e}\n')

#####################################################################################################################

def queryFDA(genericName_String):
    import json, requests, os
    details = {}
    baseURL = 'https://api.fda.gov/drug/label.json?search=openfda.generic_name:'
    try:
        fdaResponse = requests.get(baseURL + '"' + genericName_String + '"')

        if fdaResponse.status_code == 200:
            fdaJSON = fdaResponse.json()
            name = genericName_String
            use = fdaJSON['results'][0]['purpose'][0].lower()
            dontUse = fdaJSON['results'][0]['do_not_use'][0].lower()

        details['generic_name'] = name
        details['purpose'] = use
        details['do_not_use'] = dontUse

        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'Creating record of {name} in database for future use...\n')
        createDBentry(details)

        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'queryFDA(genericName_String) returned: {details}\n')
        return details
        
    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in queryFDA(genericName) function.\n{e}\n')

#####################################################################################################################

def createDBentry(drug_Dictionary):
    try:
        Medicine.objects.create(
            generic_name = drug_Dictionary['generic_name'],
            purpose = drug_Dictionary['purpose'],
            do_not_use = drug_Dictionary['do_not_use']
        )
    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in createDBentry(drug_Dictionary) function.\n{e}\n')

#####################################################################################################################
