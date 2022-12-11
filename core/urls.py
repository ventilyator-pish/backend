from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from core.views import TagViewSet, StudentProfileViewSet, ProjectViewSet, CompanyViewSet, ReviewViewSet, StudentRequestViewSet, CrowdFoundingViewSet, TinderViewSet


router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("profiles", StudentProfileViewSet)
router.register("projects", ProjectViewSet)
router.register("companies", CompanyViewSet)
router.register("reviews", ReviewViewSet)
router.register("student_requests", StudentRequestViewSet)
router.register("crowdfounding", CrowdFoundingViewSet)
router.register("tinder", TinderViewSet)


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      terms_of_service="https://www.ggoogle.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   url="https://engineers-itmo.ru/api/",
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
