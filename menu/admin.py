from django.contrib import admin
from django.utils.html import format_html
from .models import MenuVersion, MenuCategory, MenuItem, Item


class MenuItemInline(admin.TabularInline):
    """Inline for items inside each category."""
    model = MenuItem
    extra = 1
    autocomplete_fields = ['item']
    fields = ('item', 'get_base_price', 'custom_price', 'is_available', 'order')
    readonly_fields = ('get_base_price',)

    def get_base_price(self, obj):
        return obj.item.base_unit_price if obj and obj.item else '-'
    get_base_price.short_description = 'Base Unit Price'


class MenuCategoryInline(admin.StackedInline):
    """Inline for categories inside a menu version, with nested menu items."""
    model = MenuCategory
    extra = 1
    show_change_link = True
    fields = ('name', 'description', 'order')
    inlines = [MenuItemInline]

    # Django doesn't support nested inlines natively, but we simulate this
    # by adding a readonly link to edit MenuItems in a related admin page.
    def get_readonly_fields(self, request, obj=None):
        return ('edit_items_link',) if obj else ()

    def edit_items_link(self, obj):
        if not obj.id:
            return '-'
        return format_html(
            '<a href="/admin/menu/menucategory/{}/change/">Edit Menu Items</a>',
            obj.id
        )
    edit_items_link.short_description = 'Edit Menu Items'


@admin.register(MenuVersion)
class MenuVersionAdmin(admin.ModelAdmin):
    """Top-level admin for managing menu versions."""
    list_display = ('name', 'is_active', 'created_at')
    inlines = [MenuCategoryInline]
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Master catalog of reusable dishes."""
    list_display = ('name', 'base_unit_price', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ['name']


# ❌ Hide MenuCategory and MenuItem from admin index
@admin.register(MenuCategory)
class HiddenMenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_version', 'order')
    inlines = [MenuItemInline]

    def has_module_permission(self, request):
        """Hide the model from the main admin sidebar."""
        return False


@admin.register(MenuItem)
class HiddenMenuItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'menu_category', 'custom_price', 'is_available', 'order')

    def has_module_permission(self, request):
        """Hide the model from the main admin sidebar."""
        return False
