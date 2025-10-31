from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import MenuVersion, MenuItem


@method_decorator(staff_member_required, name='dispatch')
class PreviewMenuView(TemplateView):
    template_name = 'preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        version_id = self.kwargs.get('pk')
        if version_id:
            # ✅ Show the specific version being requested
            active_menu = get_object_or_404(MenuVersion, pk=version_id)
        else:
            # fallback to the currently active version
            active_menu = MenuVersion.objects.filter(is_active=True).first()

        if active_menu:
            items = (
                MenuItem.objects.filter(menu_version=active_menu)
                .select_related('item__category')
                .order_by('item__category__name', 'item__name')
            )
            grouped = {}
            for item in items:
                grouped.setdefault(item.item.category.name, []).append(item)
            context['active_menu'] = active_menu
            context['grouped_items'] = grouped
        else:
            context['active_menu'] = None
            context['grouped_items'] = {}

        return context
