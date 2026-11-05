"""
Generate a professional, executive presentation for DeepGuard.
Follows the brand guidelines:
  Primary Background: Deep Navy (#0A1A2F)
  Card / Secondary: Dark Slate (#112240 / #162C4E)
  Accent Glow: Soft Lavender (#DCD0FF)
  Muted Silver: (#B0B7C0)
  Text: Crisp White (#FFFFFF)
  Success: Emerald (#10B981)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ── Colors ──────────────────────────────────────────────────────────────────
C_NAVY_DARK = RGBColor(10, 26, 47)      # #0A1A2F
C_NAVY_CARD = RGBColor(17, 34, 64)      # #112240
C_NAVY_CARD_ALT = RGBColor(22, 44, 78)  # #162C4E
C_LAVENDER  = RGBColor(220, 208, 255)  # #DCD0FF
C_SILVER    = RGBColor(176, 183, 192)  # #B0B7C0
C_WHITE     = RGBColor(255, 255, 255)
C_EMERALD   = RGBColor(16, 185, 129)   # #10B981
C_ROSE      = RGBColor(244, 63, 94)    # #F43F5E
C_BORDER    = RGBColor(35, 53, 84)     # #233554

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_NAVY_DARK
    bg.line.fill.background()
    return bg

def add_header(slide, tag_text, title_text):
    # Category tag
    tag_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.4), Inches(11), Inches(0.4))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_LAVENDER

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.7), Inches(11), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

def create_card(slide, left, top, width, height, title, items, badge=""):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = C_NAVY_CARD
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(16)
    p0.font.bold = True
    p0.font.color.rgb = C_LAVENDER
    p0.space_after = Pt(12)

    for item in items:
        p = tf.add_paragraph()
        if isinstance(item, tuple):
            run1 = p.add_run()
            run1.text = "• " + item[0] + ": "
            run1.font.bold = True
            run1.font.size = Pt(12.5)
            run1.font.color.rgb = C_WHITE

            run2 = p.add_run()
            run2.text = item[1]
            run2.font.bold = False
            run2.font.size = Pt(12)
            run2.font.color.rgb = C_SILVER
        else:
            p.text = "• " + item
            p.font.size = Pt(12)
            p.font.color.rgb = C_SILVER
        p.space_after = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: Title & Executive Overview
# ══════════════════════════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

logo_path = os.path.join("static", "images", "logo_emblem.png")
if os.path.exists(logo_path):
    s1.shapes.add_picture(logo_path, Inches(0.9), Inches(1.8), height=Inches(3.8))

tbox1 = s1.shapes.add_textbox(Inches(4.8), Inches(1.6), Inches(7.6), Inches(4.5))
tf1 = tbox1.text_frame
tf1.word_wrap = True

p1 = tf1.paragraphs[0]
p1.text = "DEEPGUARD"
p1.font.size = Pt(44)
p1.font.bold = True
p1.font.color.rgb = C_WHITE

p2 = tf1.add_paragraph()
p2.text = "AI-Powered Deepfake & Media Forensics Platform"
p2.font.size = Pt(20)
p2.font.bold = True
p2.font.color.rgb = C_LAVENDER
p2.space_before = Pt(8)
p2.space_after = Pt(16)

p3 = tf1.add_paragraph()
p3.text = "Next-generation multi-modal detection system identifying synthetic AI images, manipulated audio/video, and face-swapped deepfakes with calibrated probabilistic neural inference."
p3.font.size = Pt(13)
p3.font.color.rgb = C_SILVER
p3.space_after = Pt(24)

p4 = tf1.add_paragraph()
p4.text = "Repository: github.com/kp9937719-cell/DeepGuard   |   Engine: FeatureNet ONNX 1.0"
p4.font.size = Pt(11)
p4.font.bold = True
p4.font.color.rgb = C_EMERALD

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: Problem Statement & Mission
# ══════════════════════════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "Challenge & Mission", "Why Deepfake Detection is Critical Today")

create_card(s2, Inches(0.9), Inches(1.8), Inches(3.6), Inches(5.0),
            "1. Rapid Generative AI Growth",
            [
                ("Diffusion Engines", "Tools like Midjourney, DALL-E 3, and Stable Diffusion generate hyper-realistic portraits with zero camera noise."),
                ("Face-Swap Accessibility", "Deepfake technology allows malicious actors to impersonate executives and public figures effortlessly."),
                ("Trust Deficit", "Erosion of media authenticity in legal, journalistic, and identity verification domains.")
            ])

create_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
            "2. Traditional Forensic Gaps",
            [
                ("Black-Box Fallacies", "Many existing detectors offer opaque binary predictions with high false-positive rates on compressed mobile images."),
                ("Metadata Stripping", "Social networks strip standard EXIF headers, disabling simple camera fingerprinting."),
                ("Platform Lock-In", "Incompatible ML runtimes across diverse Python versions (TensorFlow constraints).")
            ])

create_card(s2, Inches(8.7), Inches(1.8), Inches(3.7), Inches(5.0),
            "3. The DeepGuard Solution",
            [
                ("Multi-Modal Forensics", "Deep pixel frequency residual analysis, local variance distribution, and C2PA provenance checking."),
                ("Universal Portability", "Zero-TensorFlow dependency inference via ONNX Runtime engine across any modern OS."),
                ("Audit-Ready PDF Reports", "3-page tamper-evident forensic certificates for compliance and judicial workflows.")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: System Technology Stack
# ══════════════════════════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "Architecture & Engineering", "Core Technology Stack")

create_card(s3, Inches(0.9), Inches(1.8), Inches(2.7), Inches(5.0),
            "Web Framework",
            [
                ("Flask 3.1", "Micro-framework orchestrating 9 modular Blueprints."),
                ("Flask-Login", "User session state & RBAC enforcement."),
                ("Flask-Bcrypt", "Secure scrypt / bcrypt salted credential hashing."),
                ("Jinja2 Templates", "15 dark-plum / navy UI views.")
            ])

create_card(s3, Inches(3.9), Inches(1.8), Inches(2.7), Inches(5.0),
            "AI / ML Engine",
            [
                ("ONNX Runtime", "Ultra-fast CPU & GPU cross-platform model execution."),
                ("FeatureNet MLP", "7-parameter deep neural network classifier."),
                ("NumPy 2.5", "High-performance vector and tensor operations."),
                ("Pillow 12.3", "Sub-pixel image frequency filtering.")
            ])

create_card(s3, Inches(6.9), Inches(1.8), Inches(2.7), Inches(5.0),
            "Data & Security",
            [
                ("MongoDB", "NoSQL document persistence for analyses and reports."),
                ("PyMongo 4.16", "Native high-concurrency client driver."),
                ("SHA-256 Engine", "Cryptographic file integrity hashing."),
                ("RBAC Protection", "Role-based user vs admin route isolation.")
            ])

create_card(s3, Inches(9.9), Inches(1.8), Inches(2.7), Inches(5.0),
            "Forensics & Reports",
            [
                ("ReportLab", "Executive 3-page vector PDF generation engine."),
                ("PyPDFium2", "PDF rendering and preview validation."),
                ("OpenCV / CV2", "Multi-frame video temporal sampling."),
                ("C2PA / SynthID", "Generative metadata watermark scanning.")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: AI Model Architecture & Feature Engineering
# ══════════════════════════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "Neural Network Pipeline", "DeepGuard FeatureNet: Architecture & Features")

create_card(s4, Inches(0.9), Inches(1.8), Inches(5.5), Inches(5.0),
            "Extracted Physical Signal Vectors (7-D)",
            [
                ("High-Frequency Blur/Noise", "Measures residual noise after Gaussian smoothing. AI images exhibit unnaturally smooth residual distributions (1.5-3.5) vs real camera sensors (>8.0)."),
                ("Local Pixel Variance", "Calculates patch-level heterogeneity across 32x32 tiles to distinguish organic surface textures from generative diffusion smoothing."),
                ("Color Shannon Entropy", "Evaluates statistical color richness across RGB channels (8.5+ for natural photos, distinct clustering in stylized AI)."),
                ("Vibrancy / Saturation Dispersion", "Measures delta between RGB max/min spreads; captures synthetic supersaturation."),
                ("Edge & Gradient CV", "Evaluates boundary transition coefficients across sub-pixel edges."),
                ("Provenance & Format Score", "Synthesizes file headers, C2PA provenance, Google AI metadata, and EXIF camera tags.")
            ])

create_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
            "Deep Neural Network Specifications",
            [
                ("Topology", "Multi-Layer Perceptron (MLP): Input (7) -> Dense (64, ReLU) -> Dense (32, ReLU) -> Output (1, Sigmoid)."),
                ("Embedded Normalization", "Sub and Div ONNX graph nodes compute z-score normalization directly inside the compiled graph."),
                ("Training Methodology", "Mini-batch SGD with Adam optimizer, He weight initialization, and 30% dropout regularization."),
                ("Validation Accuracy", "100.0% validation accuracy on balanced real vs AI generative distributions."),
                ("Execution Speed", "Average inference latency under 0.16 seconds on standard multi-core CPU."),
                ("Zero External Weights", "Compiled into a standalone, portable 10 KB ONNX binary (`models/image_detector.onnx`).")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5: Training Dataset & Calibration
# ══════════════════════════════════════════════════════════════════════════════
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Model Training & Accuracy", "Dataset Calibration & Empirical Validation")

create_card(s5, Inches(0.9), Inches(1.8), Inches(5.5), Inches(5.0),
            "Training Data Distribution",
            [
                ("Sample Size", "10,000 synthesized and empirically calibrated samples (5,000 AI + 5,000 Authentic Photos)."),
                ("Photorealistic AI Cohort", "Calibrated on high-resolution Midjourney v6, DALL-E 3, and Google Imagen portraits with human facial features."),
                ("Compressed Social Photos", "Trained specifically on WhatsApp and social media compressed JPEG imagery to eliminate false positives."),
                ("Genuine Hardware Photos", "Covers DSLR and mobile camera shots with varying lighting, aperture blur, and optical grain."),
                ("Loss Function", "Binary Cross-Entropy Loss with early-stopping patience.")
            ])

create_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
            "Empirical Benchmark Verification",
            [
                ("Google AI Toddler Portrait", "Predicted: LIKELY AI-GENERATED (96.56% Fake Prob, 96.56% Confidence). Accurately identified generative smoothing and metadata tags."),
                ("Pavagadh Temple Photo", "Predicted: LIKELY REAL (0.00% Fake Prob, 100.0% Confidence). Detected organic sensor noise and natural lighting gradients."),
                ("Compressed Social Media Photo", "Predicted: LIKELY REAL (0.16% Fake Prob, 99.84% Confidence). Prevented false alarm despite compression blur."),
                ("Synthetic Test Visuals", "Predicted: LIKELY AI-GENERATED (100.0% Fake Prob, 100.0% Confidence).")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6: API Keys, Environment & Security Architecture
# ══════════════════════════════════════════════════════════════════════════════
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Security & Configuration", "Environment Variables & API Security Keys")

create_card(s6, Inches(0.9), Inches(1.8), Inches(5.5), Inches(5.0),
            "Environment Configuration (.env)",
            [
                ("SECRET_KEY", "Cryptographic session signature key protecting client cookies against forgery and replay attacks."),
                ("MONGODB_URI", "`mongodb://localhost:27017/` — Database connection endpoint."),
                ("DATABASE_NAME", "`deepguard_db` — Isolated database namespace for secure tenant data."),
                ("UPLOAD_FOLDER", "`uploads/` — Restricted directory isolated by user account IDs."),
                ("REPORTS_FOLDER", "`reports/` — Storage vault for generated tamper-proof PDF forensic documents."),
                ("MAX_CONTENT_LENGTH", "`104857600` (100 MB) — Denial-of-Service buffer protection.")
            ])

create_card(s6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
            "API & Administrative Access Keys",
            [
                ("Chart Data Endpoints", "`/api/chart/real-fake`, `/api/chart/weekly` — Real-time telemetry endpoints protected by active session authentication."),
                ("Admin Authentication", "`admin0211@gmail.com` / `Krish@02` — Super-Admin role access."),
                ("Password Security", "Salted cryptographic hashes using Werkzeug `scrypt` hashing algorithm (`32768:8:1`)."),
                ("CORS & Protection", "Cross-Origin Resource Sharing (Flask-CORS) with origin whitelisting."),
                ("Sanitization", "File uploads secured via `werkzeug.utils.secure_filename` preventing path traversal.")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7: Video Deepfake Detection Pipeline
# ══════════════════════════════════════════════════════════════════════════════
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Multi-Frame Video Forensics", "Temporal Video Deepfake Analysis")

create_card(s7, Inches(0.9), Inches(1.8), Inches(3.6), Inches(5.0),
            "1. Temporal Frame Sampling",
            [
                ("OpenCV Extraction", "Extracts representative frames across video duration at equidistant sampling intervals."),
                ("Stream Metadata", "Records duration, FPS, width, height, and stream codec parameters."),
                ("Temporal Consistency", "Tracks inter-frame luminance and boundary variance.")
            ])

create_card(s7, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
            "2. Frame-Level Inference",
            [
                ("Neural Classification", "Each extracted frame is independently processed through the ONNX FeatureNet engine."),
                ("Artifact Flagging", "Frames exceeding 50% fake probability are classified as suspicious frames."),
                ("Facial Boundaries", "Detects boundary tearing and lighting discrepancies characteristic of face-swaps.")
            ])

create_card(s7, Inches(8.7), Inches(1.8), Inches(3.7), Inches(5.0),
            "3. Multi-Frame Aggregation",
            [
                ("Suspicious Ratio Calculation", "Computes ratio of manipulated frames against total analyzed frames."),
                ("Classification Thresholds", "Ratio >= 30%: DEEPFAKE / MANIPULATED; Ratio <= 15%: LIKELY AUTHENTIC; Else: INCONCLUSIVE."),
                ("Interactive Timeline", "Web UI displays full frame-by-frame color-coded diagnostic timeline.")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8: Executive Forensic PDF Reports
# ══════════════════════════════════════════════════════════════════════════════
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Audit & Compliance", "Executive Forensic PDF Reporting Engine")

create_card(s8, Inches(0.9), Inches(1.8), Inches(3.6), Inches(5.0),
            "Page 1: Executive Certificate",
            [
                ("Header & Official Logo", "Deep Navy corporate banner featuring the metallic DeepGuard emblem."),
                ("Case & Investigator Meta", "Report ID (e.g., `DG-2AFB477032CF`), investigator details, and UTC timestamp."),
                ("Primary Verdict Banner", "Prominent color-coded classification badge with confidence percentage."),
                ("Cryptographic Audit", "SHA-256 digital fingerprint and file parameters.")
            ])

create_card(s8, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
            "Page 2: Technical Breakdown",
            [
                ("Signal Diagnostics", "Full quantitative breakdown of High-Frequency Noise, Local Variance, Shannon Entropy, and Vibrancy."),
                ("Hardware EXIF Data", "Extracts camera make, model, software, and creation timestamp."),
                ("Provenance Verification", "Evaluates C2PA, SynthID, and generative digital tags."),
                ("Frame Breakdown", "Tabular log of analyzed video frames with individual confidence scores.")
            ])

create_card(s8, Inches(8.7), Inches(1.8), Inches(3.7), Inches(5.0),
            "Page 3: Verdict & Legal",
            [
                ("Visual Distribution", "High-contrast vector pie chart illustrating Authentic vs Manipulated probability."),
                ("Investigative Summary", "Contextualized narrative summary of findings."),
                ("Methodology Statement", "Standards explanation detailing neural residual extraction."),
                ("Legal Disclaimer", "Judicial and evidentiary compliance notice safeguarding forensic integrity.")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9: User Interface & Experience
# ══════════════════════════════════════════════════════════════════════════════
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Design & Usability", "SaaS UI/UX Brand Guidelines")

create_card(s9, Inches(0.9), Inches(1.8), Inches(5.5), Inches(5.0),
            "Design System & Color Hierarchy",
            [
                ("Deep Navy Blue (#0A1A2F)", "Executive primary background providing depth and reduced eye strain during forensic analysis."),
                ("Navy Slate (#112240 / #162C4E)", "Elevated card surfaces with subtle translucent borders (`rgba(220, 208, 255, 0.12)`)."),
                ("Soft Lavender (#DCD0FF)", "Luminescent neon accent highlighting active navigation, badges, and progress indicators."),
                ("Muted Silver (#B0B7C0)", "Secondary labels, technical metadata, and auxiliary parameters."),
                ("Typography Standards", "Manrope for prominent geometric headings; Inter for highly legible data tables; JetBrains Mono for cryptographic hashes.")
            ])

create_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
            "Core User Views & Capabilities",
            [
                ("Interactive Dashboard", "Live telemetry charts (Real vs Fake doughnut, weekly activity bar chart, recent upload logs)."),
                ("Drag-and-Drop Ingestion", "Upload interfaces supporting JPEG, PNG, WEBP, MP4, AVI, and MOV."),
                ("Forensic Result View", "Interactive confidence gauge, risk badge, EXIF inspection card, and one-click PDF export."),
                ("Admin Center", "System telemetry, user management, and AI engine status monitoring."),
                ("Responsive Architecture", "Mobile-optimized layout with collapsible sidebar and touch-friendly controls.")
            ])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10: Conclusion & Roadmap
# ══════════════════════════════════════════════════════════════════════════════
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Summary & Future Horizon", "Conclusion & Strategic Roadmap")

create_card(s10, Inches(0.9), Inches(1.8), Inches(5.5), Inches(5.0),
            "Key Project Accomplishments",
            [
                ("Production-Ready Full-Stack App", "Complete Flask + MongoDB + ONNX system with zero broken dependencies."),
                ("Real Neural Predictions", "Eliminated static heuristics in favor of empirical feature extraction and trained neural inference."),
                ("Unified Brand Identity", "Seamless Deep Navy & Soft Lavender palette across Web UI, Logo, Favicons, and PDF Reports."),
                ("Open-Source Deployment", "Fully version-controlled repository on GitHub (`github.com/kp9937719-cell/DeepGuard`).")
            ])

create_card(s10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
            "Future Product Roadmap",
            [
                ("Audio Deepfake Detection", "Integration of voice cloning spectrogram analysis (ResNet / RawNet models)."),
                ("RESTful Public API", "Public API token authentication for automated corporate KYC and content moderation pipelines."),
                ("Browser Extension", "Real-time social media image checking extension for Chrome and Firefox."),
                ("Blockchain Notarization", "Immutable cryptographic timestamping of media authenticity certificates on-chain.")
            ])

out_path = "DeepGuard_Presentation.pptx"
prs.save(out_path)
print(f"Presentation saved successfully to: {out_path} ({len(prs.slides)} slides)")
