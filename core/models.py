from django.db import models
from django.contrib.auth.models import User


# Clinic Model
class Clinic(models.Model):
    name = models.CharField(max_length=200)
   # doctor_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    logo = models.ImageField(upload_to="clinic_logos/", blank=True, null=True)
    is_advanced = models.BooleanField(default=False)
    billing_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.name


# User Profile (Doctor Login → Clinic Link)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    

    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('doctor', 'Doctor'),   # 🔥 ADD THIS
        ('receptionist', 'Receptionist'),
        ('assistant', 'Assistant'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')
    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    degree = models.CharField(max_length=100, blank=True, null=True)
    reg_no = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to="doctor_photos/", blank=True, null=True)
    assigned_doctor = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"role__in": ["owner", "doctor"]},
        related_name="assistants"
    )
    def save(self, *args, **kwargs):
        # sirf doctor/owner ke liye fee allowed
        if self.role not in ['owner', 'doctor']:
            self.consultation_fee = None

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


# Patient Model

from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be exactly 10 digits"
)

class Patient(models.Model):

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    patient_id = models.IntegerField(blank=True, null=True) 

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, validators=[phone_validator])

    address = models.TextField(blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.filter(
                clinic=self.clinic
            ).order_by('-patient_id').first()

            if last_patient:
                self.patient_id = last_patient.patient_id + 1
            else:
                self.patient_id = 1

        super().save(*args, **kwargs)
        
    class Meta:
        unique_together = ['clinic', 'patient_id']

    def __str__(self):
        return f"{self.name} ({self.phone})"

#Appointment Model
class Appointment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    QUEUE_STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
    ]

    VISIT_TYPE_CHOICES = [
        ('new', 'New'),
        ('followup', 'Follow-up'),
        ('free', 'Free'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('waived', 'Waived'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    doctor = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role__in": ["owner", "doctor"]}
    )

    token_number = models.PositiveIntegerField(blank=True, null=True)

    problem = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # 💰 Consultation
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='new')

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'   # ✅ safer default
    )

    payment_mode = models.CharField(
        max_length=10,
        choices=PAYMENT_MODE_CHOICES,
        blank=True,
        null=True
    )

    # 📊 Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    queue_status = models.CharField(
        max_length=20,
        choices=QUEUE_STATUS_CHOICES,
        default='waiting'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date', '-token_number']

    def save(self, *args, **kwargs):

        # ✅ Auto token generation
        if not self.token_number:
            last = Appointment.objects.filter(
                clinic=self.clinic,
                appointment_date=self.appointment_date
            ).order_by('-token_number').first()

            self.token_number = (last.token_number + 1) if last else 1

        # ✅ Free visit handling
        if self.visit_type == 'free':
            self.consultation_fee = 0
            self.payment_status = 'waived'
            self.payment_mode = None
        elif self.consultation_fee in [None, ""] and self.doctor:
            self.consultation_fee = self.doctor.consultation_fee or 0

        # ✅ Payment validation
        if self.payment_status in ['unpaid', 'waived']:
            self.payment_mode = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.name} - {self.appointment_date} {self.appointment_time}"

# Prescription Model
class Prescription(models.Model):

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    diagnosis = models.TextField()
    symptoms = models.TextField(blank=True)
    medicines = models.TextField()
    tests = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    blood_group = models.CharField(max_length=5, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_prescriptions"
    )

    doctor = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_prescriptions",
        limit_choices_to={"role__in": ["owner", "doctor"]}
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revisions"
    )
    def __str__(self):
        return f"{self.patient.name} - {self.created_at}"
    


#Clinic Schedule

class ClinicSchedule(models.Model):

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    DAY_CHOICES = [
    ('Monday','Monday'),
    ('Tuesday','Tuesday'),
    ('Wednesday','Wednesday'),
    ('Thursday','Thursday'),
    ('Friday','Friday'),
    ('Saturday','Saturday'),
    ('Sunday','Sunday'),
]

    day = models.CharField(max_length=10, choices=DAY_CHOICES)

    start_time = models.TimeField()

    end_time = models.TimeField()



    #Billing Model
class Bill(models.Model):

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    doctor = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True
    )
    referred_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referred_bills"
    )

    bill_number = models.CharField(max_length=20)


    test_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_mode = models.CharField(max_length=10, choices=PAYMENT_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bill_number} - {self.patient.name}"
    def save(self, *args, **kwargs):

        if not self.bill_number:
            last_bill = Bill.objects.filter(clinic=self.clinic).order_by('-id').first()

            if last_bill and last_bill.bill_number:
                last_num = int(last_bill.bill_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1001

            self.bill_number = f"FD-{new_num}"

        super().save(*args, **kwargs)
    

class BillItem(models.Model):

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="items"
    )

    item_name = models.CharField(max_length=200)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} - {self.amount}"


class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.code


class UserPermission(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
