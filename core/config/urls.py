# core/config/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.website.urls")),
    # path('dashboard/', include('dashboard.urls')),
    # path('accounts/', include('accounts.urls')),
    # path('shop/', include('shop.urls')),
    # path('cart/', include('cart.urls')),
    # path('order/', include('order.urls')),
    # path('payment/', include('payment.urls')),
    # path('review/', include('review.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

# if settings.DEBUG:
#     urlpatterns += [
#         path("__debug__/", include("debug_toolbar.urls")),
#     ]
