from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    path("", views.login_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
    "change-password/",
    PasswordChangeView.as_view(template_name="change_password.html"),
    name="change_password",
),

path(
    "change-password-done/",
    PasswordChangeDoneView.as_view(template_name="change_password_done.html"),
    name="password_change_done",
),
path("profile/", views.profile, name="profile"),
path("edit-profile/", views.edit_profile, name="edit_profile"),
path("edit-schedule/<int:id>/", views.edit_schedule, name="edit_schedule"),
path("delete-schedule/<int:id>/", views.delete_schedule, name="delete_schedule"),
path("export-month/", views.export_month_appointments, name="export_month"),
path("export-all/", views.export_all_appointments, name="export_all"),
path("mark-pending/<int:appointment_id>/", views.mark_pending, name="mark_pending"),
path("billing/create/", views.create_bill, name="create_bill"),
path("billing/history/", views.bill_history, name="bill_history"),
path("billing/<int:bill_id>/", views.view_bill, name="view_bill"),
path(
    "billing/create/<int:patient_id>/",
    views.create_bill_for_patient,
    name="create_bill_for_patient"
),
path("bill/<int:bill_id>/print/", views.print_bill, name="print_bill"),
path("prescription/<int:id>/revise/", views.revise_prescription, name="revise_prescription"),
path("prescription/<int:id>/print/", views.print_prescription, name="print_prescription"),
path('prescription/<int:id>/', views.view_prescription, name='view_prescription'),
path("enable-advanced/", views.enable_advanced_mode, name="enable_advanced"),
path("staff/add/", views.add_staff, name="add_staff"),
path("staff/", views.staff_list, name="staff_list"),
path("staff/<int:staff_id>/permissions/", views.edit_staff_permissions, name="edit_staff_permissions"),
path('staff-blocked/', views.staff_blocked, name='staff_blocked'),
path("staff/<int:staff_id>/deactivate/", views.deactivate_staff, name="deactivate_staff"),
path("send-to-doctor/<int:appointment_id>/", views.send_to_doctor, name="send_to_doctor"),
path("billing/export-month/", views.export_month_bills, name="export_month_bills"),
path("billing/export-all/", views.export_all_bills, name="export_all_bills"),
path("api/queue/", views.api_queue, name="api_queue"),
path('get-queue-data/', views.get_queue_data, name='get_queue_data'),
path('clinic-blocked/', views.clinic_blocked, name='clinic_blocked'),
path('user-blocked/', views.user_blocked, name='user_blocked'),
path('revenue-report/', views.revenue_report, name='revenue_report'),
path('search-medicine/', views.search_medicine, name='search_medicine'),
path('prescription/<int:id>/pdf/', views.download_prescription_pdf, name='download_prescription_pdf'),
path("search-patients/", views.search_patients, name="search_patients"),







]
