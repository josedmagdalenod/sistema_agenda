import re
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

class PerfilUsuario(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador Global'),
        ('COMPRAS', 'Analista de Compras'),
        ('SOLICITANTE', 'Usuario Solicitante'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='SOLICITANTE', verbose_name="Rol en el Sistema")

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance, rol='ADMIN' if instance.is_superuser else 'SOLICITANTE')

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


class Proveedor(models.Model):
    RUBRO_CHOICES = [
        ('Tecnología / Informática', 'Tecnología / Informática'),
        ('Ferretería / Materiales de Construcción', 'Ferretería / Materiales de Construcción'),
        ('Papelería / Material de Oficina', 'Papelería / Material de Oficina'),
        ('Mobiliario y Equipamiento', 'Mobiliario y Equipamiento'),
        ('Servicios Generales / Mantenimiento', 'Servicios Generales / Mantenimiento'),
        ('Telecomunicaciones', 'Telecomunicaciones'),
        ('Seguridad / Vigilancia', 'Seguridad / Vigilancia'),
        ('Limpieza y Aseo', 'Limpieza y Aseo'),
        ('Transporte / Logística', 'Transporte / Logística'),
        ('Otro / General', 'Otro / General'),
    ]

    rubro = models.CharField(max_length=100, choices=RUBRO_CHOICES, default='Otro / General', verbose_name='Rubro / Tipo de Servicio')
    nombre_empresa = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    rif = models.CharField(max_length=20, unique=True, verbose_name="RIF / Identificación Fiscal")
    telefono = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=150, blank=True, null=True, verbose_name="Correo Electrónico")
    direccion = models.TextField(verbose_name="Dirección Fiscal")
    
    documento_rif = models.FileField(upload_to='documentos_proveedores/rif/', blank=True, null=True, verbose_name="Copia de RIF")
    acta_constitutiva = models.FileField(upload_to='documentos_proveedores/actas/', blank=True, null=True, verbose_name="Acta Constitutiva")
    otros_documentos = models.FileField(upload_to='documentos_proveedores/otros/', blank=True, null=True, verbose_name="Otros Documentos")

    creado_el = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.nombre_empresa} ({self.rif})"


class EmpresaHolding(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Empresa del Holding")
    rif = models.CharField(max_length=20, unique=True, verbose_name="RIF")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Empresa del Holding"
        verbose_name_plural = "Empresas del Holding"

    def __str__(self):
        return self.nombre


class RequerimientoTicket(models.Model):
    ESTATUS_TICKET = [
        ('PENDIENTE', 'Pendiente por Revisar'),
        ('EN_CURSO', 'En Cotización / En Curso'),
        ('PROCESADO', 'Procesado / Comprado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario Solicitante")
    empresa_holding = models.ForeignKey(EmpresaHolding, on_delete=models.CASCADE, verbose_name="Empresa del Holding")
    ticket_glpi = models.CharField(max_length=50, blank=True, null=True, verbose_name="N° Ticket GLPI (Opcional)")
    titulo = models.CharField(max_length=200, verbose_name="Título / Asunto del Requerimiento")
    desglose_items = models.TextField(verbose_name="Lista / Desglose de Materiales Solicitados")
    estatus = models.CharField(max_length=20, choices=ESTATUS_TICKET, default='PENDIENTE', verbose_name="Estatus")
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Requerimiento / Ticket"
        verbose_name_plural = "Requerimientos / Tickets Solicitados"

    def __str__(self):
        return f"[Req #{self.id}] {self.titulo} - {self.solicitante.username}"


class RegistroCompraPago(models.Model):
    ESTATUS_CHOICES = [
        ('COTIZANDO', 'En Cotización'),
        ('COMPRADO', 'Comprado / Adjudicado'),
        ('TRANSITO', 'En Tránsito / Almacén'),
        ('ASIGNADO', 'Asignado a Empresa del Holding'),
    ]

    MONEDA_CHOICES = [
        ('USD', 'Dólares ($)'),
        ('VES', 'Bolívares (Bs.)'),
        ('EUR', 'Euros (€)'),
        ('USDT', 'USDT / Cripto'),
        ('OTRO', 'Otro Pago'),
    ]

    requerimiento_origen = models.ForeignKey(RequerimientoTicket, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras_asociadas', verbose_name="Requerimiento en Curso Seleccionado")
    solicitante_info = models.CharField(max_length=250, blank=True, null=True, verbose_name="Persona que Solicitó / Email")
    ticket_glpi = models.CharField(max_length=50, verbose_name="N° Ticket")
    titulo_requerimiento = models.CharField(max_length=200, verbose_name="Título / Asunto del Requerimiento")
    empresa_destino = models.ForeignKey(EmpresaHolding, on_delete=models.CASCADE, verbose_name="Empresa del Holding Asignada")
    fecha_registro = models.DateField(verbose_name="Fecha de Solicitud")
    moneda = models.CharField(max_length=10, choices=MONEDA_CHOICES, default='USD', verbose_name="Moneda de Pago")
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='COMPRADO', verbose_name="Estatus")

    desglose_items = models.TextField(verbose_name="Desglose de Ítems / Lista de Materiales Solicitados")

    proveedor_cot_1 = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_cot_1', verbose_name="Proveedor Cotización 1")
    monto_cot_1 = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Monto Cotización 1")
    archivo_cot_1 = models.FileField(upload_to='cotizaciones/', blank=True, null=True, verbose_name="PDF Cotización 1")

    proveedor_cot_2 = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_cot_2', verbose_name="Proveedor Cotización 2")
    monto_cot_2 = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Monto Cotización 2")
    archivo_cot_2 = models.FileField(upload_to='cotizaciones/', blank=True, null=True, verbose_name="PDF Cotización 2")

    proveedor_cot_3 = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_cot_3', verbose_name="Proveedor Cotización 3")
    monto_cot_3 = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Monto Cotización 3")
    archivo_cot_3 = models.FileField(upload_to='cotizaciones/', blank=True, null=True, verbose_name="PDF Cotización 3")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Solicitud / Ticket de Compra"
        verbose_name_plural = "Solicitudes / Tickets de Compras"

    def __str__(self):
        return f"[Ticket #{self.ticket_glpi}] {self.titulo_requerimiento}"

    @property
    def total_compra(self):
        return sum(pago.monto_pagado for pago in self.pagos_proveedores.all())


class PagoProveedorAdjudicado(models.Model):
    solicitud = models.ForeignKey(RegistroCompraPago, on_delete=models.CASCADE, related_name='pagos_proveedores')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name="Proveedor Adjudicado")
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Monto Pagado")
    fecha_pago = models.DateField(verbose_name="Fecha de Pago")
    descripcion_adjudicacion = models.TextField(blank=True, null=True, verbose_name="Desglose por Línea (Ítem | Marca | Serial | Costo)")
    factura = models.FileField(upload_to='facturas_compras/', blank=True, null=True, verbose_name="Factura (PDF/Imagen)")
    comprobante_pago = models.FileField(upload_to='comprobantes_pago/', blank=True, null=True, verbose_name="Comprobante de Pago (PDF/Imagen)")
    history = HistoricalRecords()

    def __str__(self):
        return f"Pago a {self.proveedor.nombre_empresa} - ${self.monto_pagado} ({self.fecha_pago})"



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Intentar parsear las líneas del desglose e insertarlas en Inventario
        if self.descripcion_adjudicacion:
            from gestion.models import Inventario
            lineas = self.descripcion_adjudicacion.splitlines()
            for line in lineas:
                line = line.strip()
                if not line: continue
                
                # Ejemplo de extracción o registro estructurado
                Inventario.objects.get_or_create(
                    producto_marca_modelo=line[:255],
                    proveedor=self.proveedor,
                    fecha_compra=self.fecha_pago or self.solicitud.fecha_registro,
                    empresa_asignada=self.solicitud.empresa_destino,
                    defaults={
                        'cantidad': 1,
                        'costo_unitario': self.monto_pagado or 0,
                        'serial_o_detalles': line,
                        'estatus': 'DISPONIBLE'
                    }
                )


class Inventario(models.Model):

    @property
    def cantidad_real(self):
        # 1. Si el producto empieza por un número (ej. '3 Marcadores', '5 BOLÍGRAFOS')
        if self.producto_marca_modelo:
            match = re.match(r'^(\d+)\s+', str(self.producto_marca_modelo).strip())
            if match:
                return match.group(1)
        # 2. De lo contrario, retornar el campo cantidad de la BD o 1
        return self.cantidad if self.cantidad else 1

    empresa_origen = models.ForeignKey('EmpresaHolding', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventario_origen', verbose_name='Empresa Origen')

    @property
    def get_empresa_origen_nombre(self):
        if hasattr(self, 'empresa_origen') and self.empresa_origen:
            return getattr(self.empresa_origen, 'nombre', str(self.empresa_origen))
        elif hasattr(self, 'empresa') and self.empresa:
            return getattr(self.empresa, 'nombre', str(self.empresa))
        return "WIWU"

    @property
    def get_empresa_asignada_nombre(self):
        if hasattr(self, 'empresa') and self.empresa:
            return getattr(self.empresa, 'nombre', str(self.empresa))
        elif hasattr(self, 'empresa_origen') and self.empresa_origen:
            return getattr(self.empresa_origen, 'nombre', str(self.empresa_origen))
        return "N/A"

    ESTATUS_INVENTARIO = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_STOCK', 'En Stock'),
        ('ASIGNADO', 'Asignado'),
        ('AGOTADO', 'Agotado'),
    ]

    TIPO_IVA_CHOICES = [
        ('CON_IVA', 'Con IVA (16%)'),
        ('SIN_IVA', 'Exento / Sin IVA'),
    ]

    producto_marca_modelo = models.CharField(max_length=250, verbose_name="Producto - Marca y Modelo")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Costo Unitario Base ($)")
    tipo_iva = models.CharField(max_length=10, choices=TIPO_IVA_CHOICES, default='CON_IVA', verbose_name="Condición de IVA")
    fecha_compra = models.DateField(null=True, blank=True, verbose_name="Fecha de Compra")
    
    empresa_asignada = models.ForeignKey(EmpresaHolding, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Empresa Asignada")
    estatus = models.CharField(max_length=20, choices=ESTATUS_INVENTARIO, default='EN_STOCK', verbose_name="Estatus")
    serial_o_detalles = models.TextField(blank=True, verbose_name="Seriales / Observaciones")
    actualizado_el = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Equipo / Material de Inventario"
        verbose_name_plural = "Inventario de Equipos y Materiales"

    def __str__(self):
        return f"{self.producto_marca_modelo} ({self.cantidad}) - ${self.costo_unitario}"

    @property
    def monto_iva(self):
        if self.tipo_iva == 'CON_IVA':
            return (self.costo_unitario * Decimal('0.16')).quantize(Decimal('0.01'))
        return Decimal('0.00')

    @property
    def costo_unitario_con_iva(self):
        return (self.costo_unitario + self.monto_iva).quantize(Decimal('0.01'))

    @property
    def costo_total(self):
        return (self.costo_unitario_con_iva * Decimal(self.cantidad)).quantize(Decimal('0.01'))

    @property
    def serial_limpio(self):
        if self.serial_o_detalles:
            match = re.search(r'S/N:\s*([^|]+)', self.serial_o_detalles)
            if match:
                val = match.group(1).strip()
                return val if val not in ['S/N', 'N/A', ''] else 'Sin Serial'
        return 'Sin Serial'


@receiver(post_save, sender=PagoProveedorAdjudicado)
def procesar_inventario_desde_pago(sender, instance, created, **kwargs):
    compra = instance.solicitud
    if compra.requerimiento_origen:
        req = compra.requerimiento_origen
        req.estatus = 'PROCESADO'
        req.save()

    if instance.descripcion_adjudicacion:
        lineas = [l.strip() for l in instance.descripcion_adjudicacion.strip().split('\n') if l.strip()]
        total_lineas = len(lineas) if len(lineas) > 0 else 1
        monto_pagado_total = instance.monto_pagado or Decimal('0.00')
        costo_prorrateado = (monto_pagado_total / Decimal(total_lineas)).quantize(Decimal('0.01')) if monto_pagado_total > 0 else Decimal('0.00')

        for linea in lineas:
            partes = [p.strip() for p in linea.split('|')]
            nombre_item = partes[0] if len(partes) > 0 else "Equipo"
            marca = partes[1] if len(partes) > 1 else ""
            serial = partes[2] if len(partes) > 2 else ""
            
            try:
                costo_val = Decimal(partes[3]) if len(partes) > 3 and Decimal(partes[3]) > 0 else costo_prorrateado
            except:
                costo_val = costo_prorrateado

            prod_nombre_completo = f"{nombre_item} - {marca}".strip(" -")
            serial_text = f"S/N: {serial} | Ticket #{compra.ticket_glpi}" if serial and serial not in ["S/N", "N/A"] else f"Ticket #{compra.ticket_glpi}"

            Inventario.objects.create(
                producto_marca_modelo=prod_nombre_completo,
                cantidad=1,
                proveedor=instance.proveedor,
                costo_unitario=costo_val,
                fecha_compra=instance.fecha_pago or compra.fecha_registro,
                empresa_asignada=compra.empresa_destino,
                estatus='ASIGNADO' if compra.estatus == 'ASIGNADO' else 'EN_STOCK',
                serial_o_detalles=serial_text
            )


class ItemCompraInventario(models.Model):
    compra = models.ForeignKey('RegistroCompraPago', on_delete=models.CASCADE, related_name='items_inventario', verbose_name="Compra / Pago")
    producto_item = models.CharField(max_length=255, verbose_name="Ítem / Producto")
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    serial = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serial / N° Serie")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Costo Unitario ($)")

    class Meta:
        verbose_name = "Ítem para Inventario"
        verbose_name_plural = "Ítems para Inventario (Marca, Serial y Costo)"

    def __str__(self):
        return f"{self.producto_item} - {self.marca or 'S/M'} - {self.serial or 'S/S'}"


from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=RegistroCompraPago)
def actualizar_estatus_requerimiento(sender, instance, created, **kwargs):
    if instance.requerimiento_origen:
        req = instance.requerimiento_origen
        # Buscar la clave interna adecuada de 'comprado'
        field = req._meta.get_field('estatus')
        target_val = 'comprado'
        if field.choices:
            for val, label in field.choices:
                if 'compra' in str(val).lower() or 'proces' in str(val).lower() or 'compra' in str(label).lower():
                    target_val = val
                    break
        req.estatus = target_val
        req.save()