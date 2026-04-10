from django.shortcuts import redirect
from django.urls import reverse

class StaffAccessMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            if hasattr(request.user, 'userprofile'):

                profile = request.user.userprofile
                clinic = profile.clinic

                allowed_paths = [
                    reverse('login'),
                    reverse('logout'),
                    reverse('staff_blocked'),
                    reverse('clinic_blocked'),
                ]

                # 🔴 1. Clinic check (MOST IMPORTANT)
                if not clinic.is_active:
                    if not any(request.path.startswith(p) for p in allowed_paths):
                        return redirect('clinic_blocked')

                # 🔴 2. User check
                if not profile.is_active:
                    if not any(request.path.startswith(p) for p in allowed_paths):
                        return redirect('user_blocked')

                # 🟡 3. Existing logic (Advanced mode)
                if not profile.is_owner:
                    if not clinic.is_advanced:
                        if not any(request.path.startswith(p) for p in allowed_paths):
                            return redirect('staff_blocked')

        return self.get_response(request)
