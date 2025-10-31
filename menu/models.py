from django.db import models


class MenuVersion(models.Model):
    """Represents a version of the menu (e.g. Summer 2025 Menu)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'menu_version'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class MenuCategory(models.Model):
    """Represents a section within a menu version (e.g. Starters, Mains, Sides)."""
    menu_version = models.ForeignKey(
        MenuVersion,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'menu_category'
        ordering = ['order']

    def __str__(self):
        return f'{self.name} ({self.menu_version.name})'


class Item(models.Model):
    """Represents a master dish item that can appear in multiple menus."""
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    base_unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'item'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Represents an item in a specific menu category (linked to a master item)."""
    menu_category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    custom_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'menu_item'
        ordering = ['order']

    def __str__(self):
        return f'{self.item.name} ({self.menu_category.name})'

    @property
    def final_price(self):
        """Returns the effective price for display (custom or base)."""
        return self.custom_price or self.item.base_unit_price
