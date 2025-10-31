from django.shortcuts import render, get_object_or_404
from .models import MenuVersion

def preview_menu(request, version_id=None):
    """Render preview for the active or specified menu version."""
    if version_id:
        menu = get_object_or_404(MenuVersion.objects.prefetch_related('categories__menu_items__item'), pk=version_id)
    else:
        menu = MenuVersion.objects.filter(is_active=True).prefetch_related('categories__menu_items__item').first()

    return render(request, 'preview.html', {'menu': menu})
