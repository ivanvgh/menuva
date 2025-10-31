from django.db import migrations


def seed_menu_data(apps, schema_editor):
    MenuVersion = apps.get_model('menu', 'MenuVersion')
    MenuCategory = apps.get_model('menu', 'MenuCategory')
    Item = apps.get_model('menu', 'Item')
    MenuItem = apps.get_model('menu', 'MenuItem')

    # Create base menu version
    main_menu = MenuVersion.objects.create(
        name='Main Menu 2025',
        description='Default restaurant menu for 2025',
        is_active=True
    )

    # Create categories
    starters = MenuCategory.objects.create(
        menu_version=main_menu,
        name='Starters',
        description='Appetizers and light dishes to start your meal',
        order=1
    )
    mains = MenuCategory.objects.create(
        menu_version=main_menu,
        name='Mains',
        description='Main course dishes',
        order=2
    )
    sides = MenuCategory.objects.create(
        menu_version=main_menu,
        name='Sides',
        description='Complementary side dishes',
        order=3
    )

    # Create base items
    items_data = [
        ('Greek Salad', 'Fresh salad with feta, olives, and tomatoes.', 5.00),
        ('Tortilla Española', 'Classic Spanish omelette with potatoes.', 4.50),
        ('Olivas Rellenas', 'Stuffed olives with herbs and spices.', 6.00),
        ('Verduras con Olivada', 'Grilled vegetables with olive tapenade.', 6.50),
        ('Lasagne', 'Traditional Italian lasagna with cheese and meat sauce.', 3.00),
        ('Lenguado', 'Pan-fried sole fish with lemon butter.', 12.00),
        ('Bacalao Frito', 'Crispy fried cod fish.', 7.00),
        ('Paella Mixta', 'Traditional mixed paella with seafood and chicken.', 8.50),
        ('Lomo de Salmón', 'Grilled salmon fillet with herbs.', 11.50),
        ('Pollo al Horno', 'Oven-roasted chicken with garlic and thyme.', 8.00),
        ('Fries', 'Crispy golden fries.', 2.00),
        ('Pepper Potatoes', 'Spicy roasted potatoes.', 7.00),
        ('Green Salad', 'Fresh mixed greens.', 2.00),
        ('Coleslaw', 'Creamy cabbage slaw.', 2.00),
        ('Jacket Potato', 'Baked potato with butter.', 4.00),
        ('Onion Rings', 'Crispy fried onion rings.', 3.00),
        ('Fried Beans', 'Fried beans with spices.', 3.00),
    ]

    item_objects = {}
    for name, desc, price in items_data:
        item_objects[name] = Item.objects.create(
            name=name,
            description=desc,
            base_unit_price=price,
            is_active=True
        )

    # Assign menu items by category
    starters_items = ['Greek Salad', 'Tortilla Española', 'Olivas Rellenas', 'Verduras con Olivada', 'Lasagne']
    mains_items = ['Lenguado', 'Bacalao Frito', 'Paella Mixta', 'Lomo de Salmón', 'Pollo al Horno']
    sides_items = ['Fries', 'Pepper Potatoes', 'Green Salad', 'Coleslaw', 'Jacket Potato', 'Onion Rings', 'Fried Beans']

    def create_menu_items(category, item_names):
        for order, name in enumerate(item_names, start=1):
            MenuItem.objects.create(
                menu_category=category,
                item=item_objects[name],
                custom_price=None,  # Use base_unit_price
                is_available=True,
                order=order
            )

    create_menu_items(starters, starters_items)
    create_menu_items(mains, mains_items)
    create_menu_items(sides, sides_items)


def remove_menu_data(apps, schema_editor):
    MenuVersion = apps.get_model('menu', 'MenuVersion')
    MenuVersion.objects.filter(name='Main Menu 2025').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_menu_data, remove_menu_data),
    ]
