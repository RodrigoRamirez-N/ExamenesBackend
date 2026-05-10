from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from examenes.views import ExamenPresentadoViewSet, ExamenViewSet, ResumenAnaliticaAPIView
from usuarios.views import LoginAPIView, LogoutAPIView, UsuarioViewSet

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")
router.register(r"examenes", ExamenViewSet, basename="examenes")
router.register(r"examenes-presentados", ExamenPresentadoViewSet, basename="examenes-presentados")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
    path("api/login/", LoginAPIView.as_view(), name="api-login"),
    path("api/logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("api/analitica/resumen/", ResumenAnaliticaAPIView.as_view(), name="api-analitica-resumen"),
    path("api/", include(router.urls)),
]
