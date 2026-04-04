from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from pathlib import Path
import os

from .models import Patient, Doctor, DiagnosisRecord, Appointment, Message, Feedback
from .ai_model import run_detection
from .utils.pdf_generator import generate_pdf_report


# ─── INDEX ───────────────────────────────────────────────────────────────────

def index(request):
    return render(request, 'index.html')


# ─── PATIENT AUTH ─────────────────────────────────────────────────────────────

def patient_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')
        username   = request.POST.get('username')
        email      = request.POST.get('email')
        password   = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'Patient/Patient-Side-Register.html',
                          {'error': 'Username already exists.'})

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        Patient.objects.create(user=user)
        login(request, user)
        return redirect('patient_main')

    return render(request, 'Patient/Patient-Side-Register.html')


def patient_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'patient_profile'):
            login(request, user)
            return redirect('patient_main')
        return render(request, 'Patient/Patient-Side-Login.html',
                      {'error': 'Invalid credentials.'})
    return render(request, 'Patient/Patient-Side-Login.html')


def patient_logout(request):
    logout(request)
    return redirect('index')


# ─── PATIENT VIEWS ────────────────────────────────────────────────────────────

@login_required
def patient_main(request):
    return render(request, 'Patient/Patient-Side-Main-Page.html',
                  {'patient': request.user.patient_profile})


@login_required
def patient_chat_with_ai(request):
    """Upload dental image → run YOLO detection → generate PDF report."""
    patient = request.user.patient_profile
    context = {'patient': patient}

    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']

        # Save record
        record = DiagnosisRecord.objects.create(
            patient=patient,
            uploaded_image=image_file,
            detection_json=[],
            detected_conditions=[],
        )

        # Run detection
        image_full_path = os.path.join(settings.MEDIA_ROOT, str(record.uploaded_image))
        try:
            result = run_detection(image_full_path)

            # Update record
            processed_rel = str(Path(result['annotated_image_path']).relative_to(settings.MEDIA_ROOT))
            record.processed_image = processed_rel
            record.detection_json  = result['detections']
            record.detected_conditions = result['conditions_found']
            record.save()

            # Generate PDF
            pdf_path = generate_pdf_report(patient, record)
            pdf_rel  = str(Path(pdf_path).relative_to(settings.MEDIA_ROOT))
            record.pdf_report = pdf_rel
            record.save()

            context.update({
                'result': result,
                'record': record,
                'pdf_url': settings.MEDIA_URL + pdf_rel,
            })

        except Exception as e:
            context['error'] = str(e)

    return render(request, 'Patient/Patient-Side-ChatWithAI.html', context)


@login_required
def patient_check_history(request):
    patient  = request.user.patient_profile
    diagnoses = DiagnosisRecord.objects.filter(patient=patient).order_by('-created_at')
    return render(request, 'Patient/Patient-Side-CheckHistory.html',
                  {'patient': patient, 'diagnoses': diagnoses})


@login_required
def patient_appointment(request):
    patient = request.user.patient_profile
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date      = request.POST.get('date')
        time      = request.POST.get('time')
        notes     = request.POST.get('notes', '')

        doctor = get_object_or_404(Doctor, id=doctor_id)
        Appointment.objects.create(
            patient=patient, doctor=doctor,
            date=date, appointment_time=time, notes=notes
        )
        return redirect('patient_appointment')

    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    return render(request, 'Patient/Patient-Side-Appointment.html',
                  {'patient': patient, 'doctors': doctors, 'appointments': appointments})


@login_required
def patient_chat_with_doctor(request):
    patient = request.user.patient_profile
    doctors = Doctor.objects.all()
    selected_doctor_id = request.GET.get('doctor_id')
    messages = []

    if selected_doctor_id:
        doctor = get_object_or_404(Doctor, id=selected_doctor_id)
        messages = Message.objects.filter(
            sender__in=[request.user, doctor.user],
            receiver__in=[request.user, doctor.user]
        ).order_by('timestamp')

        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            if content:
                Message.objects.create(
                    sender=request.user, receiver=doctor.user, content=content
                )
            return redirect(f'/patient/chat-doctor/?doctor_id={selected_doctor_id}')

    return render(request, 'Patient/Patient-Side-ChatWithDoctor.html',
                  {'patient': patient, 'doctors': doctors,
                   'messages': messages, 'selected_doctor_id': selected_doctor_id})


@login_required
def patient_feedback(request):
    patient = request.user.patient_profile
    if request.method == 'POST':
        rating  = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        Feedback.objects.create(patient=patient, rating=rating, comment=comment)
        return redirect('patient_main')
    return render(request, 'Patient/Patient-Side-Feedback.html', {'patient': patient})


@login_required
def patient_account(request):
    return render(request, 'Patient/Patient-Side-Account.html',
                  {'patient': request.user.patient_profile})


# ─── DOCTOR AUTH ──────────────────────────────────────────────────────────────

def doctor_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')

        if User.objects.filter(username=username).exists():
            return render(request, 'Doctor/Doctor-Side-Register.html',
                          {'error': 'Username already exists.'})

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        Doctor.objects.create(user=user)
        login(request, user)
        return redirect('doctor_dashboard')

    return render(request, 'Doctor/Doctor-Side-Register.html')


def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'doctor_profile'):
            login(request, user)
            return redirect('doctor_dashboard')
        return render(request, 'Doctor/Doctor-Side-Login.html',
                      {'error': 'Invalid credentials.'})
    return render(request, 'Doctor/Doctor-Side-Login.html')


def doctor_logout(request):
    logout(request)
    return redirect('index')


# ─── DOCTOR VIEWS ─────────────────────────────────────────────────────────────

@login_required
def doctor_dashboard(request):
    doctor = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date')[:5]
    patients = Patient.objects.all()
    return render(request, 'Doctor/Doctor-Side-Dashbord.html',
                  {'doctor': doctor, 'appointments': appointments,
                   'patient_count': patients.count()})


@login_required
def doctor_appointments(request):
    doctor = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date')

    if request.method == 'POST':
        apt_id = request.POST.get('appointment_id')
        status = request.POST.get('status')
        apt = get_object_or_404(Appointment, id=apt_id, doctor=doctor)
        apt.status = status
        apt.save()

    return render(request, 'Doctor/Doctor-Side-Appointments.html',
                  {'doctor': doctor, 'appointments': appointments})


@login_required
def doctor_patient_cases(request):
    doctor  = request.user.doctor_profile
    patients = Patient.objects.all()
    selected_patient_id = request.GET.get('patient_id')
    diagnoses = []

    if selected_patient_id:
        patient   = get_object_or_404(Patient, id=selected_patient_id)
        diagnoses = DiagnosisRecord.objects.filter(patient=patient).order_by('-created_at')

    return render(request, 'Doctor/Doctor-Side-Patient-Cases.html',
                  {'doctor': doctor, 'patients': patients,
                   'diagnoses': diagnoses, 'selected_patient_id': selected_patient_id})


@login_required
def doctor_patient_chat(request):
    doctor   = request.user.doctor_profile
    patients = Patient.objects.all()
    selected_patient_id = request.GET.get('patient_id')
    messages = []

    if selected_patient_id:
        patient  = get_object_or_404(Patient, id=selected_patient_id)
        messages = Message.objects.filter(
            sender__in=[request.user, patient.user],
            receiver__in=[request.user, patient.user]
        ).order_by('timestamp')

        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            if content:
                Message.objects.create(
                    sender=request.user, receiver=patient.user, content=content
                )
            return redirect(f'/doctor/chat/?patient_id={selected_patient_id}')

    return render(request, "Doctor/Doctor-Side-Patient's-display-chat.html",
                  {'doctor': doctor, 'patients': patients,
                   'messages': messages, 'selected_patient_id': selected_patient_id})
