from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

class ApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            approval_status = request.user.approval_status
            active_status = request.user.is_active
            # print(approval_status, 'Approval', active_status, request.user)  # Debug print to check approval status
            
            # # Exclude admin URLs to avoid redirecting from admin panel
            if request.path.startswith(reverse('admin:index')):
                return None

            # Redirect if user is inactive and trying to access pages other than signup or login
            if active_status == 'False':
                if request.path != reverse('signup') and request.path != reverse('login'):
                    print('Inactive User')
                    messages.warning(request, "We have sent a verification email. Please verify your account.")
                    return redirect('login')

            # Redirect if user approval is pending or rejected, avoid loop with signup and login page
            if request.path != reverse('login') and request.path != reverse('signup'):
                if approval_status == 'pending':
                    print('Pending Approval')
                    messages.warning(request, "Your account is still pending approval by an administrator.")
                    return redirect('login')
                elif approval_status == 'rejected':
                    messages.error(request, "Your account has been rejected. Please contact support.")
                    return redirect('login')

        return None
