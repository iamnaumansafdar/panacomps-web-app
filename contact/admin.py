from django.contrib import admin
from .models import ContactSupport, GlossaryTerm, AIPromptTemplate

class ContactSupportAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ('formatted_ticket_number', 'user_name', 'user_email', 'subject', 'category', 'created_at')
    
    # Enable search functionality for specific fields
    search_fields = ('ticket_number', 'user_name', 'user_email', 'subject')
    
    # Enable filters for date and category
    list_filter = ('created_at', 'category')
    
    # Fields that should be read-only after creation
    readonly_fields = ('ticket_number', 'created_at')
    
    # Organize fields into sections in the admin form view
    fieldsets = (
        ('User Information', {
            'fields': ('user_name', 'user_email')
        }),
        ('Issue Details', {
            'fields': ('category', 'subject', 'details')
        }),
        ('System Information', {
            'fields': ('ticket_number', 'created_at'),
        }),
        ('Attachments', {
            'fields': ('attachment',),
        }),
    )

    # Ordering the records by most recent first
    ordering = ('-created_at',)
    
    # Custom method to format ticket number in the list view
    def formatted_ticket_number(self, obj):
        return f"Ticket #{obj.ticket_number}"
    formatted_ticket_number.short_description = 'Ticket Number'

    # Override the save method to handle read-only fields on object creation
    def get_readonly_fields(self, request, obj=None):
        # If creating a new object, exclude the read-only fields
        if obj is None:
            return ('created_at',)
        return self.readonly_fields

# Register the model and the custom admin interface
admin.site.register(ContactSupport, ContactSupportAdmin)



@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ('term_es', 'term_en')


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'prompt_template')
    ordering = ('name',)
    
    # Define the fieldsets without duplicate fields
    fieldsets = (
        (None, {
            'fields': ('name', 'prompt_template')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('description',), 
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('name')