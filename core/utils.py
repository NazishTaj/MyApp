from .models import UserPermission

def has_permission(user, perm_code):
    profile = user.userprofile

    # Owner = full access
    if profile.is_owner:
        return True

    return UserPermission.objects.filter(
        user_profile=profile,
        permission__code=perm_code
    ).exists()
