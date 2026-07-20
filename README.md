# eKYC — Electronic Know Your Customer

A secure identity verification system built with Django. Integrates face detection (MTCNN), face recognition (ArcFace), and OCR (Tesseract) to enroll, verify, and serve student identity data through a field-level access-controlled REST API.

## Features

- **Face Registration & Recognition** — Detects faces via MTCNN (OpenCV DNN), extracts 512‑dim embeddings with ArcFace (ONNX Runtime), and matches against a local facebank
- **ID Card OCR** — Extracts National ID numbers from ID card images using Tesseract
- **Student Enrollment** — Full CRUD for students with academic, personal, economic, and course data; CGPA auto‑computed from grades
- **Field‑Level API Access Control** — Each API consumer (Customer) is assigned a key and a comma‑separated list of accessible fields; the REST API dynamically filters responses
- **Private File Storage** — Student images served via `django-private-storage`, not directly accessible
- **Admin Dashboard** — Bootstrap 4 UI for managing students, customers, and facebank data

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 3.2.9, Django REST Framework 3.12.4 |
| Face Detection | MTCNN via OpenCV DNN (P‑Net / R‑Net / O‑Net ONNX models) |
| Face Recognition | ArcFace (ResNet backbone) via ONNX Runtime |
| OCR | Tesseract via `pytesseract` |
| Tensor Ops | PyTorch 1.7.1, NumPy, scikit‑learn |
| File Serving | `django-private-storage` 3.0 |
| Frontend | Bootstrap 4 (CDN) |
| Database | SQLite3 (default; swappable) |

## Project Structure

```
electronic-Know-Your-Customer/
├── eKYC/                        # Django project configuration (settings, root URLs)
├── enrollment_data_show/        # Core app: models, views, templates, facebank management
│   ├── checkpoints/facedetector/  # RetinaFace Caffe model (legacy)
│   ├── templates/               # Bootstrap 4 HTML templates
│   └── templatetags/            # Custom template filters
├── FACE_RECOGNITION/            # Standalone Python module
│   ├── FR/Recognition.py        # FaceModel — ArcFace embedding + facebank I/O
│   ├── mtcnn_cv2/               # MTCNN detection, alignment, cropping
│   └── OCR/ocr.py               # ID card text extraction
├── rest_api/                    # REST API app (serializers, views, URLs)
├── manage.py
└── requirements.txt
```

## Prerequisites

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and available on `PATH`
- Model weight files (not tracked in git):
  - `enrollment_data_show/checkpoints/facebank/arcface.onnx`
  - `FACE_RECOGNITION/mtcnn_cv2/pnet.onnx`, `rnet.onnx`, `onet.onnx`

## Installation

```bash
# 1. Clone the repository
git clone <repo-url> && cd electronic-Know-Your-Customer

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic

# 6. Create a superuser (admin dashboard)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

## Usage

### Admin Workflow

1. **Login** — Navigate to `/admin_login/` and authenticate with your superuser credentials
2. **Create an API Customer** — Go to `/create_customer/`, enter a name, and select which student fields the customer is allowed to access. An auto‑generated 16‑char hex key is assigned.
3. **Enroll a Student** — Go to `/enter_student_data/`. Fill in all academic, personal, economic, and course information, and upload a **single‑face** photo. MTCNN detects the face, ArcFace registers the embedding in the facebank, and the student record is created with CGPA auto‑calculated.
4. **Manage Records** — View, update, or delete students and customers through the admin interface. The facebank can be wiped via `/delete_facebank_data/`.

### API Consumer Workflow

1. Retrieve your assigned **Customer Key** from the admin
2. Query student data via the REST endpoint:

```
GET /rest_api/view_student_info_customer_end/<customer_key>/<student_id>/
```

The response is a JSON list containing the matched student's data, **dynamically filtered** to only include fields the customer is authorized to see.

**Example (customer with access to `name`, `email`, `department`):**

```json
[
  {
    "nsuID": 12345,
    "name": "John Doe",
    "email": "john@example.com",
    "department": "Computer Science"
  }
]
```

If the student is not found or the key is invalid, a 404 is returned.

## Face Recognition Pipeline

```
Input Image → MTCNN (OpenCV DNN)
                ├── P‑Net: propose candidate face regions
                ├── R‑Net: refine bounding boxes
                └── O‑Net: output 5 facial landmarks
             → Similarity Transform (align & crop to 112×112)
             → ArcFace (ONNX Runtime) → 512‑dim embedding
             → L2 distance vs facebank entries
             → Match if distance < 0.93, otherwise "unknown"
```

During enrollment the embedding is added to `facebank.pth` and the label to `names.npy`, both stored under `checkpoints/facebank/`.

## OCR (ID Card Parsing)

Located in `FACE_RECOGNITION/OCR/ocr.py`. The `detect_id(image)` function:
1. Resizes the image to 1024×665
2. Splits it into 4 horizontal strips
3. Applies grayscale → binary threshold → median blur → Tesseract OCR on each strip
4. Extracts a 10‑digit National ID number via regex

*Note: This module is currently not wired into any view or API endpoint.*

## Database Schema

```
Student (PK: nsuID)
├── image              — PrivateFileField (served via /private-media/)
├── name, email, birth_certificate_number, department, majorIn, enrolled_in, cgpa
├── sscPassYear, sscGpa, hscPassYear, hscGpa
├── ── course_info     — OneToOne → CourseInfo
│                          ├── courses (comma‑separated)
│                          ├── creditHours (comma‑separated)
│                          ├── creditPassed
│                          └── grades (comma‑separated)
├── ── personal_info   — OneToOne → PersonalInfo (DOB, gender, blood group, marital status,
│                          phone, parents' details, address)
└── ── economic_info   — OneToOne → EconomicInfo (NID, occupation, income, bank account)

Customer (API access control)
├── customer_name
├── accessible_fields  — comma‑separated field names
└── key                — auto‑generated 16‑char hex UUID
```

When a `Student` is deleted, a `pre_delete` signal removes its uploaded image file and directory. The related `CourseInfo`, `PersonalInfo`, and `EconomicInfo` records are cascade‑deleted by the database.

## Security

- **Secret Key** — Currently exposed in `settings.py`. Rotate before deploying to production.
- **DEBUG** — Set to `True` in development; must be `False` in production.
- **ALLOWED_HOSTS** — Empty by default; configure for your domain.
- **Private Media** — Student photos are stored under `media/private-media/` and served via `django-private-storage` at `/private-media/` (login required).
- **API Authentication** — Each request to the REST API is authenticated via a `Customer.key` lookup. Responses are filtered to the customer's `accessible_fields` at the DRF serializer level — no raw model data is leaked.

## Production Checklist

- [ ] Generate a new `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Switch to a production database (PostgreSQL recommended)
- [ ] Set up proper static/media file serving (e.g., Nginx / S3)
- [ ] Add CORS headers (`django-cors-headers`) if the API is consumed from a different origin
- [ ] Enable HTTPS
- [ ] Add authentication throttling to the API endpoint

## Development

- **Tests** — Both `enrollment_data_show/tests.py` and `rest_api/tests.py` are empty stubs. Contributions welcome.
- **Requirements** — The `requirements.txt` file uses UCS‑2 LE encoding; handle accordingly if parsing programmatically.
