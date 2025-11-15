from django.contrib import admin
from .models import (
    Rol, Usuario, Cliente, TipoEstado, Estado, Mesa, Categoria,
    TipoItem, Item, TipoPedido, Pedido, DetallePedido, Factura,
    DetalleFactura, FormaPago, Pago
)

# -----------------------------------------------------------
# CONFIGURACIÓN DE MODELOS EN ADMIN
# -----------------------------------------------------------

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cc', 'email', 'rol', 'fecha_contratacion', 'salario')
    list_filter = ('rol',)
    search_fields = ('nombre', 'cc', 'email')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cc', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'cc', 'telefono')


@admin.register(TipoEstado)
class TipoEstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo_estado')
    list_filter = ('tipo_estado',)


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('id', 'capacidad', 'estado')
    list_filter = ('estado',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(TipoItem)
class TipoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock', 'categoria', 'tipo_item', 'estado')
    list_filter = ('categoria', 'tipo_item', 'estado')
    search_fields = ('nombre',)


@admin.register(TipoPedido)
class TipoPedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'mesa', 'estado', 'tipo_pedido', 'fecha', 'usuario')
    list_filter = ('estado', 'tipo_pedido')
    search_fields = ('cliente__nombre', 'usuario__nombre')


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'item', 'cantidad', 'subtotal')


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'cliente', 'usuario', 'fecha', 'total', 'descuento')


@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'factura', 'item', 'cantidad', 'subtotal')


@admin.register(FormaPago)
class FormaPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'factura', 'forma_pago', 'monto', 'fecha')
    list_filter = ('forma_pago',)

admin.site.site_header = "Sistema de Gestión del Restaurante"
admin.site.site_title = "Panel Administrativo"
admin.site.index_title = "Bienvenido al Panel de Gestión"