from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect, render
from .models import CustomUser, UserClassification
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages



class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_classifications'] = UserClassification.objects.all()
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Inactive until email confirmation and admin approval
        user.save()

        # Send email confirmation
        current_site = get_current_site(self.request)
        subject = 'Activate Your Account'
        message = render_to_string('registration/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
        })
        plain_message = strip_tags(message)
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)

        # Send admin notification
        send_mail(
            'New User Registration',
            f'A new user has registered: {user.email}. Please review and approve their account.',
            settings.DEFAULT_FROM_EMAIL,
            [admin_email for admin_email in get_admin_emails()]
        )
        messages.success(self.request, "We have sent a verification email. Please verify your account.")
        
        return super().form_valid(form)

def get_admin_emails():
    return [user.email for user in CustomUser.objects.filter(is_staff=True, is_superuser=True)]


class ActivateAccountView(View):
    template_name = 'registration/activation_success.html'
    
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if not user.is_active:
            user.is_active = True
            user.save()
            return render(request, self.template_name)
        return redirect('login')