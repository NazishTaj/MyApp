from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .utils import has_permission
from datetime import date , datetime
from .forms import ClinicScheduleForm
import openpyxl
from django.http import HttpResponse
from .models import Patient, Appointment, Prescription, UserProfile , ClinicSchedule , Clinic
from django.core.exceptions import ValidationError
from .models import Bill, BillItem
from django.db.models import Sum



def billing_enabled(request):

    # ✅ check login
    if not request.user.is_authenticated:
        return False

    profile = get_object_or_404(UserProfile, user=request.user)

    return profile.clinic.billing_enabled


# ---------------- LOGIN ---------------- #

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- DASHBOARD ---------------- #

from django.utils import timezone

@login_required(login_url="login")
def dashboard(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    today = timezone.localtime().date()

    appointments_today = Appointment.objects.filter(
        clinic=clinic,
        appointment_date=today
    )
    today_revenue = Bill.objects.filter(
        clinic=clinic,
        created_at__date=today
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    today_appointments = appointments_today.count()
    pending_appointments = appointments_today.filter(status="Pending").count()
    completed_appointments = appointments_today.filter(status="Completed").count()

    total_patients = Patient.objects.filter(clinic=clinic).count()
    total_appointments = Appointment.objects.filter(clinic=clinic).count()
    

    context = {
        "appointments": appointments_today,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments,
        "today_appointments": today_appointments,
        "today_revenue": today_revenue,
    }

    return render(request, "dashboard.html", context)
    


# ---------------- PATIENTS ---------------- #

from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def patient_list(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    query = request.GET.get("q", "").strip()

    patients = Patient.objects.filter(clinic=clinic).order_by('patient_id')

    if query:
        patients = patients.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query)
        )

    context = {
        "patients": patients,
        "query": query
    }

    return render(request, "patients.html", context)


from django.core.exceptions import ValidationError

@login_required(login_url="login")
def add_patient(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    prefill_phone = request.GET.get("phone","")

    if request.method == "POST":

        name = request.POST["name"]
        phone = request.POST["phone"]
        age = request.POST["age"]
        gender = request.POST["gender"]
        address = request.POST.get("address")

        force_create = request.POST.get("force_create")

        existing_patient = Patient.objects.filter(
            clinic=clinic,
            phone=phone
        ).first()

        # 🔴 Duplicate detected but user didn't confirm
        if existing_patient and not force_create:
            return render(
                request,
                "add_patient.html",
                {
                    "error_duplicate": "Patient with this phone number already exists.",
                    "prefill_phone": phone,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "address": address,
                    "show_continue": True
                }
            )

        patient = Patient(
            clinic=clinic,
            name=name,
            phone=phone,
            age=age,
            gender=gender,
            address=address
        )

        try:
            patient.full_clean()
            patient.save()
            return redirect("patient_list")

        except ValidationError as e:

            return render(
                request,
                "add_patient.html",
                {
                    "error": e.message_dict,
                    "prefill_phone": phone
                }
            )

    return render(
        request,
        "add_patient.html",
        {"prefill_phone": prefill_phone}
    )
@login_required(login_url="login")
def edit_patient(request, patient_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    if request.method == "POST":

        patient.name = request.POST.get("name")
        patient.phone = request.POST.get("phone")
        patient.age = request.POST.get("age")
        patient.gender = request.POST.get("gender")
        patient.address = request.POST.get("address")

        patient.save()

        return redirect("patient_list")

    return render(request, "edit_patient.html", {"patient": patient})


@login_required(login_url="login")
def delete_patient(request, patient_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    patient.delete()

    return redirect("patient_list")


# ---------------- APPOINTMENTS ---------------- #
from django.utils import timezone
@login_required(login_url="login")
def book_appointment(request, patient_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    if request.method == "POST":

        date_val = request.POST.get("date")
        time = request.POST.get("time")
        problem = request.POST.get("problem")

        # ✅ DATE FIX (MAIN FIX)
        if date_val:
            date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
        else:
            date_val = timezone.localtime().date()

        # ✅ TIME FIX
        if time:
            time = datetime.strptime(time, "%H:%M").time()
        else:
            time = datetime.now().time()

        # 🔹 Token logic
        last_token = Appointment.objects.filter(
            clinic=clinic,
            appointment_date=date_val
        ).order_by('-token_number').first()

        if last_token and last_token.token_number:
            token = last_token.token_number + 1
        else:
            token = 1

        Appointment.objects.create(
            clinic=clinic,
            patient=patient,
            appointment_date=date_val,
            appointment_time=time,
            problem=problem,
            token_number=token
        )

        return redirect("dashboard")   # 🔥 IMPORTANT

    return render(request, "book_appointment.html", {"patient": patient})
@login_required(login_url="login")
def appointments(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    appointments = Appointment.objects.filter(clinic=clinic).order_by(
        "-appointment_date",
        "appointment_time"
    )

    return render(request, "appointments.html", {"appointments": appointments})


@login_required(login_url="login")
def complete_appointment(request, appointment_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    appointment = get_object_or_404(Appointment, id=appointment_id, clinic=clinic)

    appointment.status = "Completed"
    appointment.save()

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


@login_required(login_url="login")
def cancel_appointment(request, appointment_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    appointment = get_object_or_404(Appointment, id=appointment_id, clinic=clinic)

    appointment.status = "Cancelled"
    appointment.save()

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


# ---------------- PRESCRIPTIONS ---------------- #

@login_required(login_url="login")
def add_prescription(request, patient_id):
    if not has_permission(request.user, "create_prescription"):
        return HttpResponse("Unauthorized", status=403)
    
    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic
    
    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    if request.method == "POST":

        diagnosis = request.POST.get("diagnosis")
        symptoms = request.POST.get("symptoms")
        medicines = request.POST.get("medicines")
        tests = request.POST.get("tests")
        notes = request.POST.get("notes")
        weight = request.POST.get("weight")
        blood_group = request.POST.get("blood_group")

        Prescription.objects.create(
            clinic=clinic,
            patient=patient,
            diagnosis=diagnosis,
            symptoms=symptoms,
            medicines=medicines,
            tests=tests,
            notes=notes,
            weight=weight,
            blood_group=blood_group,
            created_by=profile,
            doctor=profile  
        )

        return redirect("patient_history", patient_id=patient.id)

    return render(request, "add_prescription.html", {"patient": patient})


@login_required(login_url="login")
def patient_history(request, patient_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
    bills = Bill.objects.filter(
    clinic=clinic,
    patient=patient
).order_by("-created_at")

    prescriptions = Prescription.objects.filter(
        clinic=clinic,
        patient=patient
    ).order_by("-created_at") 

    return render(request, "patient_history.html", {
        "patient": patient,
        "prescriptions": prescriptions,
        "bills":bills
    })
@login_required
def create_bill_for_patient(request, patient_id):
    if not has_permission(request.user, "manage_billing"):
        return HttpResponse("Unauthorized", status=403)
    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    if not clinic.billing_enabled:
        return redirect("dashboard")

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    if request.method == "POST":

        payment_mode = request.POST.get("payment_mode")
        discount_percent = float(request.POST.get("discount")or 0)

        # Generate bill number
        last_bill = Bill.objects.filter(clinic=clinic).order_by("-id").first()

        if last_bill:
            last_number = int(last_bill.bill_number.split("-")[1])
            new_number = last_number + 1
        else:
            new_number = 1001

        bill_number = f"FD-{new_number}"

        # Create bill
        bill = Bill.objects.create(
            clinic=clinic,
            patient=patient,   # 🔥 FIXED PATIENT
            doctor=profile,
            bill_number=bill_number,
            payment_mode=payment_mode,
        )

        item_names = request.POST.getlist("item_name[]")
        item_amounts = request.POST.getlist("item_amount[]")

        subtotal = 0

        for name, amount in zip(item_names, item_amounts):
            if name and amount:
                amount = float(amount)

                BillItem.objects.create(
                    bill=bill,
                    item_name=name,
                    amount=amount
                )

                subtotal += amount

        discount_amount = (subtotal * discount_percent) / 100
        total = subtotal - discount_amount

        bill.subtotal = subtotal
        bill.discount = discount_percent
        bill.discount_amount = discount_amount
        bill.total_amount = total
        bill.save()

        return redirect("view_bill", bill_id=bill.id)

    return render(request, "billing/create_bill.html", {
        "patient": patient,
        "clinic": clinic
    })

@login_required(login_url="login")
def view_prescription(request, id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    prescription = get_object_or_404(Prescription, id=id, clinic=clinic)

    return render(request, "view_prescription.html", {
    "prescription": prescription,
    "clinic": clinic
    })


# ---------------- ONLINE BOOKING ---------------- #

def online_booking(request):

    if request.method == "POST":

        name = request.POST["name"]
        phone = request.POST["phone"]
        age = request.POST["age"]
        date_val = request.POST["date"]
        time = request.POST["time"]
        problem = request.POST["problem"]

        clinic = Clinic.objects.first()

        if not clinic:
            return HttpResponse("No clinic configured", status=400)

        # ✅ DATE FIX
        if date_val:
            date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
        else:
            date_val = timezone.localtime().date()

        # ✅ TIME FIX
        if time:
            time = datetime.strptime(time, "%H:%M").time()
        else:
            time = datetime.now().time()

        # ✅ PATIENT (avoid duplicate)
        patient, created = Patient.objects.get_or_create(
            clinic=clinic,
            phone=phone,
            defaults={
                "name": name,
                "age": age,
                "gender": "Unknown"
            }
        )

        # ✅ PREVENT DUPLICATE BOOKING SAME DAY
        if Appointment.objects.filter(
            clinic=clinic,
            patient=patient,
            appointment_date=date_val
        ).exists():
            return render(request, "booking_success.html", {
                "message": "You already booked for this date"
            })

        # ✅ TOKEN LOGIC (per day reset)
        last_token = Appointment.objects.filter(
            clinic=clinic,
            appointment_date=date_val
        ).order_by('-token_number').first()

        token = last_token.token_number + 1 if last_token else 1

        # ✅ CREATE APPOINTMENT
        Appointment.objects.create(
            clinic=clinic,
            patient=patient,
            appointment_date=date_val,
            appointment_time=time,
            problem=problem,
            token_number=token
        )

        return render(request, "booking_success.html", {
            "message": "Booking successful"
        })

    return render(request, "online_booking.html")




@login_required(login_url="login")
def profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    context = {
        "user": request.user,
        "profile": profile,
        "clinic": clinic
    }

    return render(request, "profile.html", context)



#edit profile

@login_required
def edit_profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    # fetch clinic schedule
    schedules = ClinicSchedule.objects.filter(clinic=clinic).order_by('day','start_time')

    if request.method == "POST":

        profile.name = request.POST.get("name")
        profile.phone = request.POST.get("phone")
        if profile.is_owner:
            clinic.name = request.POST.get("clinic_name")
            clinic.phone = request.POST.get("clinic_phone")
            clinic.address = request.POST.get("clinic_address")
            clinic.consultation_fee = request.POST.get("consultation_fee")
        
            clinic.billing_enabled = bool(request.POST.get("billing_enabled"))
            clinic.is_advanced = bool(request.POST.get("is_advanced"))

        if request.FILES.get("photo"):
            profile.photo = request.FILES["photo"]

        if request.FILES.get("logo"):
            clinic.logo = request.FILES["logo"]

        profile.save()
        clinic.save()

        return redirect("profile")

    return render(request, "edit_profile.html", {
        "profile": profile,
        "clinic": clinic,
        "schedules": schedules   # ← IMPORTANT
    })


@login_required
def add_schedule(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    if request.method == "POST":
        form = ClinicScheduleForm(request.POST)

        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.clinic = clinic
            schedule.save()

            print("Schedule saved:", schedule.day, schedule.start_time, schedule.end_time)

            return redirect("profile")

        else:
            print("FORM ERRORS:", form.errors)  # debug ke liye

    else:
        form = ClinicScheduleForm()

    return render(request, "add_schedule.html", {
        "form": form
    })

@login_required
def delete_schedule(request, id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    schedule = ClinicSchedule.objects.get(id=id, clinic=clinic)
    schedule.delete()

    return redirect("edit_profile")

@login_required
def edit_schedule(request, id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    schedule = ClinicSchedule.objects.get(id=id, clinic=clinic)

    if request.method == "POST":

        schedule.day = request.POST.get("day")
        schedule.start_time = request.POST.get("start_time")
        schedule.end_time = request.POST.get("end_time")

        schedule.save()

        return redirect("edit_profile")

    return render(request, "edit_schedule.html", {
        "schedule": schedule
    })

#Excel Export

@login_required
def export_month_appointments(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    month = request.GET.get("month")
    year = request.GET.get("year")

    if not month or not year:
        today = date.today()
        month = today.month
        year = today.year

    appointments = Appointment.objects.filter(
        clinic=clinic,
        appointment_date__month=int(month),
        appointment_date__year=int(year)
    ).select_related("patient")

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Appointments"

    headers = [
        "Patient Name",
        "Phone",
        "Age",
        "Gender",
        "Address",
        "Date",
        "Time",
        "Problem",
        "Status"
    ]

    sheet.append(headers)

    for appt in appointments:

        patient = appt.patient

        sheet.append([
            patient.name,
            patient.phone,
            patient.age,
            patient.gender,
            patient.address,
            appt.appointment_date.strftime("%d-%m-%Y"),
            appt.appointment_time.strftime("%H:%M"),
            appt.problem,
            appt.status
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    filename = f"appointments_{month}_{year}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    workbook.save(response)

    return response



@login_required
def export_all_appointments(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    appointments = Appointment.objects.filter(clinic=clinic)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Appointments"

    headers = [
        "Patient Name",
        "Phone",
        "Age",
        "Gender",
        "Address",
        "Date",
        "Time",
        "Problem",
        "Status"
    ]

    sheet.append(headers)

    for appt in appointments:

        patient = appt.patient   # <-- important line

        sheet.append([
            patient.name,
            patient.phone,
            patient.age,
            patient.gender,
            patient.address,
            appt.appointment_date.strftime("%d-%m-%Y"),
            appt.appointment_time.strftime("%H:%M"),
            appt.problem,
            appt.status
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response['Content-Disposition'] = 'attachment; filename="all_appointments.xlsx"'

    workbook.save(response)

    return response


#------------------------------------------------------------


@login_required
def mark_pending(request, appointment_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    appointment = get_object_or_404(Appointment, id=appointment_id, clinic=clinic)

    appointment.status = "Pending"
    appointment.save()

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))



#Bill 

@login_required
def create_bill(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    if not clinic.billing_enabled:
        return redirect("dashboard")

    patients = Patient.objects.filter(clinic=clinic)

    if request.method == "POST":

        patient_id = request.POST.get("patient")
        payment_mode = request.POST.get("payment_mode")
        discount_percent = float(request.POST.get("discount")or 0)

        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

        # Generate bill number
        last_bill = Bill.objects.filter(clinic=clinic).order_by("-id").first()

        if last_bill:
            last_number = int(last_bill.bill_number.split("-")[1])
            new_number = last_number + 1
        else:
            new_number = 1001

        bill_number = f"FD-{new_number}"

        # Create empty bill
        bill = Bill.objects.create(
            clinic=clinic,
            patient=patient,
            doctor=profile,
            bill_number=bill_number,
            payment_mode=payment_mode,
        )

        item_names = request.POST.getlist("item_name[]")
        item_amounts = request.POST.getlist("item_amount[]")

        subtotal = 0
        for name, amount in zip(item_names, item_amounts):

            if name and amount:

                amount = float(amount)

                BillItem.objects.create(
                    bill=bill,
                    item_name=name,
                    amount=amount
                )

                subtotal += amount

        # Discount calculation
        discount_amount = (subtotal * discount_percent) / 100

        total = subtotal - discount_amount

        bill.subtotal = subtotal
        bill.discount = discount_percent
        bill.discount_amount = discount_amount
        bill.total_amount = total

        bill.save()

        return redirect("view_bill", bill_id=bill.id)

    return render(request, "billing/create_bill.html", {
        "patients": patients,
        "clinic": clinic
    })



#Bill History

@login_required
def bill_history(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    if not clinic.billing_enabled:
        return redirect("dashboard")

    bills = Bill.objects.filter(clinic=clinic).order_by("-created_at")

    return render(request, "billing/bill_history.html", {
        "bills": bills
    })

#Bill Detail
@login_required
def view_bill(request, bill_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    bill = get_object_or_404(Bill, id=bill_id, clinic=clinic)

    items = bill.items.all()

    return render(request, "billing/view_bill.html", {
        "bill": bill,
        "items": items,
        "clinic": clinic
    })


  #Bill Print
@login_required
def print_bill(request, bill_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    bill = get_object_or_404(
        Bill,
        id=bill_id,
        clinic=clinic
    )

    items = bill.items.all()

    return render(request, "billing/print_bill.html", {
        "bill": bill,
        "items": items,
        "clinic": clinic
    })


# Print Prescription
@login_required(login_url="login")
def print_prescription(request, id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    prescription = get_object_or_404(
        Prescription,
        id=id,
        clinic=clinic
    )

    return render(request, "print_prescription.html", {
        "prescription": prescription,
        "clinic": clinic
    })

@login_required
def enable_advanced_mode(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    if not clinic.is_advanced:
        clinic.is_advanced = True
        clinic.save()

    return redirect("dashboard")

from django.contrib.auth.models import User
from .models import UserProfile, UserPermission, Permission

@login_required
def add_staff(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic
    if not profile.is_owner:
        return HttpResponse("Unauthorized", status=403)
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")
        role = request.POST.get("role")

        # Username validation
        if User.objects.filter(username=username).exists():
            return render(request, "staff/add_staff.html", {
                "error": "Username already exists"
            })

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # ✅ Create profile
        profile_obj = UserProfile.objects.create(
            user=user,
            clinic=clinic,
            role=role,
            is_owner=False,
            name=name
        )

        # 🔥 DEFAULT PERMISSIONS AUTO ASSIGN
        if role == "receptionist":
            default_perms = [
                "manage_patients",
                "manage_appointments",
                "manage_billing"
            ]

            for perm_code in default_perms:
                perm = Permission.objects.filter(code=perm_code).first()
                if perm:

                    UserPermission.objects.create(
                        user_profile=profile_obj,
                        permission=perm
                    )

        return redirect("staff_list")

    return render(request, "staff/add_staff.html")

@login_required
def staff_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic
    if not profile.is_owner:
        return HttpResponse("Unauthorized", status=403)

    staff = UserProfile.objects.filter(clinic=clinic,is_owner=False)

    return render(request, "staff/staff_list.html", {
        "staff": staff
    })

from .models import UserPermission, Permission
@login_required
def edit_staff_permissions(request, staff_id):

    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    staff = get_object_or_404(UserProfile, id=staff_id, clinic=clinic)

    permissions = Permission.objects.all()

    # 🔥 CLEAN LABEL BANANE KE LIYE
    permissions_data = []
    for p in permissions:
        label = p.code.replace("_", " ").title()
        permissions_data.append({
            "code": p.code,
            "label": label
        })

    if request.method == "POST":

        selected_perms = request.POST.getlist("permissions")

        # Purane delete
        UserPermission.objects.filter(user_profile=staff).delete()

        # Naye add
        for perm_code in selected_perms:
            perm = Permission.objects.filter(code=perm_code).first()
            if perm:
                UserPermission.objects.create(
                    user_profile=staff,
                    permission=perm
                )

        return redirect("staff_list")

    # Existing permissions
    user_perms = UserPermission.objects.filter(user_profile=staff)
    user_perm_codes = [p.permission.code for p in user_perms]

    return render(request, "staff/edit_permissions.html", {
        "staff": staff,
        "permissions": permissions_data,   # 🔥 IMPORTANT CHANGE
        "user_perm_codes": user_perm_codes
    })

