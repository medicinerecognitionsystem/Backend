from rest_framework.decorators import api_view
from django.shortcuts import render
from django.conf import settings
from datetime import datetime
import cv2, numpy as np

#####################################################################################################################

def landingPage(request):
    return render(request, 'index.html')

def aboutPage(request):
    return render(request, 'about.html')

#####################################################################################################################

from .logic.imageProcessor import *
from .logic.utilityFunctions import *
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

@api_view(['POST'])
def webHandler(request):
    with open(settings.LOG_FILE_URL, 'a') as log:
        log.write(f"\n#start[{timestamp}]\n")
        log.write('------------------------------------------------------------------------\n')
        log.write('Processing image from web...\n')
        log.write('------------------------------------------------------------------------\n')

    if 'POST' == request.method:
        photo = request.FILES.get('photo')
        fileName = photo.name
    else:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write('Request method is not POST.\n')
            log.write('Image processing aborted!\n')
        stoppedDueToError(extractedText)
        return render(None, 'error.html', {'errorCode':'400', 'errorDescription':'Request method is not POST.'})

    if not photo:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write('Photo not received.\n')
            log.write('Image processing aborted!\n')
        stoppedDueToError(extractedText)
        return render(None, 'error.html', {'errorCode':'406', 'errorDescription':'Photo not received.'})
    else:
        try:
            image = cv2.imdecode(np.frombuffer(photo.read(), np.uint8), cv2.IMREAD_COLOR)
            tempImagePath = f'MRS/temp/{fileName}'
            cv2.imwrite(tempImagePath, image)
        except Exception as e:
            with open(settings.LOG_FILE_URL, 'a') as log:
                log.write(f'Invalid format.\n')
            stoppedDueToError(extractedText)
            return render(None, 'error.html', {'errorCode':'415', 'errorDescription':'Invalid format.'})
        
    imgDigest = generateHash(tempImagePath)
    extractedText = processImage(request, image, fileName, imgDigest)

    if 'ERROR_500' == extractedText:
        stoppedDueToError(extractedText)
        return render(None, 'error.html', {'errorCode':'500', 'errorDescription':'Internal server error.'})
    elif '' == extractedText:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write('Cannot extract text from the given image\n')
            stoppedDueToError()
        return render(None, 'error.html', {'errorCode':'422', 'errorDescription':'No medicines detected.'})
    else:
        drugsList = identifyDrugs(extractedText)

    try:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write('\n------------------------------------------------------------------------\n')
            log.write('Generating HTTP Response...\n')

        allMedicinesInfo = generateDictionaryOfDrugs(drugsList)
        numberOfMedicines = len(allMedicinesInfo)
        dictionaryForRender = {
        'generic_name': '',
        'purpose': '',
        'do_not_use': '',
        'photo': ''
        }

        for count in range(numberOfMedicines):
            medicine = allMedicinesInfo[count]
            dictionaryForRender['purpose'] += f"<li>{medicine['purpose'].capitalize()}.</li>"
            dictionaryForRender['do_not_use'] += f"<li>{medicine['do_not_use'].capitalize()}.</li>"

            if count < (numberOfMedicines-1):
                dictionaryForRender['generic_name'] += f"{medicine['generic_name'].title()}, "
            else:
                dictionaryForRender['generic_name'] += f"{medicine['generic_name'].title()}"
            
            dictionaryForRender['photo'] = Photo.objects.get(hashDigest=imgDigest).image

        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write('Sending HTTP Response...\n')
            endLogging(timestamp)
        
        return render(None, 'medicine.html', dictionaryForRender)

    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'\nAn exception occurred in webHandler(request) function.\n{e}\n')

#####################################################################################################################

def stoppedDueToError(errorMessage):
    with open(settings.LOG_FILE_URL, 'a') as log:
        log.write(f'\nImage processing is aborted due to {errorMessage}!\n')
        endLogging(timestamp)

def endLogging(timestamp):
    with open(settings.LOG_FILE_URL, 'a') as log:
        log.write('------------------------------------------------------------------------\n')
        log.write(f"#end[{timestamp}]\n\n")

#####################################################################################################################