"""sales URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.views.static import serve

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.documentation import include_docs_urls

from utils import constants


def custom404(request, exception=None):
    return JsonResponse({
        'status_code': 404,
        'detail': 'The resource was not found'
    }, status=404)


handler404 = custom404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title=constants.SYSTEM_NAME, permission_classes=[])),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/token-auth/', obtain_jwt_token),
    url(r'^api/account/', include('account.urls')),
    url(r'^api/member/', include('member.urls')),
    url(r'^api/master/', include('master.urls')),
    url(r'^api/org/', include('org.urls')),
    url(r'^api/contract/', include('contract.urls')),
    url(r'^api/partner/', include('partner.urls')),
    url(r'^api/client/', include('client.urls')),
    url(r'^api/project/', include('project.urls')),
    url(r'^api/attendance/', include('attendance.urls')),
    url(r'^api/request/', include('request.urls')),
    url(r'^api/turnover/', include('turnover.urls')),
]
