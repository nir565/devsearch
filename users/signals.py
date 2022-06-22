# To make our sigals work we have to register sigals.py file 
# in our app i.e. user app 

# This method is triggered when model is saved
from email import message
from django.db.models.signals import post_save,post_delete
from django.dispatch import  receiver
from .models import Profile
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

# connecting signals with decorator
# @receiver(post_save,sender=Profile)
def createProfile(sender,instance,created,**kwargs):
    if created:
        user = instance
        profiles = Profile.objects.create(
            user = user,
            username =user.username,
            email = user.email,
            name = user.first_name,
            
        )

        subject = 'Welcome to DevSearch'
        message = 'We are glad you are here'

        send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [profiles.email],
        fail_silently=False,
        )


# If we want to edit our profile
# then to edit our user we are doing this
def updateUser(sender,instance,created,**kwargs):
    profile = instance
    user  = profile.user
    if created == False:
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email
        user.save()







# Signal
# post_saved is called when new profile is saved
# signals are used to fire certain event when 
# some action takes place and are used to perform certian 
# oter action based on that 
def deleteUser(sender,instance,**kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass

    
# signals can also be used like this
post_save.connect(createProfile,sender=User)
post_save.connect(updateUser,sender=Profile)
post_delete.connect(deleteUser,sender=Profile)




