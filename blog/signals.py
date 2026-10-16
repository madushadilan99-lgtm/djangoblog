import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Post


@receiver(post_delete, sender=Post)
def delete_post_cover_on_delete(sender, instance, **kwargs):
    if instance.cover_image:
        if os.path.isfile(instance.cover_image.path):
            os.remove(instance.cover_image.path)