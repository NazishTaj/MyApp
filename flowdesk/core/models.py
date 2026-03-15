from django.db import models
from django.contrib.auth.models import User


# Clinic Model
class Clinic(models.Model):
    name = models.CharField(max_length=200)
   # doctor_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    logo = models.ImageField(upload_to="clinic_logos/", blank=True, null=True)
    billing_enabled = models.BooleanField(default=False)
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.name


# User Profile (Doctor Login → Clinic Link)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="doctor_photos/", blank=True, null=True)
    def __str__(self):
        return self.user.username


# Patient Model

from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be exactly 10 digits"
)

class Patient(models.Model):

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    address = models.TextField(blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    token_number = models.PositiveIntegerField(blank=True, null=True)

    problem = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'token_number']

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

    created_at = models.DateField(auto_now_add=True)

    blood_group = models.CharField(max_length=5, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)

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
