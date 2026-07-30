from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from gestion import views

urlpatterns = [
    path('usuarios/', views.usuarios, name='usuarios'),
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='gestion/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Módulos del Sistema
    path('requerimientos/', views.lista_requerimientos, name='requerimientos'),
    path('requerimientos/estatus/<int:ticket_id>/<str:nuevo_estatus>/', views.cambiar_estatus_ticket, name='cambiar_estatus_ticket'),
    path('api/requerimiento/<int:ticket_id>/', views.api_obtener_requerimiento, name='api_obtener_requerimiento'),
    
    path('proveedores/', views.lista_proveedores, name='proveedores'),
    path('proveedores/pdf/', views.exportar_proveedores_pdf, name='proveedores_pdf'),
    
    path('compras/', views.lista_compras, name='compras'),
    
    # Facturas y Trazabilidad Contable
    path('facturas/', views.trazabilidad_facturas, name='facturas'),
    path('facturas/pdf/', views.exportar_facturas_pdf, name='facturas_pdf'),
    
    path('inventario/', views.lista_inventario, name='inventario'),
    path('inventario/transferir/<int:item_id>/', views.transferir_equipo, name='transferir_equipo'),
    path('inventario/excel/', views.exportar_inventario_excel, name='inventario_excel'),
    path('inventario/pdf/', views.exportar_inventario_pdf, name='inventario_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
