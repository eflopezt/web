"""Vincula nuevos Clientes a su User si el email coincide."""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Cliente


@receiver(post_save, sender=Cliente)
def vincular_usuario_por_email(sender, instance, created, **kwargs):
    if not instance.usuario_id and instance.email:
        User = get_user_model()
        user = User.objects.filter(email__iexact=instance.email).first()
        if user:
            Cliente.objects.filter(pk=instance.pk).update(usuario=user)
