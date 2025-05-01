from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import GroupProfile
from django.db.models.signals import post_delete

@receiver(post_save, sender=Group)
def create_or_update_group_profile(sender, instance, created, **kwargs):
    if created:
        GroupProfile.objects.create(group=instance)
    else:
        # Update GroupProfile if needed
        GroupProfile.objects.update_or_create(group=instance)


@receiver(post_delete, sender=Group)
def delete_group_profile(sender, instance, **kwargs):
    try:
        group_profile = GroupProfile.objects.get(group=instance)
        group_profile.delete()
    except GroupProfile.DoesNotExist:
        pass