from django.shortcuts import render, get_object_or_404
from .models import MenuVersion


def preview_menu(request, version_id=None):
    """Render preview for the active or specified menu version."""
    # Prefetch deeply: categories → menu_items → item
    queryset = MenuVersion.objects.prefetch_related(
        'categories__menu_items__item'
    )

    if version_id:
        menu = get_object_or_404(queryset, pk=version_id)
    else:
        menu = queryset.filter(is_active=True).first()

    return render(request, 'preview.html', {'menu': menu})
