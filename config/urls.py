from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ESSA LINHA É A MAIS IMPORTANTE
    path('', include('apps.base.core.urls')),
]
