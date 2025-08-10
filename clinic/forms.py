# clinic/forms.py
from django import forms
from .models import Appointment, Prescription, TestResult

class AppointmentForm(forms.ModelForm):
    """Form for booking an appointment"""
    class Meta:
        model = Appointment
        fields = ['doctor', 'timeslot', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class PrescriptionForm(forms.ModelForm):
    """Form for creating a prescription"""
    class Meta:
        model = Prescription
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class TestResultForm(forms.ModelForm):
    """Form for uploading a test result"""
    class Meta:
        model = TestResult
        fields = ['patient', 'file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
