from django.contrib import admin
from django.urls import include, path
from recipes.views import DecodeView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
    path('s/<str:short_link>/', DecodeView.as_view(), name='short_link_decode'),
]
