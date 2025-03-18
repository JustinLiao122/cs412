# File: mini_fb.models.py
# Author: Justin Liao (liaoju@bu.edu), 3/4/2025
# Description: define data models for the blog application 

from django.db import models
from django.urls import reverse

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





    def get_status_messages(self):
        # gets all status messages for this spesific profile and orderes them by most recent first with the timestamp attribute

        status_message = StatusMessage.objects.filter(profile=self).order_by('-timestamp')
        return status_message
    
    def get_friends(self):

        friends = Friend.objects.filter(profile2 = self) | Friend.objects.filter(profile1 = self)

        friend_profiles = []
        for friend in friends:
            if friend.profile1 == self:
                friend_profiles.append(friend.profile2)
            else:
                friend_profiles.append(friend.profile1)

        return friend_profiles
    
    def add_friend(self, other):

        if self != other: 
            friends = self.get_friends()
            if other not in friends:
                Friend.objects.create(profile1=self, profile2=other)


    def get_friend_suggestions(self):
        
        my_friends = self.get_friends()
        ##print("My_friends:" , my_friends)
        friends_of_friends = []

        for friend in my_friends:
            temp_friends = friend.get_friends()
            for f in temp_friends:
                ##print("A friend of my friend:" , f)
                
                if f != self and f not in my_friends and f not in friends_of_friends:
                    friends_of_friends.append(f)
         

        return friends_of_friends

    def __str__(self):

        return f'{self.firstname} {self.lastname}'
    
    def get_absolute_url(self):
        '''Return the URL to display one instance of this model.'''
        return reverse('show_profile', kwargs={'pk':self.pk})
    


class StatusMessage(models.Model):
    '''Encapsulate the data of a statusmessage'''


    #define the data attributes of the StatusMessage Object

    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank= True)
    profile =models.ForeignKey("Profile", on_delete=models.CASCADE)



    def get_images(self):
        #gets the StatusImage objects that are related/forgienkeys with this StatusMessage 
        #then gets the Image obejct associated with that StatusImage object with the foreign key that is stored in the object as an attribute
       
        status_images = StatusImage.objects.filter(statusMessage = self)
        return [status_image.image for status_image in status_images]
    

    def __str__(self):

        return f'{self.message}'




class Image(models.Model):
    '''Encapsulate the data of a Image'''



    #define the data attributes of the Image Object
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    imageField = models.ImageField(blank=True)
    timeStamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank= True)


    def __str__(self):

        return f'{self.imageField}'


class StatusImage(models.Model):
    '''Encapsulate the data of a StatusImage'''

    #define the data attributes of the StatusImage Object
    image = models.ForeignKey("Image", on_delete=models.CASCADE)
    statusMessage = models.ForeignKey("StatusMessage", on_delete=models.CASCADE)


    def __str__(self):

        return  f'{self.image} {self.statusMessage}'
    




class Friend(models.Model):
    '''encapsulates the idea of an edge connecting two nodes within the social network'''

    profile1 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="profile1")
    profile2 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="profile2")
    anniversary = models.DateTimeField(auto_now_add=True)





    def __str__(self):
        return f'{self.profile1} is friends with {self.profile2} starting this day: {self.anniversary}'