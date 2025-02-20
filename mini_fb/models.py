#mini_fb.models.py
#define data models for the blog application 
from django.db import models

# Create your models here.
class Profile(models.Model):
    '''Encapsulate the data of a facebook profile'''

    #define the data attributes of the Profile Object
    firstname = models.TextField(blank=True)
    lastname = models.TextField(blank= True)
    city = models.TextField(blank=True)
    email = models.TextField(blank=True)
    published = models.DateTimeField(auto_now= True)
    image_url = models.URLField(blank= True)
    bios =  models.TextField(blank=True)
    


    def __str__(self):

        return f'{self.firstname} {self.lastname}'