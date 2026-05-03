from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Patient, Appointment, Prescription, Clinic, UserProfile, ClinicSchedule
from django.db.models import Count, Q


# ===== COMMON FILTER (safe) =====
def clinic_filter_queryset(self, request, qs):
    if request.user.is_superuser:
        return qs
    if hasattr(request.user, 'userprofile'):
        return qs.filter(clinic=request.user.userprofile.clinic)
    return qs.none()


# ================== PATIENT ==================
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'clinic', 'name', 'phone', 'age', 'gender')
    list_filter = ('clinic',)
    search_fields = ('name', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return clinic_filter_queryset(self, request, qs)

    def save_model(self, request, obj, form, change):
        if not obj.pk and hasattr(request.user, 'userprofile'):
            obj.clinic = request.user.userprofile.clinic
        super().save_model(request, obj, form, change)

    # 🔒 edit me clinic change band
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('clinic',)
        return ()


# ================== APPOINTMENT ==================
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'clinic', 'patient', 'appointment_date', 'appointment_time', 'token_number')
    list_filter = ('clinic', 'appointment_date')
    search_fields = ('patient__name', 'patient__phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return clinic_filter_queryset(self, request, qs)

    def save_model(self, request, obj, form, change):
        if not obj.pk and hasattr(request.user, 'userprofile'):
            obj.clinic = request.user.userprofile.clinic
        super().save_model(request, obj, form, change)

    # 🔒 critical fields lock
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('clinic', 'patient', 'token_number')
        return ()

    # 🔥 FK filtering (VERY IMPORTANT)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if hasattr(request.user, 'userprofile'):
            clinic = request.user.userprofile.clinic

            if db_field.name == "patient":
                kwargs["queryset"] = Patient.objects.filter(clinic=clinic)

            if db_field.name == "doctor":
                kwargs["queryset"] = UserProfile.objects.filter(clinic=clinic)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ================== PRESCRIPTION ==================
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'clinic', 'patient', 'created_at')
    list_filter = ('clinic',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return clinic_filter_queryset(self, request, qs)

    def save_model(self, request, obj, form, change):
        if not obj.pk and hasattr(request.user, 'userprofile'):
            obj.clinic = request.user.userprofile.clinic
        super().save_model(request, obj, form, change)

    # 🔥 FK filtering
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if hasattr(request.user, 'userprofile'):
            clinic = request.user.userprofile.clinic

            if db_field.name == "patient":
                kwargs["queryset"] = Patient.objects.filter(clinic=clinic)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ================== CLINIC ==================
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'active_users_link', 'view_data')
    list_editable = ('is_active',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(
            active_users_count=Count(
                'userprofile',
                filter=Q(userprofile__is_active=True)
            )
        )

    # 🔥 clickable users count
    def active_users_link(self, obj):
        count = getattr(obj, 'active_users_count', 0)
    
        url = (
            reverse('admin:core_userprofile_changelist')
            + f'?clinic__id__exact={obj.id}&is_active__exact=1'
        )
    
        return format_html('<a href="{}">{} Users</a>', url, count)
    

    active_users_link.short_description = "Active Accounts"

    # 🔥 smart navigation (clinic → its data)
    def view_data(self, obj):
        patient_url = reverse('admin:core_patient_changelist') + f'?clinic__id__exact={obj.id}'
        appointment_url = reverse('admin:core_appointment_changelist') + f'?clinic__id__exact={obj.id}'
        prescription_url = reverse('admin:core_prescription_changelist') + f'?clinic__id__exact={obj.id}'

        return format_html(
            '<a href="{}">Patients</a> | '
            '<a href="{}">Appointments</a> | '
            '<a href="{}">Prescriptions</a>',
            patient_url, appointment_url, prescription_url
        )

    view_data.short_description = "Clinic Data"


# ================== USER PROFILE ==================
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'clinic', 'role', 'is_active')
    list_editable = ('is_active',)


# ================== CLINIC SCHEDULE ==================
class ClinicScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'clinic', 'day', 'start_time', 'end_time')
    list_filter = ('clinic',)


# ================== REGISTER ==================
admin.site.register(Clinic, ClinicAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(ClinicSchedule, ClinicScheduleAdmin)
