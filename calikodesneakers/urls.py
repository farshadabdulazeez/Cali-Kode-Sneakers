from django.contrib import admin
from django.urls import path, include
from calikodesneakers import settings
from django.conf.urls.static import static


urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('user_app.urls')),
    path('custom-admin/', include('admin_app.urls')),
    path('products/', include('product_app.urls')),
    path('cart/', include('cart_app.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)