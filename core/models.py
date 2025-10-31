from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    """Manager returning only active (not soft-deleted) records."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Basemodel(models.Model):
    """Abstract model with timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SofDeleteMixin(models.Model):
    """Abstract model with soft delete functionality."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()

    class Meta:
        abstract = True

    def delete(self, using = None, keep_parents = False):
        """Soft delete the record."""
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self, using = None, keep_parents = False):
        """Permanently delete the record from the database."""
        super().delete()
