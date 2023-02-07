"""Dolly_Sabby_farm_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
from django.conf.urls import include
from Dolly_Sabby_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('',views.index,name='index'),
    # path('Dolly_Sabby_app/',include('Dolly_Sabby_app.urls')),
    path('admin/', admin.site.urls),
    path('',include('Dolly_Sabby_app.urls')),
    
    path('form/',views.form_name_view,name='form_name'),
    path('logout/',views.user_logout,name='logout'),
    path('special/',views.special,name='special'),
]


urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
