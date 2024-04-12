from ..models import *
from .utilityFunctions import *
from django.conf import settings

#####################################################################################################################

def processImage(request, image, fileName, MD5hash):
        import os, cv2, numpy as np
        try:
            if not Photo.objects.filter(hashDigest=MD5hash).exists():
                newPhoto = Photo.objects.create(hashDigest=MD5hash, image=f'MRS/media/{fileName}')
                newPhoto.save()
            if not os.path.exists(f'MRS/media/{fileName}'):
                cv2.imwrite(f'MRS/media/{fileName}', image)
            if not os.path.exists(f'MRS/cache/{MD5hash}.ocr'):
                performOCR(image, MD5hash)
            
            with open(f'MRS/cache/{MD5hash}.ocr', 'r') as cache:
                ocrResult = eval(cache.read().strip())
            
            return clean(ocrResult)
            
        except Exception as e:
            with open(settings.LOG_FILE_URL, 'a') as log:
                log.write(f'An exception occurred in imageProcessor(request, image, fileName, MD5hash) function.\n{e}\n')
                log.write('Image processing aborted!\n')
            return 'ERROR_500'

#####################################################################################################################

def performOCR(image, hashDigest):
    import easyocr
    try:
            reader = easyocr.Reader(['en'])
            result = reader.readtext(image)

            with open(f'MRS/cache/{hashDigest}.ocr', 'w') as cache:
                cache.write(str(result))

            with open(settings.LOG_FILE_URL, 'a') as log:
                log.write(f"performOCR(image, hashDigest) created {hashDigest}.ocr file...\n") 
                
    except Exception as e:
        with open(settings.LOG_FILE_URL, 'a') as log:
            log.write(f'An exception occurred in performOCR(image) function.\n{e}\n')

#####################################################################################################################
