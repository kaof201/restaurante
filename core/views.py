from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from functools import wraps
from .models import (
    Item, Categoria, Mesa, Pedido, DetallePedido,
    Factura, DetalleFactura, Cliente, Usuario, Estado, 
    TipoPedido, FormaPago, Pago, Rol
)
from decimal import Decimal
from datetime import date

# ============================================
# DECORADORES PERSONALIZADOS - MEJORADOS
# ============================================

def rol_requerido(*roles_permitidos):
    """
    Decorador para verificar que el usuario tenga uno de los roles permitidos
    Uso: @rol_requerido('Administrador', 'Cajero')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar si existe sesión
            usuario_id = request.session.get('usuario_id')
            
            if not usuario_id:
                messages.warning(request, 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.')
                return redirect('core:login')
            
            try:
                usuario = Usuario.objects.select_related('rol').get(id=usuario_id)
                
                # Verificar que el rol coincide con el guardado en sesión
                rol_sesion = request.session.get('usuario_rol')
                if usuario.rol.nombre != rol_sesion:
                    messages.error(request, 'Sesión inválida. Por favor, inicia sesión nuevamente.')
                    request.session.flush()
                    return redirect('core:login')
                
                # Verificar permisos
                if usuario.rol.nombre not in roles_permitidos:
                    messages.error(request, f'Acceso denegado. Esta página es solo para: {", ".join(roles_permitidos)}')
                    return redirect('core:dashboard')
                
                # Actualizar última actividad
                request.session['ultima_actividad'] = timezone.now().isoformat()
                
                # Adjuntar usuario al request
                request.usuario = usuario
                
                return view_func(request, *args, **kwargs)
                
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no válido. Por favor, inicia sesión nuevamente.')
                request.session.flush()
                return redirect('core:login')
        
        return wrapper
    return decorator


def login_requerido(view_func):
    """Decorador simple para verificar si el usuario está logueado"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        
        if not usuario_id:
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('core:login')
        
        try:
            usuario = Usuario.objects.select_related('rol').get(id=usuario_id)
            request.usuario = usuario
            
            # Actualizar última actividad
            request.session['ultima_actividad'] = timezone.now().isoformat()
            
            return view_func(request, *args, **kwargs)
            
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no válido')
            request.session.flush()
            return redirect('core:login')
    
    return wrapper


# ============================================
# VISTAS DE AUTENTICACIÓN - MEJORADAS
# ============================================

def login(request):
    """Vista de login mejorada con validación de sesión"""
    
    # Si ya está logueado, redirigir al dashboard
    if request.session.get('usuario_id'):
        usuario_id = request.session.get('usuario_id')
        
        # Verificar que el usuario aún existe
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            return redirect('core:dashboard')
        except Usuario.DoesNotExist:
            # Usuario no existe, limpiar sesión
            request.session.flush()
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Validaciones
        if not email or not password:
            messages.error(request, 'Por favor, completa todos los campos')
            return render(request, 'core/auth/login.html')
        
        try:
            # Buscar usuario
            usuario = Usuario.objects.select_related('rol').get(
                email=email,
                password=password
            )
            
            # Limpiar cualquier sesión anterior
            request.session.flush()
            
            # Crear nueva sesión
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.rol.nombre
            request.session['login_time'] = timezone.now().isoformat()
            request.session['ultima_actividad'] = timezone.now().isoformat()
            
            # Configurar tiempo de expiración
            request.session.set_expiry(28800)  # 8 horas
            
            messages.success(request, f'¡Bienvenido {usuario.nombre}!')
            
            # Log de inicio de sesión
            print(f"✓ Login exitoso: {usuario.email} ({usuario.rol.nombre}) - Sesión ID: {request.session.session_key}")
            
            return redirect('core:dashboard')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'Email o contraseña incorrectos')
            print(f"✗ Intento de login fallido: {email}")
    
    return render(request, 'core/auth/login.html')


@login_requerido
def logout(request):
    """Cerrar sesión mejorada"""
    usuario_nombre = request.session.get('usuario_nombre', 'Usuario')
    usuario_rol = request.session.get('usuario_rol', '')
    
    # Log de cierre de sesión
    print(f"✓ Logout: {usuario_nombre} ({usuario_rol}) - Sesión ID: {request.session.session_key}")
    
    # Destruir completamente la sesión
    request.session.flush()
    
    messages.success(request, f'Hasta pronto, {usuario_nombre}. Sesión cerrada correctamente.')
    return redirect('core:login')


def index(request):
    """Página de inicio - redirige al login o dashboard"""
    if request.session.get('usuario_id'):
        # Verificar que la sesión sea válida
        try:
            usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
            return redirect('core:dashboard')
        except Usuario.DoesNotExist:
            request.session.flush()
            return redirect('core:login')
    
    return redirect('core:login')


@login_requerido
def dashboard(request):
    """Dashboard principal que redirige según el rol"""
    rol = request.session.get('usuario_rol')
    
    print(f"→ Redirigiendo dashboard para rol: {rol}")
    
    if rol == 'Administrador':
        return redirect('core:admin_dashboard')
    elif rol == 'Mesero':
        return redirect('core:mesero_dashboard')
    elif rol == 'Cajero':
        return redirect('core:cajero_dashboard')
    elif rol == 'Chef':
        return redirect('core:chef_dashboard')
    else:
        messages.error(request, 'Rol no reconocido. Contacte al administrador.')
        request.session.flush()
        return redirect('core:login')


# ============================================
# RESTO DE TUS VISTAS (sin cambios)
# ============================================

@rol_requerido('Administrador')
def admin_dashboard(request):
    """Dashboard del Administrador"""
    total_mesas = Mesa.objects.count()
    mesas_disponibles = Mesa.objects.filter(estado__nombre='Disponible').count()
    pedidos_activos = Pedido.objects.filter(
        estado__nombre__in=['Pendiente', 'En preparación']
    ).count()
    items_disponibles = Item.objects.filter(estado__nombre='Activo').count()
    
    pedidos_recientes = Pedido.objects.all().select_related(
        'cliente', 'mesa', 'estado', 'usuario'
    ).order_by('-fecha')[:5]
    
    total_pedidos = Pedido.objects.count()
    total_clientes = Cliente.objects.count()
    total_empleados = Usuario.objects.count()
    
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
    return render(request, 'core/dashboard/admin_dashboard.html', context)
# ============================================
# DASHBOARD MESERO
# ============================================

@rol_requerido('Mesero')
def mesero_dashboard(request):
    """Dashboard del Mesero - Gestion de pedidos y mesas"""
    mesas_disponibles = Mesa.objects.filter(estado__nombre='Disponible')
    mesas_ocupadas = Mesa.objects.filter(estado__nombre='Ocupada')
    
    mis_pedidos = Pedido.objects.filter(
        usuario_id=request.session.get('usuario_id'),
        estado__nombre__in=['Pendiente', 'En preparación']
    ).select_related('cliente', 'mesa', 'estado').prefetch_related('detallepedido_set__item')
    
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
    return render(request, 'core/dashboard/mesero_dashboard.html', context)


# ============================================
# DASHBOARD CAJERO
# ============================================

@rol_requerido('Cajero')
def cajero_dashboard(request):
    """Dashboard del Cajero - Facturacion y cobros"""
    pedidos_sin_factura = Pedido.objects.filter(
        factura__isnull=True,
        estado__nombre='Entregado'
    ).select_related('cliente', 'mesa', 'usuario').prefetch_related('detallepedido_set__item')
    
    hoy = date.today()
    facturas_hoy = Factura.objects.filter(
        fecha__date=hoy
    ).select_related('cliente', 'usuario', 'pedido')
    
    total_recaudado = sum(f.total for f in facturas_hoy)
    
    formas_pago = FormaPago.objects.all()
    
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
    return render(request, 'core/dashboard/cajero_dashboard.html', context)


# ============================================
# DASHBOARD CHEF
# ============================================

@rol_requerido('Chef')
def chef_dashboard(request):
    """Dashboard del Chef - Gestion de cocina"""
    pedidos_pendientes = Pedido.objects.filter(
        estado__nombre='Pendiente'
    ).select_related('cliente', 'mesa', 'usuario').order_by('fecha').prefetch_related('detallepedido_set__item')
    
    pedidos_en_preparacion = Pedido.objects.filter(
        estado__nombre='En preparación'
    ).select_related('cliente', 'mesa', 'usuario').prefetch_related('detallepedido_set__item')
    
    hoy = date.today()
    items_del_dia = DetallePedido.objects.filter(
        pedido__fecha__date=hoy
    ).values('item__nombre').annotate(
        cantidad_total=Sum('cantidad')
    ).order_by('-cantidad_total')[:5]
    
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
    return render(request, 'core/dashboard/chef_dashboard.html', context)


# ============================================
# VISTAS COMPARTIDAS
# ============================================

@login_requerido
def menu(request):
    """Mostrar el menu - Acceso para todos"""
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
    """Gestion de mesas - Solo Admin y Mesero"""
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
            usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
            
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
    print(f"INICIO generar_factura para pedido #{pedido_id}")
    print(f"Metodo HTTP: {request.method}")
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido).select_related('item')
    
    subtotal = sum(detalle.subtotal for detalle in detalles)
    descuento = Decimal('0.00')
    total = subtotal - descuento
    
    # Verificar si ya existe factura
    try:
        factura = Factura.objects.get(pedido=pedido)
        print(f"Ya existe factura #{factura.id}")
    except Factura.DoesNotExist:
        factura = None
        print("No existe factura, se puede crear una nueva")
    
    # PROCESAR PAGO
    if request.method == 'POST' and not factura:
        print("PROCESANDO POST")
        try:
            forma_pago_id = request.POST.get('forma_pago')
            descuento_aplicado = request.POST.get('descuento', '0')
            
            print(f"Forma de pago ID: {forma_pago_id}")
            print(f"Descuento: {descuento_aplicado}")
            
            # Validar forma de pago
            if not forma_pago_id:
                print("ERROR: No se selecciono forma de pago")
                messages.error(request, 'Debe seleccionar una forma de pago')
                context = {
                    'pedido': pedido,
                    'detalles': detalles,
                    'subtotal': subtotal,
                    'descuento': descuento,
                    'total': total,
                    'factura': None,
                    'formas_pago': FormaPago.objects.all(),
                }
                return render(request, 'core/factura.html', context)
            
            # Calcular totales
            try:
                descuento = Decimal(descuento_aplicado)
            except:
                descuento = Decimal('0.00')
            
            total_final = subtotal - descuento
            print(f"Subtotal: ${subtotal}, Descuento: ${descuento}, Total final: ${total_final}")
            
            usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
            
            # CREAR FACTURA
            factura = Factura.objects.create(
                pedido=pedido,
                cliente=pedido.cliente,
                usuario=usuario,
                subtotal=subtotal,
                descuento=descuento,
                total=total_final
            )
            print(f"Factura creada: #{factura.id}")
            
            # Copiar detalles
            for detalle in detalles:
                DetalleFactura.objects.create(
                    factura=factura,
                    item=detalle.item,
                    cantidad=detalle.cantidad,
                    subtotal=detalle.subtotal
                )
            print(f"Detalles copiados: {detalles.count()} items")
            
            # Registrar pago
            forma_pago = FormaPago.objects.get(id=forma_pago_id)
            Pago.objects.create(
                factura=factura,
                forma_pago=forma_pago,
                monto=total_final
            )
            print(f"Pago registrado: {forma_pago.nombre}")
            
            # Cambiar estado del pedido a "Entregado"
            try:
                estado_entregado = Estado.objects.get(nombre='Entregado', tipo_estado__nombre='Pedido')
                pedido.estado = estado_entregado
                pedido.save()
                print(f"Estado cambiado a: {estado_entregado.nombre}")
            except Estado.DoesNotExist:
                print("ADVERTENCIA: No existe estado 'Entregado'")
            
            # Liberar mesa
            if pedido.mesa:
                print(f"Mesa asignada: #{pedido.mesa.id}")
                try:
                    estado_disponible = Estado.objects.get(nombre='Disponible', tipo_estado__nombre='Mesa')
                    mesa_id = pedido.mesa.id
                    pedido.mesa.estado = estado_disponible
                    pedido.mesa.save()
                    print(f"Mesa #{mesa_id} liberada")
                    messages.success(request, f'Mesa {mesa_id} liberada exitosamente')
                except Estado.DoesNotExist:
                    print("ERROR: No existe estado 'Disponible' para mesas")
            else:
                print("No hay mesa asignada")
            
            messages.success(request, f'Pago procesado! Factura #{factura.id} generada. Total: ${total_final}')
            
            # Redirigir segun rol
            rol = request.session.get('usuario_rol')
            print(f"Rol: {rol}")
            
            if rol == 'Cajero':
                print("Redirigiendo a cajero_dashboard")
                return redirect('core:cajero_dashboard')
            elif rol == 'Administrador':
                print("Redirigiendo a admin_dashboard")
                return redirect('core:admin_dashboard')
            else:
                print("Redirigiendo a mesero_dashboard")
                return redirect('core:mesero_dashboard')
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al procesar pago: {str(e)}')
    
    # MOSTRAR FACTURA
    print("Renderizando template")
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


# ============================================
# CAMBIO DE ESTADO DE PEDIDOS
# ============================================

@rol_requerido('Chef')
def cambiar_estado_pedido_chef(request, pedido_id):
    """Chef puede cambiar estado"""
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado_nombre = request.POST.get('nuevo_estado')

        estados_permitidos = ['En preparación', 'Entregado']

        if nuevo_estado_nombre in estados_permitidos:
            try:
                nuevo_estado = Estado.objects.get(
                    nombre=nuevo_estado_nombre,
                    tipo_estado__nombre='Pedido'
                )
                pedido.estado = nuevo_estado
                pedido.save()
                # NO mostrar mensaje para evitar alertas innecesarias
                print(f"Chef cambió estado del pedido #{pedido.id} a {nuevo_estado_nombre}")
            except Estado.DoesNotExist:
                messages.error(request, f'Error: Estado "{nuevo_estado_nombre}" no existe en la base de datos')
        else:
            messages.error(request, f'No tienes permiso para cambiar a ese estado')

    return redirect('core:chef_dashboard')


@rol_requerido('Mesero')
def cambiar_estado_pedido_mesero(request, pedido_id):
    """Mesero puede cambiar estado"""
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado_nombre = request.POST.get('nuevo_estado')
        
        estados_permitidos = ['Pendiente', 'Entregado']
        
        if nuevo_estado_nombre in estados_permitidos:
            try:
                nuevo_estado = Estado.objects.get(
                    nombre=nuevo_estado_nombre,
                    tipo_estado__nombre='Pedido'
                )
                pedido.estado = nuevo_estado
                pedido.save()
                
                if nuevo_estado_nombre == 'Entregado' and pedido.mesa:
                    estado_disponible = Estado.objects.get(nombre='Disponible', tipo_estado__nombre='Mesa')
                    pedido.mesa.estado = estado_disponible
                    pedido.mesa.save()
                
                messages.success(request, f'Pedido #{pedido.id} marcado como {nuevo_estado_nombre}')
            except Estado.DoesNotExist:
                messages.error(request, 'Estado no valido')
        else:
            messages.error(request, 'No tienes permiso para cambiar a ese estado')
    
    return redirect('core:mesero_dashboard')


@rol_requerido('Administrador')
def cambiar_estado_pedido_admin(request, pedido_id):
    """Admin puede cambiar a cualquier estado"""
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado_nombre = request.POST.get('nuevo_estado')
        
        try:
            nuevo_estado = Estado.objects.get(
                nombre=nuevo_estado_nombre,
                tipo_estado__nombre='Pedido'
            )
            pedido.estado = nuevo_estado
            pedido.save()
            
            if nuevo_estado_nombre == 'Entregado' and pedido.mesa:
                estado_disponible = Estado.objects.get(nombre='Disponible', tipo_estado__nombre='Mesa')
                pedido.mesa.estado = estado_disponible
                pedido.mesa.save()
            
            messages.success(request, f'Pedido #{pedido.id} actualizado a {nuevo_estado_nombre}')
        except Estado.DoesNotExist:
            messages.error(request, 'Estado no valido')
    
    return redirect('core:admin_dashboard')