from django.db import models

# Create your models here.
class ContactSupport(models.Model):
    user_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="User Name")
    user_email = models.EmailField()
    category = models.CharField(max_length=50, 
    choices=[
        ('Technical Support', 'Technical Support'),
        ('Feature Request', 'Feature Request'),
        ('New Building Request', 'New Building Request'),
        ('Other', 'Other')
    ], 
    default='Technical Support',
    verbose_name="Category")
    subject = models.CharField(max_length=150, null=True, blank=True, verbose_name="Subject")
    details = models.TextField(null=True, blank=True, verbose_name="Details of the Request")
    ticket_number = models.CharField(max_length=8, unique=True, verbose_name="Ticket Number")
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='attachments/', max_length=10000,  null=True, blank=True, verbose_name="Attach Files")

    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.user_name}"


class GlossaryTerm(models.Model):
    term_es = models.CharField(max_length=255, verbose_name='Spanish Term')
    description_es = models.TextField(verbose_name='Spanish Description')
    term_en = models.CharField(max_length=255, verbose_name='English Term')
    description_en = models.TextField(verbose_name='English Description')

    def __str__(self):
        return f"{self.term_es} / {self.term_en}"





class AIPromptTemplate(models.Model):
    name = models.CharField(max_length=255)
    prompt_template = models.TextField(help_text="Use placeholders like {{building_name}}")
    description = models.TextField(blank=True, help_text="A description of the template's purpose")

    def __str__(self):
        return self.name
