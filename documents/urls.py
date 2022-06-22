from django.urls import path
from .import views

urlpatterns = [
    path('documents/',views.documents,name='documents'),
    path('document/<str:pk>/', views.document,name='document'),
    path('create-project/', views.createProject,name='create-project'),
    path('update-project/<str:pk>/', views.updateProject,name='update-project'),
    path('delete-project/<str:pk>/', views.deleteProject,name='delete-project'),
]
