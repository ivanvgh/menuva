import io
import zipfile
from uuid import UUID

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.contrib.staticfiles import finders
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.templatetags.static import static
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SquareGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from .models import Table, TableSession
from .enum import TableStatus, SessionStatus


def active_session_for_table(table: Table) -> TableSession | None:
    """Return the currently active (OPEN) session for a table, if any."""
    return TableSession.objects.filter(
        table=table,
        status=SessionStatus.OPEN
    ).first()


def open_session(table_id: int, waiter) -> TableSession:
    """Open a new session for a table. Only one open session is allowed."""
    table = Table.objects.get(pk=table_id)

    if table.status != TableStatus.FREE:
        raise ValidationError(_('Table is not free.'))

    existing_session = active_session_for_table(table)
    if existing_session:
        raise ValidationError(_('There is already an active session for this table.'))

    session = TableSession.objects.create(
        table=table,
        opened_by=waiter,
        status=SessionStatus.OPEN,
    )

    table.status = TableStatus.OCCUPIED
    table.save(update_fields=['status'])

    return session


def close_session(table_id: int, staff) -> TableSession:
    """Close an existing open session and mark the table as free."""
    table = Table.objects.get(pk=table_id)
    session = active_session_for_table(table)

    if session.status != SessionStatus.OPEN:
        raise ValidationError(_('Session is already closed.'))

    session.status = SessionStatus.CLOSED
    session.closed_at = timezone.now()
    session.save(update_fields=['status', 'closed_at'])

    session.table.status = TableStatus.FREE
    session.table.save(update_fields=['status'])

    return session


def request_assistance(session_id: UUID) -> None:
    """Flag a table as needing assistance."""
    session = TableSession.objects.select_related('table').get(pk=session_id)

    if session.status != SessionStatus.OPEN:
        raise ValidationError(_('Cannot request assistance for a closed session.'))

    session.assistance_requested = True
    session.save(update_fields=['assistance_requested'])

    session.table.status = TableStatus.NEEDS_HELP
    session.table.save(update_fields=['status'])


def resolve_assistance(session_id: UUID) -> None:
    """Mark assistance request as resolved and revert table to occupied."""
    session = TableSession.objects.select_related('table').get(pk=session_id)

    if session.status != SessionStatus.OPEN:
        raise ValidationError(_('Cannot resolve assistance for a closed session.'))

    session.assistance_requested = False
    session.save(update_fields=['assistance_requested'])

    session.table.status = TableStatus.OCCUPIED
    session.table.save(update_fields=['status'])


def _measure_text(font, text):
    try:
        x0, y0, x1, y1 = font.getbbox(text)
        return x1 - x0, y1 - y0
    except AttributeError:
        return font.getsize(text)


def _add_logo(qr_img: Image.Image, logo_path: str):
    """Overlay a circular logo at the center of the QR code."""
    try:
        logo = Image.open(logo_path).convert('RGBA')
    except FileNotFoundError:
        return qr_img

    qr_img = qr_img.convert('RGBA')

    # Resize logo to ~20% of QR width
    logo_size = int(qr_img.width * 0.20)
    logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Create circular mask and white border background
    circle_size = logo_size + int(logo_size * 0.35)
    circle = Image.new('RGBA', (circle_size, circle_size), (255, 255, 255, 0))

    draw = ImageDraw.Draw(circle)
    # Outer border (white circle)
    draw.ellipse(
        [(0, 0), (circle_size - 1, circle_size - 1)],
        fill='white'
    )

    # Paste the logo centered on the white circle
    offset = ((circle_size - logo.width) // 2, (circle_size - logo.height) // 2)
    circle.alpha_composite(logo, offset)

    # Paste the circular badge into QR center
    x = (qr_img.width - circle.width) // 2
    y = (qr_img.height - circle.height) // 2
    qr_img.alpha_composite(circle, (x, y))

    return qr_img.convert('RGB')


def generate_qr_image(table, request, logo_path = 'core/static/img/logo.png'):
    """
    Generate a QR with:
    - Label on top
    - Single dark-blue gradient
    - Center logo
    - Rounded modules
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(table.get_qr_url(request))
    qr.make(fit=True)

    # Dark blue gradient color mask
    dark_center = (10, 40, 90)
    dark_edge = (20, 80, 150)

    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SquareGradiantColorMask(
            back_color=(255, 255, 255),
            center_color=dark_center,
            edge_color=dark_edge,
        ),
    ).convert('RGB')

    qr_img = _add_logo(qr_img, logo_path)

    # Label and layout
    label = f'Mesa {table.number}'
    font = ImageFont.truetype('DejaVuSans.ttf', size=42)
    tw, th = _measure_text(font, label)
    pad_x, pad_y = 32, 36

    canvas_w = qr_img.width + pad_x * 2
    canvas_h = th + pad_y * 3 + qr_img.height
    canvas = Image.new('RGB', (canvas_w, canvas_h), 'white')

    draw = ImageDraw.Draw(canvas)
    text_x = (canvas_w - tw) // 2
    text_y = pad_y // 2
    draw.text((text_x, text_y), label, fill='black', font=font)

    qr_x = (canvas_w - qr_img.width) // 2
    qr_y = text_y + th + pad_y
    canvas.paste(qr_img, (qr_x, qr_y))

    return canvas


def generate_qr_zip_response(queryset, request):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for table in queryset:
            img = generate_qr_image(table, request)
            iobuf = io.BytesIO()
            img.save(iobuf, format='PNG')
            zf.writestr(f'mesa_{table.number}.png', iobuf.getvalue())
    buf.seek(0)
    resp = HttpResponse(buf, content_type='application/zip')
    resp['Content-Disposition'] = 'attachment; filename="menuva_qr_codes.zip"'
    return resp