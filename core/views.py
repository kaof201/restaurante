from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from .models import (
    Item, Categoria, Mesa, Pedido, DetallePedido,
    Factura, DetalleFactura, Cliente, Usuario, Estado, 
    TipoPedido, FormaPago, Pago
)
from decimal import Decimal

def index(request):
    """Página principal - Dashboard"""
    # Estadísticas
    total_mesas = Mesa.objects.count()
    mesas_disponibles = Mesa.objects.filter(estado__nombre='Disponible').count()
    
    pedidos_activos = Pedido.objects.filter(
        estado__nombre__in=['Pendiente', 'En Preparación']
    ).count()
    
    items_disponibles = Item.objects.filter(
        estado__nombre='Disponible'
    ).count()
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.all().select_related(
        'cliente', 'mesa', 'estado', 'usuario'
    ).order_by('-fecha')[:5]
    
    context = {
        'total_mesas': total_mesas,
        'mesas_disponibles': mesas_disponibles,
        'pedidos_activos': pedidos_activos,
        'items_disponibles': items_disponibles,
        'pedidos_recientes': pedidos_recientes,
    }
    return render(request, 'core/index.html', context)


def menu(request):
    """Mostrar el menú de items"""
    categorias = Categoria.objects.all()
    items = Item.objects.filter(estado__nombre='Disponible').select_related(
        'categoria', 'tipo_item', 'estado'
    )
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        items = items.filter(categoria_id=categoria_id)
    
    context = {
        'categorias': categorias,
        'items': items,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
    }
    return render(request, 'core/menu.html', context)


def mesas(request):
    """Gestión de mesas"""
    mesas_list = Mesa.objects.all().select_related('estado')
    
    # Contar por estado
    disponibles = mesas_list.filter(estado__nombre='Disponible').count()
    ocupadas = mesas_list.filter(estado__nombre='Ocupada').count()
    
    context = {
        'mesas': mesas_list,
        'total_mesas': mesas_list.count(),
        'disponibles': disponibles,
        'ocupadas': ocupadas,
    }
    return render(request, 'core/mesas.html', context)


def pedidos(request):
    """Lista de pedidos"""
    pedidos_list = Pedido.objects.all().select_related(
        'cliente', 'mesa', 'estado', 'usuario', 'tipo_pedido'
    ).prefetch_related('detallepedido_set__item').order_by('-fecha')
    
    # Filtros
    estado_filter = request.GET.get('estado')
    if estado_filter:
        pedidos_list = pedidos_list.filter(estado__nombre=estado_filter)
    
    context = {
        'pedidos': pedidos_list,
        'estados': Estado.objects.filter(tipo_estado__nombre='Pedido'),
    }
    return render(request, 'core/pedidos.html', context)


def crear_pedido(request):
    """Crear un nuevo pedido"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cliente_id = request.POST.get('cliente_id')
            mesa_id = request.POST.get('mesa_id')
            tipo_pedido_id = request.POST.get('tipo_pedido_id')
            items_ids = request.POST.getlist('items[]')
            cantidades = request.POST.getlist('cantidades[]')
            
            # Validaciones
            if not items_ids or not cantidades:
                messages.error(request, 'Debes agregar al menos un item al pedido')
                return redirect('core:crear_pedido')
            
            # Obtener objetos necesarios
            cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None
            mesa = Mesa.objects.get(id=mesa_id) if mesa_id else None
            
            # Obtener o crear estado "Pendiente"
            estado, created = Estado.objects.get_or_create(
                nombre='Pendiente',
                defaults={'tipo_estado': None}  # Ajustar según tu modelo
            )
            
            tipo_pedido = TipoPedido.objects.get(id=tipo_pedido_id)
            
            # Obtener primer usuario (deberías usar request.user en producción)
            usuario = Usuario.objects.first()
            
            if not usuario:
                messages.error(request, 'No hay usuarios registrados en el sistema')
                return redirect('core:crear_pedido')
            
            # Crear pedido
            pedido = Pedido.objects.create(
                cliente=cliente,
                mesa=mesa,
                estado=estado,
                tipo_pedido=tipo_pedido,
                usuario=usuario
            )
            
            # Crear detalles del pedido
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
            
            # Si hay mesa, cambiar su estado a ocupada
            if mesa:
                estado_ocupada = Estado.objects.filter(nombre='Ocupada').first()
                if estado_ocupada:
                    mesa.estado = estado_ocupada
                    mesa.save()
            
            messages.success(request, f'Pedido #{pedido.id} creado exitosamente. Total: ${total_pedido}')
            return redirect('core:pedidos')
            
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado')
        except Mesa.DoesNotExist:
            messages.error(request, 'Mesa no encontrada')
        except TipoPedido.DoesNotExist:
            messages.error(request, 'Tipo de pedido no encontrado')
        except Item.DoesNotExist:
            messages.error(request, 'Uno o más items no fueron encontrados')
        except Exception as e:
            messages.error(request, f'Error al crear pedido: {str(e)}')
    
    # GET request
    context = {
        'clientes': Cliente.objects.all(),
        'mesas': Mesa.objects.filter(estado__nombre='Disponible'),
        'items': Item.objects.filter(estado__nombre='Disponible').select_related('categoria'),
        'tipos_pedido': TipoPedido.objects.all(),
        'categorias': Categoria.objects.all(),
    }
    return render(request, 'core/crear_pedido.html', context)


def generar_factura(request, pedido_id):
    """Generar factura para un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido).select_related('item')
    
    # Calcular totales
    subtotal = sum(detalle.subtotal for detalle in detalles)
    descuento = Decimal('0.00')  # Puedes agregar lógica de descuentos
    total = subtotal - descuento
    
    # Verificar si ya existe factura
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