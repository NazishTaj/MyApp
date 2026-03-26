from .models import UserPermission

def has_permission(user, perm_code):
    """
    Check if user has specific permission
    """

    # Agar user login hi nahi hai
    if not user.is_authenticated:
        return False

    profile = user.userprofile

    # Owner = full access
    if profile.is_owner:
        return True

    return UserPermission.objects.filter(
        user_profile=profile,
        permission__code=perm_code
    ).exists()
