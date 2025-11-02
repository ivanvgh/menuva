import pytest
from django.templatetags.static import static
from django.urls import reverse
from menu.models import MenuVersion, MenuCategory, Item, MenuItem


@pytest.mark.django_db
def test_menu_version_activation():
    MenuVersion.objects.all().delete()
    v1 = MenuVersion.objects.create(name='Version 1', is_active=False)
    v2 = MenuVersion.objects.create(name='Version 2', is_active=True)

    # Activate v1
    v1.is_active = True
    v1.save()

    active_versions = MenuVersion.objects.filter(is_active=True)
    assert active_versions.count() == 1
    assert active_versions.first() == v1
    assert not MenuVersion.objects.filter(pk=v2.pk, is_active=True).exists()


@pytest.mark.django_db
def test_clone_menu_version_with_items():
    MenuVersion.objects.all().delete()
    version = MenuVersion.objects.create(name='Main', is_active=True)
    category = MenuCategory.objects.create(menu_version=version, name='Drinks')
    item = Item.objects.create(name='Coke', base_unit_price=10)

    MenuItem.objects.create(menu_category=category, item=item, custom_price=12)

    # Clone menu manually (simulate an admin clone action)
    new_version = MenuVersion.objects.create(name='Main Copy', is_active=False)
    for cat in version.categories.all():
        new_cat = MenuCategory.objects.create(
            menu_version=new_version,
            name=cat.name,
            description=cat.description,
            order=cat.order,
        )
        for mi in cat.menu_items.all():
            MenuItem.objects.create(
                menu_category=new_cat,
                item=mi.item,
                custom_price=mi.custom_price,
                is_available=mi.is_available,
                order=mi.order,
            )

    assert MenuVersion.objects.count() == 2
    assert MenuCategory.objects.filter(menu_version=new_version).count() == 1
    assert MenuItem.objects.filter(menu_category__menu_version=new_version).count() == 1


@pytest.mark.django_db
def test_menuitem_final_price_and_image_default(settings):
    item = Item.objects.create(name='Burger', base_unit_price=15)
    version = MenuVersion.objects.create(name='Test Menu')
    cat = MenuCategory.objects.create(menu_version=version, name='Mains')

    mi = MenuItem.objects.create(menu_category=cat, item=item, custom_price=None)
    assert mi.final_price == 15

    mi.custom_price = 18
    mi.save()
    assert mi.final_price == 18

    assert mi.image_or_default == static('menu/default-dish.png')


@pytest.mark.django_db
def test_menuitem_str_representation():
    version = MenuVersion.objects.create(name='Lunch Menu')
    cat = MenuCategory.objects.create(menu_version=version, name='Starters')
    item = Item.objects.create(name='Soup', base_unit_price=8)

    mi = MenuItem.objects.create(menu_category=cat, item=item)
    assert str(mi) == 'Soup (Starters)'


@pytest.mark.django_db
def test_preview_menu_view(client, admin_user):
    """Test that the preview page for the active menu loads correctly."""
    version = MenuVersion.objects.create(name='Active Menu', is_active=True)
    cat = MenuCategory.objects.create(menu_version=version, name='Desserts')
    item = Item.objects.create(name='Cake', base_unit_price=12)
    MenuItem.objects.create(menu_category=cat, item=item, custom_price=14)

    client.force_login(admin_user)
    url = reverse('menu:preview-version', args=[version.id])
    response = client.get(url)

    assert response.status_code == 200
    assert b'Active Menu' in response.content
    assert b'Cake' in response.content
