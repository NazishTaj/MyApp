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
                    reverse('user_blocked'),
                ]

                # 🔥 CLEAN PATH FIX (MOST IMPORTANT)
                current_path = request.path_info.rstrip('/')
                allowed_clean = [p.rstrip('/') for p in allowed_paths]

                # 🔴 1. Clinic check
                if not clinic.is_active:
                    if current_path not in allowed_clean:
                        return redirect('clinic_blocked')

                # 🔴 2. User check
                if not profile.is_active:
                    if current_path not in allowed_clean:
                        return redirect('user_blocked')

                # 🟡 3. Advanced mode
                if not profile.is_owner:
                    if not clinic.is_advanced:
                        if current_path not in allowed_clean:
                            return redirect('staff_blocked')

        return self.get_response(request)
