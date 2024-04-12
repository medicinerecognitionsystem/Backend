from django.db import models

class Photo(models.Model):
    hashDigest = models.CharField(max_length=35)
    image = models.ImageField(upload_to='MRS/media')

    def __str__(self):
        return self.hashDigest

class Medicine(models.Model):
    generic_name = models.CharField(max_length=100)
    purpose = models.CharField(max_length=500)
    do_not_use = models.CharField(max_length=1500)

    def __str__(self):
        return self.generic_name
    