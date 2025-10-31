from django.db import models
from django.templatetags.static import static

from core.models import BaseModel, SoftDeleteMixin


class ItemCategory(BaseModel, SoftDeleteMixin):
    """Represents a group of menu items (e.g., Starters, Drinks)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Item(BaseModel, SoftDeleteMixin):
    """Defines a basic menu item template."""
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    base_unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

    def __str__(self):
        """Show item name + price for clearer admin dropdowns."""
        price = f"S/. {self.base_unit_price:.2f}" if self.base_unit_price else "S/. 0.00"
        return f"{price} — {self.name}"

    @property
    def image_or_default(self):
        if self.image:
            return self.image.url
        if self.category and self.category.name == 'Drinks':
            return static('menu/drinks_default.png')
        return static('menu/dishes_default.png')


class MenuVersion(BaseModel, SoftDeleteMixin):
    """Represents a version of a restaurant menu."""
    name = models.CharField(max_length=150)
    version_no = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} (v{self.version_no})'

    def save(self, *args, **kwargs):
        """Ensure only one active menu version exists."""
        if self.is_active:
            type(self).objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class MenuItem(BaseModel):
    """Specific item included in a given MenuVersion."""
    menu_version = models.ForeignKey(MenuVersion, on_delete=models.CASCADE, related_name='menu_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='menu_items')
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.item.name} ({self.menu_version})'
