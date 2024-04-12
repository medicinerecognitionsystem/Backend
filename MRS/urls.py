"""
URL configuration for MRS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from MRS import views
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.landingPage),
    path('admin', admin.site.urls),
    path('about', views.aboutPage),
    path('web', webHandler),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def custom404(request, exception):
    errorType ={'errorCode':'404', 'errorDescription':'Could not find the page you requested.'}
    return render(request, 'error.html', errorType)

handler404 = custom404