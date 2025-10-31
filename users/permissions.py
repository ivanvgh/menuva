from functools import wraps
from rest_framework.response import Response
from rest_framework import status


# ────────────────────────────────────────────────
# Dynamic Role Utilities
# ────────────────────────────────────────────────
def user_has_role(user, role_name: str) -> bool:
    """Return True if user belongs to the given role (Group)."""
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name__iexact=role_name).exists()


def user_has_any_role(user, *role_names) -> bool:
    """Return True if user belongs to any of the given roles."""
    if not user or not user.is_authenticated:
        return False
    normalized = [r.lower() for r in role_names]
    return user.groups.filter(name__in=normalized).exists()


class RoleChecker:
    """Helper class for clean role checks."""
    def __init__(self, user):
        self.user = user

    def has(self, role_name: str) -> bool:
        return user_has_role(self.user, role_name)

    def any(self, *role_names) -> bool:
        return user_has_any_role(self.user, *role_names)
# ────────────────────────────────────────────────


# ────────────────────────────────────────────────
# Decorator for DRF views
# ────────────────────────────────────────────────
def require_role(*allowed_roles):
    """
    Restrict access to authenticated users in one of the allowed roles.

    Example:
        @require_role('admin')
        @require_role('admin', 'manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated:
                return Response(
                    {'detail': 'Authentication required.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not user.groups.filter(name__in=allowed_roles).exists():
                return Response(
                    {'detail': f'Permission denied. Allowed roles: {", ".join(allowed_roles)}'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
# ────────────────────────────────────────────────


# ────────────────────────────────────────────────
# Optional convenience wrappers
# ────────────────────────────────────────────────
is_admin = lambda u: user_has_role(u, 'admin')
is_guest = lambda u: user_has_role(u, 'guest')
