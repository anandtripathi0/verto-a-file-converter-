from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.main,name='main'),
    path('img_to_pdf/', views.img_to_pdf,name='img_to_pdf'),
    path('compress/',views.compress,name='compress'),
    path('resize/',views.resizer,name='resize'),
    path('pdf_to_doc/',views.pdf_to_doc,name='pdf_to_doc'),
    path('pdf_merge/',views.pdf_merge,name='pdf_merge'),
    path('word_to_pdf/',views.word_to_pdf,name='word_to_pdf'),
]
