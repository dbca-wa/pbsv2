from django.contrib.auth.models import (  # Import the built-in User model, which is a sender
    User,
)
from django.db.models.signals import (  # Import a post_save signal when a user is created
    post_save,
)
from django.dispatch import receiver  # Import the receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, "profile") or not instance.profile:
            Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if not hasattr(instance, "profile") or not instance.profile:
        Profile.objects.create(user=instance)
    instance.profile.save()
