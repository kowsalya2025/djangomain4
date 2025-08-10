from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=200)
    specialty = models.ForeignKey(Specialty, related_name='doctors', on_delete=models.SET_NULL, null=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='doctors/', null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialty})"

class Patient(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=200)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='timeslots', on_delete=models.CASCADE)
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    capacity = models.PositiveSmallIntegerField(default=1)  # how many patients per slot

    class Meta:
        unique_together = ('doctor','date','start')

    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start}-{self.end}"

class Appointment(models.Model):
    STATUS_CHOICES = [('scheduled','Scheduled'), ('cancelled','Cancelled'), ('completed','Completed')]
    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, related_name='appointments', on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient','timeslot')

    def __str__(self):
        return f"{self.patient} with {self.doctor} at {self.timeslot}"

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, related_name='prescription', on_delete=models.CASCADE)
    prescribed_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    file = models.FileField(upload_to='prescriptions/', null=True, blank=True)

    def __str__(self):
        return f"Prescription for {self.appointment}"

class TestResult(models.Model):
    patient = models.ForeignKey(Patient, related_name='test_results', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='test_results/')
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TestResult {self.id} for {self.patient}"

# ---------- clinic/admin.py ----------
from django.contrib import admin
from .models import Specialty, Doctor, Patient, TimeSlot, Appointment, Prescription, TestResult

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name','specialty','phone')
    search_fields = ('full_name','specialty__name')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name','phone','email')
    search_fields = ('full_name','phone','email')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor','date','start','end','capacity')
    list_filter = ('doctor','date')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient','doctor','timeslot','status','created_at')
    list_filter = ('status','doctor')

admin.site.register(Prescription)
admin.site.register(TestResult)

# ---------- clinic/forms.py ----------
from django import forms
from .models import Appointment, Prescription, TestResult
from django.forms import DateInput, TimeInput

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor','timeslot','reason']

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['content','file']

class TestResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['patient','file','notes']

