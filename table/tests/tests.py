import pytest
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from table.models import Table, TableSession
from table.enum import TableStatus, SessionStatus
from table.services import (
    open_session,
    close_session,
    request_assistance,
    resolve_assistance,
    active_session_for_table,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def waiter():
    return User.objects.create_user(username='waiter', password='1234')


@pytest.fixture
def table():
    return Table.objects.create(number='A1')


def test_open_session_sets_table_occupied(table, waiter):
    session = open_session(table.id, waiter)
    table.refresh_from_db()
    assert session.status == SessionStatus.OPEN
    assert table.status == TableStatus.OCCUPIED


def test_only_one_open_session_per_table(table, waiter):
    open_session(table.id, waiter)
    with pytest.raises(ValidationError):
        open_session(table.id, waiter)


def test_close_session_sets_table_free(table, waiter):
    session = open_session(table.id, waiter)
    close_session(session.id, waiter)
    table.refresh_from_db()
    assert table.status == TableStatus.FREE
    session.refresh_from_db()
    assert session.status == SessionStatus.CLOSED
    assert session.closed_at is not None


def test_request_and_resolve_assistance(table, waiter):
    session = open_session(table.id, waiter)
    request_assistance(session.id)
    table.refresh_from_db()
    assert table.status == TableStatus.NEEDS_HELP

    resolve_assistance(session.id)
    table.refresh_from_db()
    assert table.status == TableStatus.OCCUPIED


def test_regenerate_qr_uuid_changes_value(table):
    old_uuid = table.qr_uuid
    table.qr_uuid = uuid4()
    table.save(update_fields=['qr_uuid'])
    table.refresh_from_db()
    assert table.qr_uuid != old_uuid


def test_active_session_for_table_returns_open(table, waiter):
    session = open_session(table.id, waiter)
    assert active_session_for_table(table) == session


def test_guest_qr_resolver_redirects_to_session(client, table, waiter):
    """If an active session exists, guest should be redirected to it."""
    session = open_session(table.id, waiter)
    url = reverse('table:guest-qr-resolver', args=[table.qr_uuid])
    response = client.get(url)
    assert response.status_code == 302
    assert str(session.id) in response['Location']


def test_guest_qr_resolver_shows_waiter_page(client, table):
    """If no active session, render ask_waiter.html."""
    url = reverse('table:guest-qr-resolver', args=[table.qr_uuid])
    response = client.get(url)
    assert response.status_code == 200
    assert b'ask your waiter' in response.content.lower()
