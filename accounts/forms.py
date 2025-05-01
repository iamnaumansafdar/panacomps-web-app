from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserClassification


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            'username',
            "first_name",
            "last_name",
            'classification',
            'language_preference',
            'currency_preference',
            "password1",
            "password2"
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classification'].queryset = UserClassification.objects.all()