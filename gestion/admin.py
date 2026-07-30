from django.contrib import admin
from django import forms
from django.db import models
from .models import (
    PerfilUsuario,
    Proveedor,
    EmpresaHolding,
    RequerimientoTicket,
    RegistroCompraPago,
    PagoProveedorAdjudicado,
    Inventario,
    ItemCompraInventario
)

class ItemCompraInventarioInline(admin.TabularInline):
    model = ItemCompraInventario
    extra = 1
    fields = ('producto_item', 'marca', 'modelo', 'serial', 'cantidad', 'costo_unitario')
    verbose_name = "Ítem de Inventario"
    verbose_name_plural = "Ítems para Inventario (Marca, Serial y Costo)"

class PagoProveedorAdjudicadoInline(admin.StackedInline):
    model = PagoProveedorAdjudicado
    extra = 1

@admin.register(RegistroCompraPago)
class RegistroCompraPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_glpi', 'titulo_requerimiento', 'solicitante_info', 'fecha_registro', 'estatus')
    inlines = [PagoProveedorAdjudicadoInline, ItemCompraInventarioInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['requerimiento_origen', 'requerimiento', 'requerimiento_ticket']:
            from gestion.models import RequerimientoTicket, RegistroCompraPago
            from django.db.models import Q
            
            # Obtener IDs de requerimientos que YA están asignados a una compra
            usados_ids = list(RegistroCompraPago.objects.exclude(requerimiento_origen=None).values_list('requerimiento_origen_id', flat=True))
            usados_ids = [x for x in usados_ids if x is not None]
            
            # FILTRO ESTRICTO: Solo Requerimientos que estén "En Curso" o "Cotizando" y NO estén en la lista de usados
            qs = RequerimientoTicket.objects.filter(
                Q(estatus__icontains='curso') | Q(estatus__icontains='cotiz') | Q(estatus__icontains='pendiente')
            ).exclude(id__in=usados_ids)
            
            # Si se está editando una compra previa, incluir su propio requerimiento
            object_id = request.resolver_match.kwargs.get('object_id') if request.resolver_match else None
            if object_id:
                compra = RegistroCompraPago.objects.filter(id=object_id).first()
                if compra and compra.requerimiento_origen_id:
                    qs = RequerimientoTicket.objects.filter(
                        id__in=list(qs.values_list('id', flat=True)) + [compra.requerimiento_origen_id]
                    )
            
            kwargs['queryset'] = qs.order_by('-id')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
class RequerimientoTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_glpi', 'titulo', 'solicitante', 'estatus', 'creado_el')

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_empresa', 'rubro', 'rif', 'telefono', 'email', 'verificado')
    search_fields = ('nombre_empresa', 'rubro', 'rif', 'email')
    change_form_template = 'admin/gestion/proveedor/change_form.html'

    fieldsets = (
        (None, {'fields': ('rubro', 'nombre_empresa', 'rif', 'telefono', 'email', 'direccion', 'documento_rif', 'acta_constitutiva', 'otros_documentos')}),
        ('Verificación (auditor)', {
            'fields': (
                'nombre_empresa_verificado', 'rif_verificado', 'telefono_verificado', 'email_verificado',
                'direccion_verificada', 'documento_rif_verificado', 'acta_constitutiva_verificada', 'verificado'
            ),
            'description': 'Marcar cada ítem verificado por el auditor. El checkbox "Proveedor verificado" sólo se habilita cuando todos los ítems estén marcados.'
        }),
    )

    class Media:
        js = ('gestion/js/admin_proveedor_verificacion.js',)

    def save_model(self, request, obj, form, change):
        # Validación en servidor: sólo permitir marcar 'verificado' si todos los ítems están verificados
        all_checked = all([
            obj.nombre_empresa_verificado,
            obj.rif_verificado,
            obj.telefono_verificado,
            obj.email_verificado,
            obj.direccion_verificada,
            obj.documento_rif_verificado,
            obj.acta_constitutiva_verificada,
        ])
        if obj.verificado and not all_checked:
            from django.contrib import messages
            messages.error(request, "No puede marcar 'Verificado' hasta que todos los ítems estén verificados.")
            obj.verificado = False
        super().save_model(request, obj, form, change)

@admin.register(EmpresaHolding)
class EmpresaHoldingAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'rif')

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto_marca_modelo', 'empresa_origen', 'empresa_asignada', 'costo_unitario', 'estatus', 'fecha_compra')
    search_fields = ('producto_marca_modelo', 'serial_o_detalles', 'proveedor__nombre')
    list_filter = ('estatus', 'empresa_origen', 'empresa_asignada', 'fecha_compra')

    def get_readonly_fields(self, request, obj=None):
        # Campos críticos que no deben alterarse en compras ya registradas
        campos_protegidos = ['costo_unitario', 'tipo_iva', 'proveedor', 'fecha_compra', 'empresa_origen']
        
        # Si el usuario NO es superusuario, se le bloquean los campos financieros/origen
        if not request.user.is_superuser:
            return campos_protegidos
        return []
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'rol')




@admin.register(RequerimientoTicket)
class RequerimientoTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'estatus')
    search_fields = ('titulo', 'estatus')
