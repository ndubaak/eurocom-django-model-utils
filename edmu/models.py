from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _

from uuidfield import UUIDField


class UUIDModel(models.Model):
    """
    An abstract base class model that provides a UUID field as it's primary key..
    """
    uuid = UUIDField(name=_('uuid'), primary_key=True, auto=True)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating ``date_created`` and ``date_updated`` fields.
    """
    date_created = models.DateTimeField(_('date created'), default=datetime.now)
    date_updated = models.DateTimeField(_('date updated'), auto_now=True)

    class Meta:
        abstract = True


class UserStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating ``created_by`` and ``updated_by`` fields. To be able to
    save the user's information in the the ``created_by`` and ``updated_by`` fields, the ``user`` argument must be
    set when instantiating the class.

    To user ``UserStampedModel``, the user model needs to be passed in the ``save`` method via ``user``.
    """
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('created by'),
                                   related_name='%(app_label)s_%(class)s_created_by')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('updated by'),
                                   related_name='%(app_label)s_%(class)s_updated_by')

    class Meta:
        abstract = True


class UserTimeStampedModel(TimeStampedModel, UserStampedModel):
    """
    An abstract base class model that provides self-updating ``date_created``, ``date_updated``, ``created_by`` and
    ``updated_by`` fields. To be able to save the user's information in the the ``created_by`` and ``updated_by``
    fields, the ``user`` argument must be set when instantiating the class.
    """
    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """
    An abstract model that allows objects to be ordered relative to each other.
    Provides an ``order`` field.
    """
    order = models.PositiveIntegerField(editable=False, db_index=True)

    class Meta:
        abstract = True
        ordering = ('order',)

    def save(self, *args, **kwargs):
        if not self.pk:
            c = self.__class__.objects.all().aggregate(Max('order')).get('order__max')
            self.order = c and c + 1 or 0
        super(OrderedModel, self).save(*args, **kwargs)

    def _move(self, up, qs=None):
        if qs is None:
            qs = self.__class__._default_manager

        if up:
            qs = qs.order_by('-order').filter(order__lt=self.order)
        else:
            qs = qs.filter(order__gt=self.order)
        try:
            replacement = qs[0]
        except IndexError:
            # already first/last
            return
        self.order, replacement.order = replacement.order, self.order
        self.save()
        replacement.save()

    def move(self, direction, qs=None):
        self._move(direction == 'up', qs)

    def move_down(self):
        """
        Move this object down one position.
        """
        return self._move(up=False)

    def move_up(self):
        """
        Move this object up one position.
        """
        return self._move(up=True)
