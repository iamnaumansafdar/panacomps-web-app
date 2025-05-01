from django.contrib.auth.hashers import make_password
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.contrib.auth.models import Group
from panaEstate.models import Building, Metrics


class UserClassification(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class SubscriptionLevel(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class CustomUser(AbstractBaseUser, PermissionsMixin):

    APPROVAL_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    username = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    classification = models.ForeignKey(UserClassification, on_delete=models.CASCADE, null=True, blank=True)
    language_preference = models.CharField(max_length=50, default='English')
    currency_preference = models.CharField(max_length=50, default='USD')
    subscription_level = models.ForeignKey(SubscriptionLevel,
                                    on_delete=models.CASCADE, 
                                    null=True, 
                                    blank=True,)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='pending')

    # required
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


    def get_full_name(self):
        """
        Returns the full name of the user by combining first and last name.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, add_label):
        return True
    

    # def save(self, *args, **kwargs):
    #     # Correct any CustomUser instances that might have an invalid string 'Free' in subscription_level
    #     free_level = SubscriptionLevel.objects.get_or_create(name='Free')[0]
    #     CustomUser.objects.filter(subscription_level='Free').update(subscription_level=free_level)
        
    #     if not self.subscription_level:
    #         self.subscription_level = free_level
        
    #     super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # Hash the password if it's set and not hashed already
    #     if self.password and not self.password.startswith("pbkdf2_sha256$"):
    #         self.password = make_password(self.password)
    #     super(User, self).save(*args, **kwargs)


@receiver(post_save, sender=CustomUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    record_limit = models.PositiveIntegerField(null=True, blank=True)  # Set to None for no limit
    can_download_summary_excel = models.BooleanField(default=False)
    can_download_detailed_excel = models.BooleanField(default=False)
    can_download_pdf = models.BooleanField(default=False)
    can_view_detail = models.BooleanField(default=False)
    can_view_history = models.BooleanField(default=False)
    accessible_buildings = models.ManyToManyField(Metrics, blank=True)
    enable_ai_analysis = models.BooleanField(default=False)
    # access_all_buildings = models.BooleanField(default=False)

    def __str__(self):
        return self.group.name