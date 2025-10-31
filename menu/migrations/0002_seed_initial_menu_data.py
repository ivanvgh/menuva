from django.db import migrations
import uuid


def seed_menu_data(apps, schema_editor):
    MenuVersion = apps.get_model('menu', 'MenuVersion')
    MenuCategory = apps.get_model('menu', 'MenuCategory')
    Item = apps.get_model('menu', 'Item')
    MenuItem = apps.get_model('menu', 'MenuItem')

    # === Crear versión del menú ===
    version = MenuVersion.objects.create(
        id=uuid.uuid4(),
        name='Menú Principal 2025',
        description='Menú principal del restaurante para el año 2025',
        is_active=True,
    )

    # === Crear categorías ===
    entradas = MenuCategory.objects.create(
        menu_version=version,
        name='Entradas',
        description='Platos ligeros para comenzar la comida',
        order=1,
    )
    principales = MenuCategory.objects.create(
        menu_version=version,
        name='Platos Principales',
        description='Platos fuertes y especialidades de la casa',
        order=2,
    )
    postres = MenuCategory.objects.create(
        menu_version=version,
        name='Postres',
        description='Dulces y opciones para cerrar la comida',
        order=3,
    )
    bebidas = MenuCategory.objects.create(
        menu_version=version,
        name='Bebidas',
        description='Refrescos, jugos naturales y bebidas calientes',
        order=4,
    )

    # === Crear platos y bebidas (Items) ===
    items_data = {
        # Entradas
        'Causa Limeña': (16.00, 'Puré de papa amarilla relleno de pollo con mayonesa y palta.'),
        'Tiradito de Pescado': (22.00, 'Láminas de pescado con crema de ají amarillo y limón.'),
        'Papa a la Huancaína': (15.00, 'Papas bañadas en salsa de queso y ají amarillo.'),
        'Tequeños de Queso': (18.00, 'Crujientes tequeños rellenos de queso con guacamole.'),
        'Ensalada César': (14.00, 'Clásica ensalada con pollo a la parrilla y aderezo César.'),

        # Platos Principales
        'Lomo Saltado': (32.00, 'Salteado de carne, cebolla, tomate y papas fritas.'),
        'Ají de Gallina': (28.00, 'Guiso de pollo desmenuzado en crema de ají amarillo.'),
        'Arroz con Mariscos': (34.00, 'Arroz criollo con mariscos, pimientos y especias.'),
        'Tallarines Verdes con Bistec': (30.00, 'Pasta en salsa de albahaca y bistec a la plancha.'),
        'Seco de Cordero': (36.00, 'Guiso de cordero en salsa de culantro con frijoles y arroz.'),

        # Postres
        'Suspiro a la Limeña': (18.00, 'Manjar blanco con merengue al oporto.'),
        'Mazamorra Morada': (12.00, 'Postre tradicional de maíz morado con frutas secas.'),
        'Arroz con Leche': (10.00, 'Arroz dulce con canela, leche y pasas.'),
        'Tarta de Maracuyá': (16.00, 'Tarta con crema de maracuyá y base crocante.'),
        'Helado Artesanal': (14.00, 'Helado casero de vainilla, chocolate o lúcuma.'),

        # Bebidas
        'Chicha Morada': (8.00, 'Refresco tradicional de maíz morado con piña y canela.'),
        'Limonada de Hierbabuena': (9.00, 'Limonada natural con toque de hierbabuena.'),
        'Maracuyá Frozen': (10.00, 'Bebida helada de maracuyá con hielo frappé.'),
        'Pisco Sour': (18.00, 'Cóctel peruano con pisco, limón y clara de huevo.'),
        'Café Americano': (7.00, 'Café negro recién preparado.'),
    }

    item_objs = {
        name: Item.objects.create(
            name=name,
            description=desc,
            base_unit_price=price,
            is_active=True,
        )
        for name, (price, desc) in items_data.items()
    }

    # === Asignar platos y bebidas a categorías ===
    categorias = {
        entradas: [
            'Causa Limeña', 'Tiradito de Pescado', 'Papa a la Huancaína',
            'Tequeños de Queso', 'Ensalada César'
        ],
        principales: [
            'Lomo Saltado', 'Ají de Gallina', 'Arroz con Mariscos',
            'Tallarines Verdes con Bistec', 'Seco de Cordero'
        ],
        postres: [
            'Suspiro a la Limeña', 'Mazamorra Morada', 'Arroz con Leche',
            'Tarta de Maracuyá', 'Helado Artesanal'
        ],
        bebidas: [
            'Chicha Morada', 'Limonada de Hierbabuena', 'Maracuyá Frozen',
            'Pisco Sour', 'Café Americano'
        ],
    }

    for categoria, item_names in categorias.items():
        for order, item_name in enumerate(item_names, start=1):
            MenuItem.objects.create(
                menu_category=categoria,
                item=item_objs[item_name],
                custom_price=None,
                is_available=True,
                order=order,
            )


def remove_menu_data(apps, schema_editor):
    MenuVersion = apps.get_model('menu', 'MenuVersion')
    MenuVersion.objects.filter(name='Menú Principal 2025').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_menu_data, remove_menu_data),
    ]
