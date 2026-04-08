# """
# URL configuration for pdf_converter project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/6.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin
from django.urls import path,include
# from . import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('home/', views.home,name='home'),
#     path('compress/',views.compress,name='compress'),
#     path('jpg_to_doc/',views.jpg_to_doc,name='jpg_to_doc'),
#     path('pdf_merge/',views.pdf_merge,name='pdf_merge'),
#     path('word_to_pdf/',views.word_to_pdf,name='word_to_pdf'),
# ]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('converter.urls')),
]