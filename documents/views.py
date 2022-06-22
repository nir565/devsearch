from multiprocessing import context
from django.shortcuts import render, redirect
from django.http import HttpResponse
from . models import Project,Tag
from .forms import ProjectForm,ReviewForm
from django.contrib import messages
# this decorator sits above any view we want to block
# and will ask for authentication
from django.contrib.auth.decorators import login_required
from .utils import searchProject , paginateProjects


def documents(request):
    projects,search_query = searchProject(request)
    custom_range,projects = paginateProjects(request,projects,2)
    context = {'projects':projects,'search_query':search_query,'custom_range':custom_range}
    return render(request,'documents/doc.html',context)

    


def document(request, pk):
    projObj = Project.objects.get(id=pk)
    form  = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = projObj
        review.owner = request.user.profile
        review.save()
        # Update project vote
        projObj.getVoteCount
        messages.success(request,'Your review is added')
        return redirect('document',projObj.id)
    context = {
        'proObj': projObj,
        'form':form
    }
    return render(request, 'documents/single-doc.html', context)
# if user is ot logged
# he will be directed to the parameter given inbracket
@login_required(login_url="login")
def createProject(request):
    profile = request.user.profile
    # to use the modelform
    form = ProjectForm()
    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(','," ").split()
        # taking posted data
        # request.files is used so that images can be uploaded
        form = ProjectForm(request.POST,request.FILES)
        # checking if valid
        if form.is_valid():
            # if saved new obj created in admin
            # gives isntance of current project
            # then we can go in that project and update the owner
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            for tag in newtags:
                tag,created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('documents')

    context = {'form': form}
    return render(request, 'documents/doc_form.html', context)

@login_required(login_url="login")
def  updateProject(request,pk):
    # to protect any user from getting project from project id
    # we get all project of curretn user
    profile  = request.user.profile
    project = profile.project_set.get(id=pk)
    # to get project with particular id
    # project = Project.objects.get(id=pk)
    # instance will prefill form with
    # projects  data
    form  = ProjectForm(instance=project)
    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(','," ").split()
        # to update the data in right project
        # we have to pass insatance 
        # here also
        # request files is used to upload images
        form  = ProjectForm(request.POST,request.FILES,instance=project)

        if form.is_valid():
            project = form.save()
            for tag in newtags:
                tag,created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('documents')
        
    context={'form':form}
    return render(request,'documents/doc_form.html',context)


@login_required(login_url="login")
def deleteProject(request,pk):
    profile  = request.user.profile
    # project = Project.objects.get(id=pk)
    project = profile.project_set.get(id=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('documents')
    context={
        'object':project
    }
    return render(request, 'delete_obj.html', context)