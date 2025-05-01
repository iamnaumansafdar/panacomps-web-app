from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SubscriptionLevel, GroupProfile, UserClassification
from panaEstate.models import Building, Metrics
from django.utils.translation import gettext, gettext_lazy as _
from django.conf import settings
from django.core.mail import send_mail
from django import forms
from django.db.models import Count


@admin.register(UserClassification)
class UserClassificationAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SubscriptionLevel)
class SubscriptionLevelAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.action(description='Approve selected users')
def approve_users(modeladmin, request, queryset):
    for user in queryset:
        if user.approval_status != 'approved':
            user.approval_status = 'approved'
            user.is_active = True
            user.save()

            # Send approval email
            send_mail(
                'Account Approved',
                'Your account has been approved. You can now log in.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )

@admin.action(description='Reject selected users')
def reject_users(modeladmin, request, queryset):
    for user in queryset:
        if user.approval_status != 'rejected':
            user.approval_status = 'rejected'
            user.is_active = False
            user.save()

            # Send rejection email
            send_mail(
                'Account Rejected',
                'Your account registration has been rejected.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )



class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "username",  
        "first_name",
        "last_name",
        "classification",
        "subscription_level",
        "last_login",
        "date_joined",
        "is_active",
        'approval_status',
    )
    actions = [approve_users, reject_users]
    list_display_links = (
        "email",
        "username", 
        "first_name",
        "last_name",
    )
    readonly_fields = ("last_login", "date_joined")
    ordering = ("classification", "username")
    # ordering = ("-date_joined",)

    filter_horizontal = ()
    list_filter = ("classification", "subscription_level", "groups", "is_active", "is_staff", "is_superuser")
    # list_per_page = 25
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username',  'address', 'country', 'approval_status', 'classification', 'language_preference', 'currency_preference', 'subscription_level')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'classification'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_superuser:
             administrator_classification, created = UserClassification.objects.get_or_create(name='Administrator')
             obj.classification = administrator_classification
            # obj.classification = 'Administrator'
        super().save_model(request, obj, form, change)

# Register your CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)


# class GroupProfileAdmin(admin.ModelAdmin):
#     list_display = ('group', 'record_limit', 'can_download_summary_excel', 'can_download_detailed_excel', 'can_download_pdf', 'can_view_detail', 'can_view_history', 'access_all_buildings')
#     list_filter = ('group',)
#     filter_horizontal = ('accessible_buildings',)

#     fieldsets = (
#         (None, {
#             'fields': ('group', 'record_limit', 'access_all_buildings')
#         }),
#         ('Permissions', {
#             'fields': ('can_download_summary_excel', 'can_download_detailed_excel', 'can_download_pdf', 'can_view_detail', 'can_view_history')
#         }),
#         ('Buildings Access', {
#             'fields': ('accessible_buildings',)
#         }),
#     )

# admin.site.register(GroupProfile, GroupProfileAdmin)

class GroupProfileForm(forms.ModelForm):
    class Meta:
        model = GroupProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GroupProfileForm, self).__init__(*args, **kwargs)
        # Customize the accessible_buildings field to show only distinct building names
        buildings = set()
        unique_metrics = []
        for metric in Metrics.objects.all():
            if metric.edificio not in buildings:
                unique_metrics.append(metric)
                buildings.add(metric.edificio)
        self.fields['accessible_buildings'].queryset = Metrics.objects.filter(id__in=[metric.id for metric in unique_metrics])


# class GroupProfileAdmin(admin.ModelAdmin):
#     form = GroupProfileForm
#     list_display = ('group', 'record_limit', 'can_download_summary_excel', 'can_download_detailed_excel', 'can_download_pdf', 'can_view_detail', 'can_view_history', 'enable_ai_analysis')
#     list_filter = ('group',)
#     filter_horizontal = ('accessible_buildings',)

#     fieldsets = (
#         (None, {
#             'fields': ('group', 'record_limit')
#         }),
#         ('Permissions', {
#             'fields': ('can_download_summary_excel', 'can_download_detailed_excel', 'can_download_pdf', 'can_view_detail', 'can_view_history')
#         }),
#         ('Buildings Access', {
#             'fields': ('accessible_buildings',)
#         }),
#         ('AI Analysis', {
#             'fields': ('enable_ai_analysis',)
#         }),
#     )

# admin.site.register(GroupProfile, GroupProfileAdmin)

class GroupProfileForm(forms.ModelForm):
    """
    Custom form to show unique Building names in the accessible_buildings field.
    """
    accessible_buildings = forms.ModelMultipleChoiceField(
        queryset=Metrics.objects.none(),  # Placeholder, updated in __init__
        widget=admin.widgets.FilteredSelectMultiple('Metrics', is_stacked=False),
        required=False,
        label='Accessible Buildings (Unique Names)',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get distinct building names
        distinct_buildings = Metrics.objects.filter(
            building__isnull=False  # Exclude metrics without buildings
        ).distinct('building__name')  # Ensure distinct building names

        # Update queryset for the field
        self.fields['accessible_buildings'].queryset = distinct_buildings

        # Format labels to show only the building name
        self.fields['accessible_buildings'].label_from_instance = self.get_building_name

    @staticmethod
    def get_building_name(metric):
        """
        Display the unique name of the building associated with a Metric.
        """
        return metric.building.name if metric.building else f"Metric ID {metric.id} (No Building Name)"

    class Meta:
        model = GroupProfile
        fields = '__all__'


class GroupProfileAdmin(admin.ModelAdmin):
    form = GroupProfileForm
    list_display = (
        'group',
        'record_limit',
        'can_download_summary_excel',
        'can_download_detailed_excel',
        'can_download_pdf',
        'can_view_detail',
        'can_view_history',
        'enable_ai_analysis',
    )
    list_filter = ('group',)
    filter_horizontal = ('accessible_buildings',)

    fieldsets = (
        (None, {
            'fields': ('group', 'record_limit')
        }),
        ('Permissions', {
            'fields': ('can_download_summary_excel', 'can_download_detailed_excel', 'can_download_pdf', 'can_view_detail', 'can_view_history')
        }),
        ('Buildings Access', {
            'fields': ('accessible_buildings',)
        }),
        ('AI Analysis', {
            'fields': ('enable_ai_analysis',)
        }),
    )


admin.site.register(GroupProfile, GroupProfileAdmin)