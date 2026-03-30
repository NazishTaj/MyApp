from django.contrib import admin
from django.urls import path , include
from core import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', views.dashboard, name='home'),
    path('patients/', views.patient_list, name='patient_list'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('book-appointment/<int:patient_id>/', views.book_appointment, name='book_appointment'),
    path('patient-history/<int:patient_id>/', views.patient_history, name='patient_history'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-prescription/<int:patient_id>/', views.add_prescription, name='add_prescription'),
    path('online-booking/', views.online_booking, name='online_booking'),
    path('appointments/', views.appointments, name='appointments'),
    path('complete-appointment/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('patient/edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('patient/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path("add-schedule/", views.add_schedule, name="add_schedule"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
