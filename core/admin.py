from django.contrib import admin
from .models import Patient, Appointment, Prescription, Clinic, UserProfile , ClinicSchedule


class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'age', 'gender')


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'appointment_date', 'appointment_time')


class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'created_at')

admin.site.register(Clinic)
admin.site.register(UserProfile)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(ClinicSchedule)