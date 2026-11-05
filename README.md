# 🛡 DeepGuard – AI-Powered Deepfake Detection & Media Forensics System

> A professional full-stack deepfake detection web application powered by TensorFlow, Flask, OpenCV, and MongoDB.

---

## 1. Project Introduction

**DeepGuard** is an end-to-end AI-powered media forensics system designed to detect:

- **AI-Generated Images** (e.g., from DALL-E, Midjourney, Stable Diffusion)
- **Deepfake / Face-Manipulated Videos** (e.g., FaceSwap, DeepFaceLab)

The system uses two separate CNN-based detection pipelines — one for images, one for video frames — and provides confidence scores, detailed technical analysis, frame-by-frame timelines, EXIF metadata extraction, SHA-256 file hashing, and professional downloadable PDF forensic reports.

---

## 2. Project Objectives

- Build a production-ready deepfake detection system as an M.Sc. IT final-year project
- Implement genuine TensorFlow/Keras CNN models — no fabricated predictions
- Create a premium SaaS-quality UI with the DeepGuard color palette
- Generate professional 3-page PDF forensic reports per analysis
- Provide transparent model limitations and probabilistic disclaimers

---

## 3. Main Features

| Feature | Description |
|---|---|
| Image Detection | CNN model analyses uploaded JPG/PNG/WEBP for AI generation |
| Video Detection | Frame-by-frame deepfake analysis with aggregation strategy |
| Analytics Dashboard | Chart.js charts: Real vs Fake, weekly activity, media type |
| PDF Report Cards | 3-page professional forensic reports via ReportLab |
| Analysis History | Searchable, filterable, paginated history per user |
| Report Center | Download all generated PDF reports |
| EXIF Metadata | Extracts camera make/model, DateTime, GPS from image EXIF |
| SHA-256 Hashing | Every uploaded file is hashed and stored in MongoDB |
| Admin Dashboard | System-wide stats, user list, model status monitoring |
| Secure Auth | Bcrypt hashing, Flask-Login sessions, protected routes |

---

## 4. Technology Stack

**Frontend:** HTML5, CSS3, JavaScript ES6, Bootstrap 5, Chart.js, Font Awesome, Jinja2

**Backend:** Python 3, Flask, Flask-Login, Flask-CORS, Werkzeug

**AI/ML:** TensorFlow 2, Keras CNN, OpenCV, NumPy, Pillow, Scikit-learn

**Database:** MongoDB, PyMongo

**PDF:** ReportLab

**Tools:** Git, VS Code, Google Antigravity

---

## 5. System Architecture

```
User Browser
    │
    ▼
Flask App (app.py)
    │
    ├── routes/         ← Blueprint route handlers
    ├── services/       ← Business logic (preprocessing, prediction, PDF)
    ├── models/         ← Keras model loader + .keras files
    ├── database/       ← MongoDB connection + indexes
    └── templates/      ← Jinja2 HTML templates
         │
         ├── MongoDB ── (users, analyses, reports, model_versions)
         └── TensorFlow CNN ── image_detector.keras / video_detector.keras
```

---

## 6. Project Folder Structure

```
DeepGuard/
├── app.py                      # Flask application factory + entry point
├── config.py                   # Configuration (env vars)
├── requirements.txt
├── .env                        # Local secrets (not committed)
├── .env.example
├── .gitignore
├── README.md
│
├── models/
│   ├── image_detector.keras    # Trained image CNN (place after training)
│   ├── video_detector.keras    # Trained video CNN (place after training)
│   └── model_loader.py         # Lazy model cache + availability check
│
├── routes/
│   ├── auth_routes.py
│   ├── dashboard_routes.py
│   ├── image_routes.py
│   ├── video_routes.py
│   ├── result_routes.py
│   ├── history_routes.py
│   ├── report_routes.py
│   ├── profile_routes.py
│   └── admin_routes.py
│
├── services/
│   ├── image_preprocessing.py
│   ├── image_prediction.py
│   ├── video_processing.py
│   ├── video_prediction.py
│   ├── metadata_analysis.py
│   ├── hash_service.py
│   ├── report_generator.py
│   └── analysis_service.py
│
├── database/
│   └── db.py
│
├── training/
│   ├── train_image_model.py    # CIFAKE training script
│   ├── train_video_model.py    # FF++ training script
│   ├── evaluate_model.py
│   └── dataset_loader.py
│
├── templates/
│   ├── base.html               # Sidebar layout
│   ├── index.html              # Landing page
│   ├── login.html / register.html
│   ├── dashboard.html
│   ├── image_detection.html
│   ├── video_detection.html
│   ├── result.html
│   ├── history.html
│   ├── reports.html
│   ├── profile.html
│   ├── admin_dashboard.html
│   ├── admin_users.html
│   └── errors/ (403, 404, 500)
│
├── static/
│   ├── css/ (style.css, dashboard.css, responsive.css)
│   ├── js/  (main.js, charts.js, image_detection.js, video_detection.js)
│   └── images/
│
├── uploads/                    # User-isolated uploaded media (gitignored)
├── reports/                    # Generated PDF reports (gitignored)
├── dataset/                    # Training datasets (gitignored)
└── tests/
    ├── test_auth.py
    ├── test_detection.py
    ├── test_reports.py
    └── test_database.py
```

---

## 7. Installation Requirements

- Python 3.10+
- MongoDB 6.0+ (Community Edition)
- Git

---

## 8. Python Virtual Environment Setup

```bash
# Clone the repo
git clone https://github.com/your-username/deepguard.git
cd deepguard

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 9. MongoDB Configuration

1. Install MongoDB Community Edition from https://www.mongodb.com/try/download/community
2. Start MongoDB service:

```bash
# Windows (run as administrator)
net start MongoDB

# Linux / macOS
sudo systemctl start mongod
```

3. Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-very-secret-key-here
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=deepguard_db
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
MAX_CONTENT_LENGTH=104857600
```

The application will create collections and indexes automatically on first connection.

---

## 10. Dataset Setup

### A. Image Detection – CIFAKE

**Dataset:** CIFAKE: Real and AI-Generated Synthetic Images  
**Source:** https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images  
**License:** Creative Commons (verify on Kaggle)

```bash
# Install Kaggle CLI
pip install kaggle

# Place your kaggle.json at ~/.kaggle/kaggle.json
# Then run:
python training/dataset_loader.py --action download_cifake
```

The dataset will be organised as:
```
dataset/image/train/REAL/
dataset/image/train/FAKE/
dataset/image/test/REAL/
dataset/image/test/FAKE/
```

### B. Video Detection – FaceForensics++

**Dataset:** FaceForensics++  
**Source:** https://github.com/ondyari/FaceForensics  
**License:** Academic / Non-commercial – requires author approval

1. Complete the access request form at the FF++ GitHub repository
2. Download the dataset per their instructions
3. Extract face crops using:
```bash
# Extracts face crops from raw videos into dataset/video/
python training/dataset_loader.py --action split
```

Expected structure:
```
dataset/video/train/REAL/
dataset/video/train/FAKE/
dataset/video/test/REAL/
dataset/video/test/FAKE/
```

---

## 11. Model Training Instructions

### Train Image Model (CIFAKE)

```bash
python training/train_image_model.py
```

Training details:
- Architecture: Custom CNN (4 Conv blocks + GlobalAveragePooling + Dense head)
- Input: 224 × 224 RGB
- Output: Sigmoid (1 = Fake, 0 = Real)
- Callbacks: EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
- Saves to: `models/image_detector.keras`

### Train Video Model (FF++)

```bash
python training/train_video_model.py
```

### Evaluate a Model

```bash
python training/evaluate_model.py --model image
python training/evaluate_model.py --model video
```

Outputs: Accuracy, Precision, Recall, F1-score, Confusion Matrix, ROC-AUC

---

## 12. Model Integration

Once trained, the models are automatically loaded by `models/model_loader.py` when the Flask app starts. No extra configuration needed.

If the model files are missing:
- The detection pages will show a clear **"Model Not Available"** notice
- Analysis records will be saved with `status: model_unavailable`
- PDF reports will not be generated for unavailable-model analyses

---

## 13. Application Execution

```bash
# Activate virtual environment first
venv\Scripts\activate   # Windows

# Run the Flask development server
python app.py
```

The application will start at: **http://localhost:5000**

### Create an Admin Account

Register normally via the UI, then update your role in MongoDB:

```javascript
// In MongoDB shell or Compass
use deepguard_db
db.users.updateOne({ email: "admin@example.com" }, { $set: { role: "admin" } })
```

---

## 14. Testing Instructions

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/ -v

# Run individual test files
pytest tests/test_auth.py -v
pytest tests/test_detection.py -v
pytest tests/test_database.py -v
pytest tests/test_reports.py -v
```

> **Note:** Tests marked with `pytest.skip` require a running MongoDB instance.

---

## 15. PDF Report Generation

1. Upload and analyse a file (image or video)
2. On the result page, click **"Generate PDF Report"**
3. The report is saved to `reports/DG-<ID>.pdf` and recorded in MongoDB
4. Download the report from the result page or the **Report Center**

Each PDF contains:
- **Page 1:** Cover, user info, media info, detection summary
- **Page 2:** Technical analysis (EXIF/frame table)
- **Page 3:** Probability pie chart, conclusion, disclaimer

---

## 16. Screenshots

> Add screenshots of your running application here after deployment.

- Landing page
- Login / Register
- User Dashboard with charts
- Image Detection upload
- Detection Result page
- PDF Report sample
- Analysis History
- Admin Dashboard

---

## 17. Future Enhancements

| Enhancement | Description |
|---|---|
| Grad-CAM Heatmaps | Overlay CNN attention maps on the result image |
| Transfer Learning | Fine-tune EfficientNet or ResNet50 for higher accuracy |
| Email Alerts | Send detection reports to users via email |
| API Endpoints | REST API for programmatic media submission |
| Batch Analysis | Analyse multiple files in a single request |
| Video Face Detection | Integrate RetinaFace for more accurate face crops |
| Real-time Detection | WebSocket-based live frame analysis |
| Cloud Storage | Store uploads on AWS S3 or Google Cloud Storage |

---

## Disclaimer

> This system uses AI-based probabilistic detection. Results are not forensic proof of media authenticity or manipulation. Always corroborate results with additional investigative methods.

---

**DeepGuard – AI-Powered Deepfake Detection & Media Forensics System**  
Built with TensorFlow · Flask · MongoDB · OpenCV · ReportLab
