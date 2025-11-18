from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import (
    Item, Categoria, Mesa, Pedido, DetallePedido,
    Factura, DetalleFactura, Cliente, Usuario, Estado, 
    TipoPedido, FormaPago, Pago, Rol
)
from decimal import Decimal

# ============================================
# DECORADORES PERSONALIZADOS
# ============================================

def rol_requerido(*roles_permitidos):
    """
    Decorador para verificar que el usuario tenga uno de los roles permitidos
    Uso: @rol_requerido('Administrador', 'Cajero')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar si hay usuario en sesión
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                messages.error(request, 'Debes iniciar sesión para acceder a esta página')
                return redirect('core:login')
            
            # Obtener usuario
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                request.usuario = usuario  # Agregar usuario al request
                
                # Verificar rol
                if usuario.rol.nombre not in roles_permitidos:
                    messages.error(request, 'No tienes permisos para acceder a esta página')
                    return redirect('core:dashboard')
                
                return view_func(request, *args, **kwargs)
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no válido')
                return redirect('core:login')
        
        return wrapper
    return decorator


def login_requerido(view_func):
    """Decorador simple para verificar si el usuario está logueado"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('core:login')
        
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            request.usuario = usuario
            return view_func(request, *args, **kwargs)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no válido')
            return redirect('core:login')
    
    return wrapper


# ============================================
# VISTAS DE AUTENTICACIÓN
# ============================================

def login(request):
    """Vista de login"""
    # Si ya está logueado, redirigir al dashboard
    if request.session.get('usuario_id'):
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Buscar usuario por email y contraseña
            usuario = Usuario.objects.select_related('rol').get(
                email=email,
                password=password  # En producción usar hash
            )
            
            # Guardar en sesión
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.rol.nombre
            
            messages.success(request, f'¡Bienvenido {usuario.nombre}!')
            return redirect('core:dashboard')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'Email o contraseña incorrectos')
    
    return render(request, 'core/auth/login.html')


@login_requerido
def logout(request):
    """Cerrar sesión"""
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('core:login')


@login_requerido
def dashboard(request):
    """Dashboard principal que redirige según el rol"""
    rol = request.session.get('usuario_rol')
    
    # Redirigir según el rol
    if rol == 'Administrador':
        return redirect('core:admin_dashboard')
    elif rol == 'Mesero':
        return redirect('core:mesero_dashboard')
    elif rol == 'Cajero':
        return redirect('core:cajero_dashboard')
    else:
        messages.error(request, 'Rol no reconocido. Contacte al administrador.')
        return redirect('core:login')


# ============================================
# DASHBOARD ADMINISTRADOR
# ============================================

@rol_requerido('Administrador')
def admin_dashboard(request):
    """Dashboard del Administrador - Acceso completo"""
    # Estadísticas generales
    total_mesas = Mesa.objects.count()
    mesas_disponibles = Mesa.objects.filter(estado__nombre='Disponible').count()
    pedidos_activos = Pedido.objects.filter(
        estado__nombre__in=['Pendiente', 'En preparación']
    ).count()
    items_disponibles = Item.objects.filter(estado__nombre='Activo').count()
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.all().select_related(
        'cliente', 'mesa', 'estado', 'usuario'
    ).order_by('-fecha')[:5]
    
    # Estadísticas de ventas
    total_pedidos = Pedido.objects.count()
    total_clientes = Cliente.objects.count()
    total_empleados = Usuario.objects.count()
    
    # Calcular ingresos del día
    from datetime import date
    hoy = date.today()
    facturas_hoy = Factura.objects.filter(fecha__date=hoy)
    ingresos_hoy = sum(f.total for f in facturas_hoy)
    
    context = {
        'total_mesas': total_mesas,
        'mesas_disponibles': mesas_disponibles,
        'pedidos_activos': pedidos_activos,
        'items_disponibles': items_disponibles,
        'pedidos_recientes': pedidos_recientes,
        'total_pedidos': total_pedidos,
        'total_clientes': total_clientes,
        'total_empleados': total_empleados,
        'ingresos_hoy': ingresos_hoy,
    }
    return render(request, 'core/dashboards/admin_dashboard.html', context)


# ============================================
# DASHBOARD MESERO
# ============================================

@rol_requerido('Mesero')
def mesero_dashboard(request):
    """Dashboard del Mesero - Gestión de pedidos y mesas"""
    # Mesas disponibles y ocupadas
    mesas_disponibles = Mesa.objects.filter(estado__nombre='Disponible')
    mesas_ocupadas = Mesa.objects.filter(estado__nombre='Ocupada')
    
    # Pedidos activos del mesero
    mis_pedidos = Pedido.objects.filter(
        usuario_id=request.session.get('usuario_id'),
        estado__nombre__in=['Pendiente', 'En preparación']
    ).select_related('cliente', 'mesa', 'estado')
    
    # Categorías e items para crear pedidos rápidos
    categorias = Categoria.objects.all()
    items_populares = Item.objects.filter(estado__nombre='Activo')[:8]
    
    context = {
        'mesas_disponibles': mesas_disponibles,
        'mesas_ocupadas': mesas_ocupadas,
        'mis_pedidos': mis_pedidos,
        'categorias': categorias,
        'items_populares': items_populares,
        'total_mesas_disponibles': mesas_disponibles.count(),
        'total_mis_pedidos': mis_pedidos.count(),
    }
    return render(request, 'core/dashboards/mesero_dashboard.html', context)


# ============================================
# DASHBOARD CAJERO
# ============================================

@rol_requerido('Cajero')
def cajero_dashboard(request):
    """Dashboard del Cajero - Facturación y cobros"""
    # Pedidos pendientes de facturar
    pedidos_sin_factura = Pedido.objects.filter(
        factura__isnull=True,
        estado__nombre='Entregado'
    ).select_related('cliente', 'mesa', 'usuario')
    
    # Facturas del día
    from datetime import date
    hoy = date.today()
    facturas_hoy = Factura.objects.filter(
        fecha__date=hoy
    ).select_related('cliente', 'usuario', 'pedido')
    
    # Total recaudado hoy
    total_recaudado = sum(f.total for f in facturas_hoy)
    
    # Formas de pago
    formas_pago = FormaPago.objects.all()
    
    # Pedidos listos para entregar
    pedidos_listos = Pedido.objects.filter(
        estado__nombre='En preparación'
    ).select_related('cliente', 'mesa')
    
    context = {
        'pedidos_sin_factura': pedidos_sin_factura,
        'facturas_hoy': facturas_hoy,
        'total_recaudado': total_recaudado,
        'formas_pago': formas_pago,
        'pedidos_listos': pedidos_listos,
        'total_facturas_hoy': facturas_hoy.count(),
    }
    return render(request, 'core/dashboards/cajero_dashboard.html', context)


# ============================================
# DASHBOARD CHEF
# ============================================

@rol_requerido('Chef')
def chef_dashboard(request):
    """Dashboard del Chef - Gestión de cocina"""
    # Pedidos pendientes de preparar
    pedidos_pendientes = Pedido.objects.filter(
        estado__nombre='Pendiente'
    ).select_related('cliente', 'mesa', 'usuario').order_by('fecha')
    
    # Pedidos en preparación
    pedidos_en_preparacion = Pedido.objects.filter(
        estado__nombre='En preparación'
    ).select_related('cliente', 'mesa', 'usuario')
    
    # Items más pedidos del día
    from datetime import date
    hoy = date.today()
    items_del_dia = DetallePedido.objects.filter(
        pedido__fecha__date=hoy
    ).values('item__nombre').annotate(
        cantidad_total=Sum('cantidad')
    ).order_by('-cantidad_total')[:5]
    
    # Stock bajo
    items_stock_bajo = Item.objects.filter(
        estado__nombre='Activo',
        stock__lt=10
    )
    
    context = {
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_en_preparacion': pedidos_en_preparacion,
        'items_del_dia': items_del_dia,
        'items_stock_bajo': items_stock_bajo,
        'total_pendientes': pedidos_pendientes.count(),
        'total_en_preparacion': pedidos_en_preparacion.count(),
    }
    return render(request, 'core/dashboards/chef_dashboard.html', context)


# ============================================
# VISTAS COMPARTIDAS (con permisos)
# ============================================

@login_requerido
def menu(request):
    """Mostrar el menú - Acceso para todos"""
    categorias = Categoria.objects.all()
    items = Item.objects.filter(estado__nombre='Activo').select_related(
        'categoria', 'tipo_item', 'estado'
    )
    
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        items = items.filter(categoria_id=categoria_id)
    
    context = {
        'categorias': categorias,
        'items': items,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
    }
    return render(request, 'core/menu.html', context)


@rol_requerido('Administrador', 'Mesero')
def mesas(request):
    """Gestión de mesas - Solo Admin y Mesero"""
    mesas_list = Mesa.objects.all().select_related('estado')
    disponibles = mesas_list.filter(estado__nombre='Disponible').count()
    ocupadas = mesas_list.filter(estado__nombre='Ocupada').count()
    
    context = {
        'mesas': mesas_list,
        'total_mesas': mesas_list.count(),
        'disponibles': disponibles,
        'ocupadas': ocupadas,
    }
    return render(request, 'core/mesas.html', context)


@rol_requerido('Administrador', 'Mesero', 'Cajero')
def pedidos(request):
    """Lista de pedidos - Admin, Mesero y Cajero"""
    rol = request.session.get('usuario_rol')
    
    pedidos_list = Pedido.objects.all().select_related(
        'cliente', 'mesa', 'estado', 'usuario', 'tipo_pedido'
    ).prefetch_related('detallepedido_set__item').order_by('-fecha')
    
    # Si es mesero, solo ver sus pedidos
    if rol == 'Mesero':
        pedidos_list = pedidos_list.filter(
            usuario_id=request.session.get('usuario_id')
        )
    
    estado_filter = request.GET.get('estado')
    if estado_filter:
        pedidos_list = pedidos_list.filter(estado__nombre=estado_filter)
    
    context = {
        'pedidos': pedidos_list,
        'estados': Estado.objects.filter(tipo_estado__nombre='Pedido'),
    }
    return render(request, 'core/pedidos.html', context)


@rol_requerido('Administrador', 'Mesero')
def crear_pedido(request):
    """Crear pedido - Admin y Mesero"""
    if request.method == 'POST':
        try:
            cliente_id = request.POST.get('cliente_id')
            mesa_id = request.POST.get('mesa_id')
            tipo_pedido_id = request.POST.get('tipo_pedido_id')
            items_ids = request.POST.getlist('items[]')
            cantidades = request.POST.getlist('cantidades[]')
            
            if not items_ids or not cantidades:
                messages.error(request, 'Debes agregar al menos un item al pedido')
                return redirect('core:crear_pedido')
            
            cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None
            mesa = Mesa.objects.get(id=mesa_id) if mesa_id else None
            
            estado = Estado.objects.get(nombre='Pendiente', tipo_estado__nombre='Pedido')
            tipo_pedido = TipoPedido.objects.get(id=tipo_pedido_id)
            
            # Usar el usuario logueado
            usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
            
            # Crear pedido
            pedido = Pedido.objects.create(
                cliente=cliente,
                mesa=mesa,
                estado=estado,
                tipo_pedido=tipo_pedido,
                usuario=usuario
            )
            
            total_pedido = Decimal('0.00')
            for item_id, cantidad in zip(items_ids, cantidades):
                if not cantidad or int(cantidad) <= 0:
                    continue
                    
                item = Item.objects.get(id=item_id)
                cantidad = int(cantidad)
                subtotal = item.precio * cantidad
                total_pedido += subtotal
                
                DetallePedido.objects.create(
                    pedido=pedido,
                    item=item,
                    cantidad=cantidad,
                    subtotal=subtotal
                )
            
            if mesa:
                estado_ocupada = Estado.objects.filter(nombre='Ocupada').first()
                if estado_ocupada:
                    mesa.estado = estado_ocupada
                    mesa.save()
            
            messages.success(request, f'Pedido #{pedido.id} creado exitosamente. Total: ${total_pedido}')
            return redirect('core:pedidos')
            
        except Exception as e:
            messages.error(request, f'Error al crear pedido: {str(e)}')
    
    context = {
        'clientes': Cliente.objects.all(),
        'mesas': Mesa.objects.filter(estado__nombre='Disponible'),
        'items': Item.objects.filter(estado__nombre='Activo').select_related('categoria'),
        'tipos_pedido': TipoPedido.objects.all(),
        'categorias': Categoria.objects.all(),
    }
    return render(request, 'core/crear_pedido.html', context)


@rol_requerido('Administrador', 'Cajero', 'Mesero')
def generar_factura(request, pedido_id):
    """Generar factura - Admin, Cajero y Mesero"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido).select_related('item')
    
    subtotal = sum(detalle.subtotal for detalle in detalles)
    descuento = Decimal('0.00')
    total = subtotal - descuento
    
    try:
        factura = Factura.objects.get(pedido=pedido)
    except Factura.DoesNotExist:
        factura = None
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'subtotal': subtotal,
        'descuento': descuento,
        'total': total,
        'factura': factura,
        'formas_pago': FormaPago.objects.all(),
    }
    return render(request, 'core/factura.html', context)


# Página de inicio pública (redirige al login)
def index(request):
    """Página de inicio - redirige al login si no está autenticado"""
    if request.session.get('usuario_id'):
        return redirect('core:dashboard')
    return redirect('core:login')