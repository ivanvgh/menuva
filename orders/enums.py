from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    QUEUED = "QUEUED", _("Queued")
    PREPARING = "PREPARING", _("Preparing")
    READY = "READY", _("Ready")
    SERVED = "SERVED", _("Served")
    CANCELED = "CANCELED", _("Canceled")


class OrderItemStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    ORDERED = "ORDERED", _("Ordered")
    DELIVERED = "DELIVERED", _("Delivered")


TAX_RATE = Decimal("0.18")
