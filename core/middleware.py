from django.shortcuts import redirect
from django.urls import reverse

class StaffAccessMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            # Check userprofile safely
            if hasattr(request.user, 'userprofile'):

                profile = request.user.userprofile
                clinic = profile.clinic

                # Owner ko allow karo
                if not profile.is_owner:

                    # 🔴 Advanced mode OFF → block staff
                    if not clinic.is_advanced:

                        allowed_paths = [
                            reverse('login'),
                            reverse('logout'),
                            reverse('staff_blocked'),
                        ]

                        if request.path not in allowed_paths:
                            return redirect('staff_blocked')

        return self.get_response(request)
