from django.contrib import admin
from django.urls import path,include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from timetable.views import TimeTableView

schema_view = get_schema_view(
    openapi.Info(
        title="Dtuotg API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.ourapp.com/policies/terms/",
        contact=openapi.Contact(email="contact@expenses.local"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('user.urls')),
    path('events/',include('events.urls')),
    path('social_auth/',include('social_auth.urls')),
    path('', schema_view.with_ui('swagger',
                                 cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
                                       cache_timeout=0), name='schema-redoc'),
    path('timetablet/', TimeTableView, name='timetable') 
]

urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
