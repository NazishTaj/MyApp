from django.contrib import admin
from .models import Patient, Appointment, Prescription, Clinic, UserProfile, ClinicSchedule


class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'age', 'gender')


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'appointment_date', 'appointment_time')


class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'created_at')


# 🔥 IMPORTANT PART (UPDATE THIS)

class ClinicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    list_editable = ('is_active',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'clinic', 'role', 'is_active')
    list_editable = ('is_active',)


# 🔥 REGISTER

admin.site.register(Clinic, ClinicAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(ClinicSchedule)
