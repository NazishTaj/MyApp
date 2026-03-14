from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import date , datetime
from .forms import ClinicScheduleForm

from .models import Patient, Appointment, Prescription, UserProfile , ClinicSchedule , Clinic


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

from datetime import date

@login_required(login_url="login")
def dashboard(request):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    today = date.today()

    appointments_today = Appointment.objects.filter(
        clinic=clinic,
        appointment_date=today
    )

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
    }

    return render(request, "dashboard.html", context)


# ---------------- PATIENTS ---------------- #

from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def patient_list(request):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    query = request.GET.get("q", "").strip()

    patients = Patient.objects.filter(clinic=clinic)

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


@login_required(login_url="login")
def add_patient(request):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    prefill_phone = request.GET.get("phone","")

    if request.method == "POST":

        name = request.POST["name"]
        phone = request.POST["phone"]
        age = request.POST["age"]
        gender = request.POST["gender"]
        address = request.POST.get("address")

        Patient.objects.create(
            clinic=clinic,
            name=name,
            phone=phone,
            age=age,
            gender=gender,
            address=address
        )

        return redirect("patient_list")

    return render(request, "add_patient.html",
            {"prefill_phone": prefill_phone})


@login_required(login_url="login")
def edit_patient(request, patient_id):

    profile = UserProfile.objects.get(user=request.user)
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

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    patient.delete()

    return redirect("patient_list")


# ---------------- APPOINTMENTS ---------------- #

@login_required(login_url="login")
def book_appointment(request, patient_id):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    if request.method == "POST":

        date_val = request.POST["date"]
        time = request.POST["time"]
        problem = request.POST["problem"]

        if not date_val:
            date_val = date.today()

        if not time:
             time = datetime.now().time()
        
        

        Appointment.objects.create(
            clinic=clinic,
            patient=patient,
            appointment_date=date_val,
            appointment_time=time,
            problem=problem
        )

        return redirect("appointments")

    return render(request, "book_appointment.html", {"patient": patient})


@login_required(login_url="login")
def appointments(request):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    appointments = Appointment.objects.filter(clinic=clinic).order_by(
        "-appointment_date",
        "appointment_time"
    )

    return render(request, "appointments.html", {"appointments": appointments})


@login_required(login_url="login")
def complete_appointment(request, appointment_id):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    appointment = get_object_or_404(Appointment, id=appointment_id, clinic=clinic)

    appointment.status = "Completed"
    appointment.save()

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


@login_required(login_url="login")
def cancel_appointment(request, appointment_id):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    appointment = get_object_or_404(Appointment, id=appointment_id, clinic=clinic)

    appointment.status = "Cancelled"
    appointment.save()

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


# ---------------- PRESCRIPTIONS ---------------- #

@login_required(login_url="login")
def add_prescription(request, patient_id):

    profile = UserProfile.objects.get(user=request.user)
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
        )

        return redirect("patient_history", patient_id=patient.id)

    return render(request, "add_prescription.html", {"patient": patient})


@login_required(login_url="login")
def patient_history(request, patient_id):

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)

    prescriptions = Prescription.objects.filter(
        clinic=clinic,
        patient=patient
    )

    return render(request, "patient_history.html", {
        "patient": patient,
        "prescriptions": prescriptions
    })


@login_required(login_url="login")
def view_prescription(request, id):

    profile = UserProfile.objects.get(user=request.user)
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

        patient = Patient.objects.create(
            name=name,
            phone=phone,
            age=age,
            gender="Unknown"
        )

        Appointment.objects.create(
            patient=patient,
            appointment_date=date_val,
            appointment_time=time,
            problem=problem
        )

        return render(request, "booking_success.html")

    return render(request, "online_booking.html")





@login_required(login_url="login")
def profile(request):

    profile = UserProfile.objects.get(user=request.user)
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

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    # fetch clinic schedule
    schedules = ClinicSchedule.objects.filter(clinic=clinic).order_by('day','start_time')

    if request.method == "POST":

        profile.doctor_name = request.POST.get("doctor_name")
        profile.phone = request.POST.get("phone")

        clinic.name = request.POST.get("clinic_name")
        clinic.phone = request.POST.get("clinic_phone")
        clinic.address = request.POST.get("clinic_address")

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

    profile = UserProfile.objects.get(user=request.user)
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

    profile = UserProfile.objects.get(user=request.user)
    clinic = profile.clinic

    schedule = ClinicSchedule.objects.get(id=id, clinic=clinic)
    schedule.delete()

    return redirect("edit_profile")

@login_required
def edit_schedule(request, id):

    profile = UserProfile.objects.get(user=request.user)
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



    