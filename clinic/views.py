from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, Patient, TimeSlot, Appointment, Prescription
from .forms import AppointmentForm, PrescriptionForm, TestResultForm
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
import datetime

def doctors_list(request):
    doctors = Doctor.objects.select_related('specialty').all()
    return render(request, 'clinic/doctors_list.html', {'doctors': doctors})

def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    timeslots = doctor.timeslots.filter(date__gte=datetime.date.today()).order_by('date','start')
    return render(request, 'clinic/doctor_detail.html', {'doctor': doctor, 'timeslots': timeslots})

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            ap = form.save(commit=False)
            # assume the patient profile exists for logged-in user
            patient = getattr(request.user, 'patient', None)
            if not patient:
                messages.error(request, 'No patient profile linked to your user.')
                return redirect('clinic:doctor_detail', pk=doctor_id)
            ap.patient = patient
            # conflict detection: check capacity
            slot = ap.timeslot
            existing = Appointment.objects.filter(timeslot=slot, status='scheduled').count()
            if existing >= slot.capacity:
                messages.error(request, 'This time slot is full. Please choose another slot.')
                return redirect('clinic:doctor_detail', pk=doctor_id)
            ap.doctor = doctor
            ap.save()
            # send email reminder (simple)
            try:
                send_mail(
                    'Appointment Scheduled',
                    f'Your appointment with Dr. {doctor.full_name} on {slot.date} at {slot.start} is scheduled.',
                    settings.DEFAULT_FROM_EMAIL,
                    [patient.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Appointment booked successfully')
            return redirect('clinic:my_appointments')
    else:
        form = AppointmentForm(initial={'doctor': doctor})
    return render(request, 'clinic/book_appointment.html', {'form': form, 'doctor': doctor})

@login_required
def my_appointments(request):
    patient = getattr(request.user, 'patient', None)
    if not patient:
        messages.error(request, 'No patient profile linked to your account.')
        return redirect('clinic:doctors_list')
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor','timeslot')
    return render(request, 'clinic/my_appointments.html', {'appointments': appointments})

@login_required
def prescription_create(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            pres = form.save(commit=False)
            pres.appointment = appointment
            pres.save()
            messages.success(request, 'Prescription saved')
            return redirect('clinic:appointment_detail', pk=appointment.id)
    else:
        form = PrescriptionForm()
    return render(request, 'clinic/prescription_form.html', {'form': form, 'appointment': appointment})

@login_required
def appointment_detail(request, pk):
    ap = get_object_or_404(Appointment, pk=pk)
    return render(request, 'clinic/appointment_detail.html', {'appointment': ap})

@login_required
def upload_test_result(request):
    if request.method == 'POST':
        form = TestResultForm(request.POST, request.FILES)
        if form.is_valid():
            tr = form.save(commit=False)
            tr.uploaded_by = request.user
            tr.save()
            messages.success(request, 'Test result uploaded')
            return redirect('clinic:my_appointments')
    else:
        form = TestResultForm()
    return render(request, 'clinic/upload_test_result.html', {'form': form})

@login_required
def daily_report(request):
    today = datetime.date.today()
    appointments = Appointment.objects.filter(timeslot__date=today).select_related('patient','doctor','timeslot')
    # CSV response
    if request.GET.get('format') == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="appointments_{today}.csv"'
        writer = csv.writer(response)
        writer.writerow(['patient','doctor','date','start','status'])
        for a in appointments:
            writer.writerow([a.patient.full_name, a.doctor.full_name, a.timeslot.date, a.timeslot.start, a.status])
        return response
    return render(request, 'clinic/daily_report.html', {'appointments': appointments, 'today': today})
