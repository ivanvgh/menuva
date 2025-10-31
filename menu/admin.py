from django.contrib import admin, messages
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import ItemCategory, Item, MenuVersion, MenuItem


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Deletion info', {'fields': ('deleted_at',)}),
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_unit_price', 'thumbnail', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('deleted_at',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="40" style="object-fit:cover;border-radius:4px;">',
                obj.image_or_default
            )
        return '-'

    thumbnail.short_description = 'Image'

    def get_search_results(self, request, queryset, search_term):
        """
        Extend default search to include base_unit_price in the JSON response
        for autocomplete_fields.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # attach price as additional metadata
        results = []
        for item in queryset:
            results.append({
                'id': item.pk,
                'text': str(item),
                'base_price': float(item.base_unit_price),
            })
        return queryset, use_distinct


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('item__name', 'menu_version', 'unit_price', 'created_at')
    list_filter = ('menu_version',)


# ---- MenuVersion Admin ----
@admin.action(description='Activate selected menu')
def activate_menu(modeladmin, request, queryset):
    if not queryset.exists():
        messages.error(request, 'No menu selected.')
        return
    MenuVersion.objects.update(is_active=False)
    version = queryset.first()
    version.is_active = True
    version.save()
    messages.success(request, f'Menu "{version.name}" activated.')


@admin.action(description='Clone selected menu')
def clone_menu(modeladmin, request, queryset):
    if not queryset.exists():
        messages.error(request, 'No menu selected.')
        return

    version = queryset.first()
    new_version = MenuVersion.objects.create(
        name=f'{version.name} Copy',
        version_no=version.version_no + 1,
        is_active=False,
    )
    for item in version.menu_items.all():
        MenuItem.objects.create(
            menu_version=new_version,
            item=item.item,
            unit_price=item.unit_price,
            category=item.category,
        )
    messages.success(request, f'Menu "{version.name}" cloned → "{new_version.name}".')

# ---- Inline setup ----
class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ('item', 'unit_price',)
    autocomplete_fields = ('item',)
    ordering = ('item__category__name', 'item__name')

    class Media:
        js = ('admin/js/menuitem_autofill.js',)  # JS autofills price when item picked

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Disable add/edit/delete icons for related Item."""
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'item':
            widget = formfield.widget
            if isinstance(widget, RelatedFieldWidgetWrapper):
                widget.can_add_related = False
                widget.can_change_related = False
                widget.can_delete_related = False
                widget.can_view_related = False
        return formfield


@admin.register(MenuVersion)
class MenuVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'version_no', 'is_active', 'created_at', 'preview_link')
    actions = [activate_menu, clone_menu]
    inlines = [MenuItemInline]  # ✅ allows inline editing of MenuItems
    readonly_fields = ('deleted_at',)
    fieldsets = (
        (None, {'fields': ( 'name', 'version_no', 'is_active')}),
        ('Deletion info', {'fields': ('deleted_at',)}),
    )

    def preview_link(self, obj):
        url = reverse('menu:preview', args=[obj.pk])  # ✅ now links to that version
        return format_html(
            '<a class="button" href="{}" target="_blank" '
            'style="padding:4px 8px;background:#007bff;'
            'color:white;border-radius:10px;text-decoration:none;">Preview</a>',
            url,
        )
    preview_link.short_description = 'Preview'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Injects preview URL into the change form template context."""
        extra_context = extra_context or {}
        try:
            preview_url = reverse('menu:preview', args=[object_id])
            extra_context['preview_url'] = preview_url
        except Exception:
            extra_context['preview_url'] = None

        return super().change_view(request, object_id, form_url, extra_context=extra_context)
