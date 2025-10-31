from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import UserProfile


# 👇 Add this line to unregister the default UserAdmin first to avoid conflict
#    with the below User & Group Admin registration
admin.site.unregister(User)
admin.site.unregister(Group)

class UserProfileInline(admin.StackedInline):
    """Inline form to edit profile fields from User admin."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fieldsets = ((None, {'fields': ('phone', 'is_deleted', 'created_at', 'updated_at')}),)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Extend the built-in User admin to show roles and profile."""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_groups', 'is_active', 'date_joined')
    list_filter = ('is_active', 'groups')
    search_fields = ('username', 'email')

    def get_groups(self, obj):
        roles = ', '.join(obj.groups.values_list('name', flat=True))
        return roles or '-'
    get_groups.short_description = 'Roles'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Treat Django Groups as system roles."""
    list_display = ('name', 'user_count')
    search_fields = ('name',)

    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Users Assigned'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Direct management of profiles (if needed)."""
    list_display = ('user', 'phone', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('user__username', 'phone')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')
