from email import message
from django.shortcuts import render,redirect
from django.contrib.auth import login ,authenticate,logout
from .models import Profile,User,Message
from django.contrib import messages
# for registering user
# from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm,ProfileForm,SkillForm,MessageForm
from django.contrib.auth.decorators import  login_required
from django.db.models import Q
from .utils import paginateProfiles, searchProfiles 

def logoutUser(request):
    # logout method wil delete the session_id
    logout(request)
    messages.info(request, 'Logged-out successfull')
    return redirect('login')




def loginUser(request):
    page = 'login'

    # if user is already logged inn this line will
    # prevent him from going to login page maually
    if request.user.is_authenticated:
        return redirect('profiles')
    # if method is post we are extracting username ,password
    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']
        try:
            # we are checking if the user already exists
            user  = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')
        # if it finds user with this name and password 
        # it returns back the user
        user = authenticate(request,username=username,password=password)

        if user is not None:
            # login will create session for user in db table
            # will also give that session to browsers cookies
            login(request,user)
            return redirect('profiles')
        else:
            messages.error(request, 'Username or Password is incorrect')
    return render(request,'users/login_register.html')



def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # commit gives us instance of user after
            # saving it so that we can still make some changes
            user = form.save(commit=False)
            # We wanted the username to be lower case in any condtiton 
            user.username = user.username.lower()
            user.save()
            messages.success(request,'User account was created!')
            
            login(request,user)
            return redirect('edit-account')
        else:
            messages.success(request,'Error has occured during registration')
    context={'page':page,'form':form}
    return render(request,'users/login_register.html',context)
    




def profiles(request):
    profiles,search_query =  searchProfiles(request)
    custom_range,profiles = paginateProfiles(request,profiles,3)
    context={
        'profiles':profiles,
        'search_query':search_query,
        'custom_range':custom_range
    }
    return render(request,'users/profiles.html',context)


def userProfile(request,pk):
    profiles = Profile.objects.get(id=pk)
    topSkills = profiles.skill_set.exclude(description__exact="")
    otherSkills = profiles.skill_set.filter(description="") 

    context={
        'profile':profiles,'topSkills':topSkills,'otherSkills':otherSkills
    }
    return render(request,'users/user-profile.html',context)

# For user account detail
@login_required(login_url='login')
def userAccount(request):
    # getting profile of logged in user
    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.project_set.all()
    context={'profile':profile,'skills':skills,'projects':projects}
    return render(request,'users/account.html',context)



@login_required(login_url='login')
def editAccount(request):
    profile  = request.user.profile
    # to show the form with previous data
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context={'form':form}
    return render(request,'users/profile_form.html',context)



@login_required(login_url='login')
def createSkill(request):
    profile  = request.user.profile
    form = SkillForm()
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request,'skill was added successfully!!!!')
            return redirect('account')
    
    context={'form':form}
    return render(request,'users/skill_form.html',context)





@login_required(login_url='login')
def updateSkill(request,pk):
    profile  = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    if request.method == 'POST':
        form = SkillForm(request.POST,instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request,'skill was updated !!!!')
            return redirect('account')
    
    context={'form':form}
    return render(request,'users/skill_form.html',context)



@login_required(login_url='login')
def deleteSkill(request,pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request,'Skill deleted')
        return redirect('account')
    context={'object':skill}
    return render(request,'delete_obj.html',context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context={'messageRequests':messageRequests,'unreadCount':unreadCount}
    return render(request,'users/inbox.html',context)


@login_required(login_url='login')
def viewMessage(request,pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context={'message':message}
    return render(request,'users/message.html',context)



def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request, 'Your message was successfully sent!')
            return redirect('user-profile', pk=recipient.id)

    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context)
