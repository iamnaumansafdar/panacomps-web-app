from django import forms
from django.core.exceptions import ValidationError
from .models import Folios, Metrics, PDFRawData
from django.utils.dateparse import parse_date

class FolioMassUpdateForm(forms.Form):
    field = forms.ChoiceField(label="Field to update")
    value = forms.CharField(label="New value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].choices = [
            (f.name, f.verbose_name) 
            for f in Folios._meta.get_fields() 
            if not (f.is_relation or f.name == "id")
        ]

        self.fields['field'].widget.attrs.update({'class': 'form-control'})
        self.fields['value'].widget.attrs.update({'class': 'form-control'})

    def clean_value(self):
        field_name = self.cleaned_data.get('field')
        value = self.cleaned_data.get('value')
        
        model_field = Folios._meta.get_field(field_name)
        
        if isinstance(model_field, forms.DateField):
            try:
                value = parse_date(value)
                if not value:
                    raise ValidationError("Enter a valid date in YYYY-MM-DD format.")
            except ValueError:
                raise ValidationError("Enter a valid date in YYYY-MM-DD format.")
        return value



class MetricMassUpdateForm(forms.Form):
    field = forms.ChoiceField(label="Field to update")
    value = forms.CharField(label="New value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].choices = [
            (f.name, f.verbose_name) 
            for f in Metrics._meta.get_fields() 
            if not (f.is_relation or f.name == "id")
        ]

        self.fields['field'].widget.attrs.update({'class': 'form-control'})
        self.fields['value'].widget.attrs.update({'class': 'form-control'})

    def clean_value(self):
        field_name = self.cleaned_data.get('field')
        value = self.cleaned_data.get('value')
        
        model_field = Metrics._meta.get_field(field_name)
        
        if isinstance(model_field, forms.DateField):
            try:
                value = parse_date(value)
                if not value:
                    raise ValidationError("Enter a valid date in YYYY-MM-DD format.")
            except ValueError:
                raise ValidationError("Enter a valid date in YYYY-MM-DD format.")
        return value



class PDFDataMassUpdateForm(forms.Form):
    field = forms.ChoiceField(label="Field to update")
    value = forms.CharField(label="New value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].choices = [
            (f.name, f.verbose_name) 
            for f in PDFRawData._meta.get_fields() 
            if not (f.is_relation or f.name == "id")
        ]

        self.fields['field'].widget.attrs.update({'class': 'form-control'})
        self.fields['value'].widget.attrs.update({'class': 'form-control'})

    def clean_value(self):
        field_name = self.cleaned_data.get('field')
        value = self.cleaned_data.get('value')
        
        model_field = PDFRawData._meta.get_field(field_name)
        
        if isinstance(model_field, forms.DateField):
            try:
                value = parse_date(value)
                if not value:
                    raise ValidationError("Enter a valid date in YYYY-MM-DD format.")
            except ValueError:
                raise ValidationError("Enter a valid date in YYYY-MM-DD format.")
        return value