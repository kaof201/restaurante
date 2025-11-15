from django.core.management.base import BaseCommand
from core.models import (
    Rol, TipoEstado, Estado, Categoria, TipoItem, 
    Item, Mesa, TipoPedido, FormaPago
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema de restaurante'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos existentes antes de cargar nuevos datos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('⚠️  Eliminando datos existentes...')
            )
            Item.objects.all().delete()
            Mesa.objects.all().delete()
            Estado.objects.all().delete()
            TipoEstado.objects.all().delete()
            Categoria.objects.all().delete()
            TipoItem.objects.all().delete()
            TipoPedido.objects.all().delete()
            FormaPago.objects.all().delete()
            Rol.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('✅ Datos eliminados correctamente')
            )

        # ====================================================
        # ROLES
        # ====================================================
        self.stdout.write('\n👥 Creando roles...')
        roles_data = ['Administrador', 'Mesero', 'Chef', 'Cajero']
        for rol_nombre in roles_data:
            rol, created = Rol.objects.get_or_create(nombre=rol_nombre)
            status = '✨' if created else '♻️'
            self.stdout.write(f'  {status} {rol_nombre}')

        # ====================================================
        # TIPOS DE ESTADO
        # ====================================================
        self.stdout.write('\n📋 Creando tipos de estado...')
        tipos_estado_data = ['Mesa', 'Pedido', 'Item']
        tipos_estado = {}
        for tipo_nombre in tipos_estado_data:
            tipo, created = TipoEstado.objects.get_or_create(nombre=tipo_nombre)
            tipos_estado[tipo_nombre] = tipo
            status = '✨' if created else '♻️'
            self.stdout.write(f'  {status} {tipo_nombre}')

        # ====================================================
        # ESTADOS
        # ====================================================
        self.stdout.write('\n🔄 Creando estados...')
        estados_data = [
            {'nombre': 'Disponible', 'tipo': 'Mesa'},
            {'nombre': 'Ocupada', 'tipo': 'Mesa'},
            {'nombre': 'Pendiente', 'tipo': 'Pedido'},
            {'nombre': 'En preparación', 'tipo': 'Pedido'},
            {'nombre': 'Entregado', 'tipo': 'Pedido'},
            {'nombre': 'Activo', 'tipo': 'Item'},
        ]
        estados = {}
        for estado_data in estados_data:
            estado, created = Estado.objects.get_or_create(
                nombre=estado_data['nombre'],
                defaults={'tipo_estado': tipos_estado[estado_data['tipo']]}
            )
            estados[estado_data['nombre']] = estado
            status = '✨' if created else '♻️'
            self.stdout.write(f'  {status} {estado_data["nombre"]} ({estado_data["tipo"]})')

        # ====================================================
        # CATEGORÍAS
        # ====================================================
        self.stdout.write('\n🍽️  Creando categorías...')
        categorias_data = ['Bebidas', 'Platos Fuertes', 'Entradas', 'Postres']
        categorias = {}
        for cat_nombre in categorias_data:
            cat, created = Categoria.objects.get_or_create(nombre=cat_nombre)
            categorias[cat_nombre] = cat
            status = '✨' if created else '♻️'
            self.stdout.write(f'  {status} {cat_nombre}')

        # ====================================================
        # TIPOS DE ITEM
        # ====================================================
        self.stdout.write('\n📦 Creando tipos de ítem...')
        tipos_item_data = ['Comida', 'Bebida']
        tipos_item = {}
        for tipo_nombre in tipos_item_data:
            tipo, created = TipoItem.objects.get_or_create(nombre=tipo_nombre)
            tipos_item[tipo_nombre] = tipo
            status = '✨' if created else '♻️'
            self.stdout.write(f'  {status} {tipo_nombre}')

        # ====================================================
        # ITEMS / PRODUCTOS
        # ====================================================
        self.stdout.write('\n🍕 Creando ítems del menú...')
        items_data = [
            {
                'nombre': 'Coca Cola',
                'descripcion': 'Bebida gaseosa 350ml',
                'precio': Decimal('2.50'),
                'costo': Decimal('1.00'),
                'stock': 100,
                'categoria': 'Bebidas',
                'tipo_item': 'Bebida',
            },
            {
                'nombre': 'Jugo Natural de Naranja',
                'descripcion': 'Jugo de naranja natural 500ml',
                'precio': Decimal('3.50'),
                'costo': Decimal('1.50'),
                'stock': 50,
                'categoria': 'Bebidas',
                'tipo_item': 'Bebida',
            },
            {
                'nombre': 'Bandeja Paisa',
                'descripcion': 'Plato típico colombiano con carne, chicharrón, arroz, frijoles, huevo, aguacate y plátano',
                'precio': Decimal('18.00'),
                'costo': Decimal('8.00'),
                'stock': 30,
                'categoria': 'Platos Fuertes',
                'tipo_item': 'Comida',
            },
            {
                'nombre': 'Ajiaco Santafereño',
                'descripcion': 'Sopa típica con pollo, tres tipos de papa, mazorca y alcaparras',
                'precio': Decimal('12.00'),
                'costo': Decimal('5.00'),
                'stock': 25,
                'categoria': 'Platos Fuertes',
                'tipo_item': 'Comida',
            },
            {
                'nombre': 'Empanadas de Carne',
                'descripcion': '3 unidades de empanadas colombianas con carne',
                'precio': Decimal('4.50'),
                'costo': Decimal('2.00'),
                'stock': 60,
                'categoria': 'Entradas',
                'tipo_item': 'Comida',
            },
            {
                'nombre': 'Patacones con Hogao',
                'descripcion': 'Plátano verde frito con hogao',
                'precio': Decimal('5.00'),
                'costo': Decimal('2.50'),
                'stock': 40,
                'categoria': 'Entradas',
                'tipo_item': 'Comida',
            },
            {
                'nombre': 'Tres Leches',
                'descripcion': 'Pastel de tres leches tradicional',
                'precio': Decimal('5.50'),
                'costo': Decimal('2.00'),
                'stock': 20,
                'categoria': 'Postres',
                'tipo_item': 'Comida',
            },
            {
                'nombre': 'Flan de Caramelo',
                'descripcion': 'Flan casero con caramelo',
                'precio': Decimal('4.00'),
                'costo': Decimal('1.50'),
                'stock': 25,
                'categoria': 'Postres',
                'tipo_item': 'Comida',
            },
        ]

        items_created = 0
        items_existed = 0
        for item_data in items_data:
            categoria_nombre = item_data.pop('categoria')
            tipo_item_nombre = item_data.pop('tipo_item')
            
            item, created = Item.objects.get_or_create(
                nombre=item_data['nombre'],
                defaults={
                    **item_data,
                    'categoria': categorias[categoria_nombre],
                    'tipo_item': tipos_item[tipo_item_nombre],
                    'estado': estados['Activo'],
                    'imagen': '',
                }
            )
            
            if created:
                items_created += 1
                self.stdout.write(f'  ✨ {item.nombre} - ${item.precio}')
            else:
                items_existed += 1
                self.stdout.write(f'  ♻️  {item.nombre}')

        # ====================================================
        # MESAS
        # ====================================================
        self.stdout.write('\n🪑 Creando mesas...')
        mesas_data = [4, 2, 6, 4, 8]
        mesas_created = 0
        for capacidad in mesas_data:
            mesa, created = Mesa.objects.get_or_create(
                capacidad=capacidad,
                estado=estados['Disponible']
            )
            if created:
                mesas_created += 1
                self.stdout.write(f'  ✨ Mesa para {capacidad} personas')

        # ====================================================
        # TIPOS DE PEDIDO
        # ====================================================
        self.stdout.write('\n📝 Creando tipos de pedido...')
        tipos_pedido_data = ['Para Mesa', 'Para Llevar', 'Domicilio']
        for tipo_nombre in tipos_pedido_data:
            tipo, created = TipoPedido.objects.get_or_create(nombre=tipo_nombre)
            status = '✨' if created else '♻️'
            self.stdout.write(f'  {status} {tipo_nombre}')

        # ====================================================
        # FORMAS DE PAGO
        # ====================================================
        self.stdout.write('\n💳 Creando formas de pago...')
        formas_pago_data = ['Efectivo', 'Tarjeta de Crédito', 'Tarjeta de Débito', 'Transferencia']
        for forma_nombre in formas_pago_data:
            forma, created = FormaPago.objects.get_or_create(nombre=forma_nombre)
            status = '✨' if created else '♻️'
            self.stdout.write(f'  {status} {forma_nombre}')

        # ====================================================
        # RESUMEN FINAL
        # ====================================================
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('\n🎉 ¡Sistema de restaurante configurado exitosamente!\n')
        )
        self.stdout.write('📊 Resumen:')
        self.stdout.write(f'   • Roles: {len(roles_data)}')
        self.stdout.write(f'   • Categorías: {len(categorias_data)}')
        self.stdout.write(f'   • Ítems del menú: {items_created} creados, {items_existed} existían')
        self.stdout.write(f'   • Mesas: {mesas_created if mesas_created > 0 else len(mesas_data)}')
        self.stdout.write(f'   • Tipos de pedido: {len(tipos_pedido_data)}')
        self.stdout.write(f'   • Formas de pago: {len(formas_pago_data)}')
        self.stdout.write('='*60 + '\n')