import pytest
from django.urls import reverse
from menu.models import ItemCategory, Item, MenuVersion, MenuItem


@pytest.mark.django_db
def test_menu_version_activation(client, admin_user):
    version1 = MenuVersion.objects.create(name='Main', version_no=1)
    version2 = MenuVersion.objects.create(name='New', version_no=2, is_active=True)
    version1.is_active = True
    version1.save()

    assert MenuVersion.objects.filter(is_active=True).count() == 1
    assert MenuVersion.objects.get(is_active=True) == version1


@pytest.mark.django_db
def test_clone_menu_creates_new_version_and_items():
    cat = ItemCategory.objects.create(name='Drinks')
    item = Item.objects.create(name='Coke', base_unit_price=10, category=cat)
    version = MenuVersion.objects.create(name='Main', version_no=1)
    MenuItem.objects.create(
        menu_version=version, item=item, name=item.name,
        description='Cold', unit_price=10, category=cat
    )

    # Clone manually (simulate admin action)
    new_version = MenuVersion.objects.create(
        name=f'{version.name} Copy', version_no=version.version_no + 1, is_active=False
    )
    for mi in version.menu_items.all():
        MenuItem.objects.create(
            menu_version=new_version,
            item=mi.item,
            name=mi.name,
            description=mi.description,
            unit_price=mi.unit_price,
            category=mi.category,
        )

    assert MenuVersion.objects.count() == 2
    assert MenuItem.objects.filter(menu_version=new_version).count() == 1


@pytest.mark.django_db
def test_preview_menu_renders_active_menu(client, admin_user):
    cat = ItemCategory.objects.create(name='Desserts')
    item = Item.objects.create(name='Cake', base_unit_price=12, category=cat)
    version = MenuVersion.objects.create(name='Menu 1', version_no=1, is_active=True)
    MenuItem.objects.create(
        menu_version=version, item=item, name=item.name,
        description='Sweet', unit_price=12, category=cat
    )

    client.force_login(admin_user)
    url = reverse('menu:preview')
    response = client.get(url)

    assert response.status_code == 200
    assert b'Preview Active Menu' in response.content
    assert b'Cake' in response.content
