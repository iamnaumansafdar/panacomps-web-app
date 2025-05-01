from django import forms
from .models import ContactSupport

class ContactSupportForm(forms.ModelForm):
    class Meta:
        model = ContactSupport
        fields = ['user_name', 'user_email', 'category', 'subject', 'details', 'attachment']
        widgets = {
            'details': forms.Textarea(attrs={
                'placeholder': 'Describe the problem or request in detail.',
                'id': 'id_details',  # Ensure the ID is set for JavaScript to target
                'rows': 4,
            }),
        }
    

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ContactSupportForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['user_name'].initial = user.get_full_name()
            self.fields['user_email'].initial = user.email


    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')

        if attachment:
            # Check file size (5MB = 5 * 1024 * 1024 bytes)
            max_file_size = 5 * 1024 * 1024
            if attachment.size > max_file_size:
                raise forms.ValidationError(f'File size must be 5MB or less. Your file is {attachment.size / (1024 * 1024):.2f}MB.')

        return attachment        

    # def clean_attachment(self):
    #     allowed_formats = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
    #     attachment = self.cleaned_data.get('attachment')

    #     if attachment:
    #         file_extension = attachment.name.split('.')[-1].lower()
    #         if file_extension not in allowed_formats:
    #             raise forms.ValidationError(f'Unsupported file format. Allowed formats: {", ".join(allowed_formats)}')

    #     return attachment        