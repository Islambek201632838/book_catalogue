from django.dispatch import receiver

from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied

from catalogue_app import settings

minutes = settings.login_lock_down
minutes_text = f'{minutes} minute'

if minutes % 10 != 1:
    minutes_text += 's'


@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    raise PermissionDenied(f'Too many failed login attempts. Try {minutes_text} later')
