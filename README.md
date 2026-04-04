# AIDentify — AI Dental Diagnosis System

A full-stack web application that uses **YOLOv8 object detection** to diagnose dental conditions from patient images, generating detailed PDF diagnostic reports.

Built as a graduation project at Umm Al-Qura University.

---

## Demo

> Patient uploads a dental photo → AI detects conditions → PDF report is generated and saved

**Detected Conditions:**
- 🦷 Caries (Tooth Decay)
- 🔴 Gingivitis
- 🪨 Tartar (Calculus)
- 🫧 Mouth Ulcers

---

## Features

### Patient Side
- Register / Login
- Upload dental image for AI diagnosis
- View detection results with confidence scores
- Download PDF diagnostic report
- View full diagnosis history
- Book appointments with doctors
- Chat with doctor
- Submit feedback

### Doctor Side
- Dashboard with patient statistics
- View and manage appointments
- Access patient diagnosis cases and reports
- Chat with patients

### AI Engine
- YOLOv8 trained on ~10,000 dental images
- Multi-label detection (detects multiple conditions in a single scan)
- **99.3% accuracy** on unseen test data
- Auto-generates annotated images and structured JSON detection logs
- PDF report generation via ReportLab

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| AI Model | YOLOv8 (Ultralytics) |
| Database | SQLite |
| PDF Generation | ReportLab |
| Frontend | HTML / CSS / JavaScript |
| API | Django REST Framework |

---

## Project Structure

```
aididentify_backend/
├── aididentify_backend/     # Django project config
│   ├── settings.py
│   └── urls.py
├── api/
│   ├── models.py            # Patient, Doctor, DiagnosisRecord, Appointment, Message, Feedback
│   ├── views.py             # All patient and doctor views
│   ├── urls.py              # URL routing
│   ├── ai_model.py          # YOLOv8 inference engine
│   ├── utils/
│   │   └── pdf_generator.py # ReportLab PDF report builder
│   ├── models/
│   │   └── best.pt          # ← Place your trained model here (not included in repo)
│   └── templates/
│       ├── Patient/         # Patient-side HTML templates
│       └── Doctor/          # Doctor-side HTML templates
├── media/                   # Generated at runtime (gitignored)
│   ├── uploads/             # Patient uploaded images
│   ├── processed/           # YOLO-annotated images
│   ├── reports/             # Generated PDF reports
│   └── detections/          # Detection JSON logs
├── manage.py
└── requirements.txt
```

---

## Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/MaherQ11/AI-Dental-Diagnosis.git
cd AI-Dental-Diagnosis

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place the trained model
# Download best.pt and place it at: api/models/best.pt

# 5. Run migrations
python manage.py migrate

# 6. Start the server
python manage.py runserver
```

Then open: [http://localhost:8000](http://localhost:8000)

---

## Model

The YOLOv8 model (`best.pt`) is not included in this repository due to file size.

- **Architecture:** YOLOv8
- **Dataset:** ~10,000 labeled dental images (sourced from Kaggle)
- **Classes:** 4 (Caries, Gingivitis, Tartar, Mouth Ulcer)
- **Preprocessing:** Removed and relabeled a 5th class (discoloration) to improve precision
- **Accuracy:** 99.3% on held-out test set

---

## Author

**Maher Al-Qurashi**
- GitHub: [@MaherQ11](https://github.com/MaherQ11)
- LinkedIn: [maher-al-qurashi](https://www.linkedin.com/in/maher-al-qurashi-69a163351/)

---

## Disclaimer

This system is intended for **preliminary screening purposes only**. Always consult a licensed dentist for professional diagnosis and treatment.
