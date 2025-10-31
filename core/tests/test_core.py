import pytest
from django.utils import timezone
from core.models import BaseModel, SoftDeleteMixin


class DummyModel(SoftDeleteMixin, BaseModel):
    """Dummy model for testing."""
    name = 'Test'


@pytest.mark.django_db
def test_base_model_uuid_and_timestamps():
    obj = DummyModel.all_objects.create()
    assert obj.created_at <= timezone.now()
    assert obj.updated_at <= timezone.now()


@pytest.mark.django_db
def test_soft_delete_marks_deleted():
    obj = DummyModel.all_objects.create()
    obj.delete()
    obj.refresh_from_db()
    assert obj.is_deleted is True
    assert obj.deleted_at is not None


@pytest.mark.django_db
def test_active_manager_excludes_deleted():
    active = DummyModel.all_objects.create()
    deleted = DummyModel.all_objects.create()
    deleted.delete()
    results = DummyModel.objects.all()
    assert active in results
    assert deleted not in results
