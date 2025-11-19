from django.db import models
from django.contrib.auth.models import AbstractUser

# -----------------------------------------------------------
# ROLES
# -----------------------------------------------------------
class Rol(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# USUARIOS (empleados del restaurante)
# -----------------------------------------------------------
class Usuario(models.Model):
    nombre = models.CharField(max_length=255)
    cc = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    password = models.CharField(max_length=255)
    fecha_contratacion = models.DateField(auto_now_add=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.rol.nombre})"


# -----------------------------------------------------------
# CLIENTES
# -----------------------------------------------------------
class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    cc = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# TIPOS DE ESTADO
# -----------------------------------------------------------
class TipoEstado(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# ESTADOS
# -----------------------------------------------------------
class Estado(models.Model):
    nombre = models.CharField(max_length=100)
    tipo_estado = models.ForeignKey(TipoEstado, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre} ({self.tipo_estado.nombre})"


# -----------------------------------------------------------
# MESAS
# -----------------------------------------------------------
class Mesa(models.Model):
    capacidad = models.PositiveIntegerField()
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    def __str__(self):
        return f"Mesa {self.id} - {self.estado.nombre}"


# -----------------------------------------------------------
# CATEGORÍAS DE PRODUCTOS
# -----------------------------------------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# TIPOS DE ÍTEM
# -----------------------------------------------------------
class TipoItem(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# ÍTEMS / PRODUCTOS
# -----------------------------------------------------------
class Item(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    tipo_item = models.ForeignKey(TipoItem, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# TIPOS DE PEDIDO
# -----------------------------------------------------------
class TipoPedido(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# PEDIDOS
# -----------------------------------------------------------
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    tipo_pedido = models.ForeignKey(TipoPedido, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.estado.nombre}"


# -----------------------------------------------------------
# DETALLE DE PEDIDOS
# -----------------------------------------------------------
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle Pedido #{self.id} - {self.item.nombre}"


# -----------------------------------------------------------
# FACTURAS
# -----------------------------------------------------------
class Factura(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ AGREGAR
    total = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Factura #{self.id} - Total: {self.total}"

# -----------------------------------------------------------
# DETALLE DE FACTURA
# -----------------------------------------------------------
class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle Factura #{self.id} - {self.item.nombre}"


# -----------------------------------------------------------
# FORMAS DE PAGO
# -----------------------------------------------------------
class FormaPago(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# -----------------------------------------------------------
# PAGOS
# -----------------------------------------------------------
class Pago(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    forma_pago = models.ForeignKey(FormaPago, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago #{self.id} - {self.forma_pago.nombre} - {self.monto}"

