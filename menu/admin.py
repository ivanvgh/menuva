import nested_admin
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import MenuVersion, MenuCategory, MenuItem, Item


class MenuItemInline(nested_admin.NestedTabularInline):
    model = MenuItem
    extra = 1
    autocomplete_fields = ['item']
    fields = ('item', 'custom_price', 'is_available', 'order')
    verbose_name_plural = 'Items:'



class MenuCategoryInline(nested_admin.NestedStackedInline):
    model = MenuCategory
    inlines = [MenuItemInline]
    extra = 1
    fields = ('name', 'description', 'order')

    def get_formset(self, request, obj=None, **kwargs):
        """Customize the inline formset headers to show category names."""
        formset = super().get_formset(request, obj, **kwargs)
        formset.verbose_name = 'Category'
        formset.verbose_name_plural = 'Categories'
        return formset



@admin.register(MenuVersion)
class MenuVersionAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'preview_link')
    inlines = [MenuCategoryInline]
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ['-created_at']
    readonly_fields = ('deleted_at',)

    class Media:
        css = {
            'all': ('admin/custom_inline.css',)
        }

    def preview_link(self, obj):
        """Add a link to preview the menu version in list view."""
        url = reverse('menu:preview-version', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Preview</a>', url)

    preview_link.short_description = 'Preview'
    preview_link.allow_tags = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add a Preview button to the top-right action bar in the detail view."""
        extra_context = extra_context or {}
        preview_url = reverse('menu:preview-version', args=[object_id])
        extra_context['preview_url'] = preview_url
        return super().change_view(request, object_id, form_url, extra_context=extra_context)



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
