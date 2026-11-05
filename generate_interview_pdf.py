"""
Generate a comprehensive, professionally styled Interview Preparation Guide (PDF)
for the DeepGuard AI Deepfake & Media Forensics System.
Theme: Executive Deep Navy, Crisp Light Tables, Slate Borders, Soft Lavender Accents.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ── Palette ─────────────────────────────────────────────────────────────────
DG_NAVY_DARK    = colors.HexColor("#0A1A2F")
DG_NAVY_HEADER  = colors.HexColor("#071120")
DG_SLATE_BORDER = colors.HexColor("#CBD5E1")
DG_ROW_LIGHT    = colors.HexColor("#F8FAFC")
DG_ROW_ALT      = colors.HexColor("#EDF2F7")
DG_TEXT_MAIN    = colors.HexColor("#0F172A")
DG_TEXT_MUTED   = colors.HexColor("#475569")
DG_LAVENDER     = colors.HexColor("#7C3AED")
DG_WHITE        = colors.white
DG_EMERALD      = colors.HexColor("#059669")

pdf_path = "DeepGuard_Interview_Questions_Answers.pdf"
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    leftMargin=1.8 * cm,
    rightMargin=1.8 * cm,
    topMargin=1.5 * cm,
    bottomMargin=1.5 * cm,
)

styles = {
    "header_title": ParagraphStyle("header_title", fontName="Helvetica-Bold",
                                   fontSize=18, textColor=DG_WHITE, alignment=TA_CENTER, spaceAfter=2),
    "header_sub": ParagraphStyle("header_sub", fontName="Helvetica",
                                 fontSize=9.5, textColor=colors.HexColor("#DCD0FF"), alignment=TA_CENTER, spaceAfter=2),
    "category_title": ParagraphStyle("category_title", fontName="Helvetica-Bold",
                                     fontSize=13, textColor=DG_NAVY_DARK, spaceBefore=8, spaceAfter=4),
    "q_title": ParagraphStyle("q_title", fontName="Helvetica-Bold",
                              fontSize=10, textColor=DG_LAVENDER, spaceBefore=4, spaceAfter=2),
    "answer": ParagraphStyle("answer", fontName="Helvetica",
                             fontSize=8.5, textColor=DG_TEXT_MAIN, leading=11.5, spaceAfter=4, alignment=TA_JUSTIFY),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica",
                             fontSize=8.5, textColor=DG_TEXT_MAIN, leading=11, spaceAfter=2, leftIndent=12),
    "small": ParagraphStyle("small", fontName="Helvetica",
                            fontSize=7.5, textColor=DG_TEXT_MUTED, alignment=TA_CENTER),
}

story = []

# ── Header ──────────────────────────────────────────────────────────────────
logo_path = os.path.join("static", "images", "logo_emblem.png")
header_content = []
if os.path.exists(logo_path):
    header_content.append(RLImage(logo_path, width=3.2 * cm, height=2.0 * cm))
header_content.extend([
    Paragraph("<b>DeepGuard</b>", styles["header_title"]),
    Paragraph("AI Deepfake Detection &amp; Media Forensics Platform", styles["header_sub"]),
    Paragraph("Comprehensive Technical Interview Q&amp;A Guide", styles["header_sub"]),
    Paragraph("Repository: github.com/kp9937719-cell/DeepGuard &nbsp;|&nbsp; Core: FeatureNet ONNX 1.0", styles["small"]),
])

t_head = Table([[item] for item in header_content], colWidths=[17.4 * cm])
t_head.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), DG_NAVY_HEADER),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t_head)
story.append(Spacer(1, 0.3 * cm))

# ── Q&A Data Structure ──────────────────────────────────────────────────────
qa_sections = [
    {
        "category": "Section 1: Project Overview & Core Architecture",
        "items": [
            {
                "q": "Q1: What is DeepGuard, and what real-world problem does it solve?",
                "a": "DeepGuard is an enterprise-grade AI-powered media forensics and deepfake detection platform. With the rapid rise of generative AI models (like Midjourney, DALL-E, and Stable Diffusion) and deepfake face-swapping algorithms, manipulated media has become virtually indistinguishable to the human eye. DeepGuard provides automated, explainable, and cryptographically verified forensic analysis for both static images and video files to verify media authenticity for journalism, judicial workflows, corporate KYC, and cybersecurity."
            },
            {
                "q": "Q2: Walk me through the high-level architecture of DeepGuard.",
                "a": "DeepGuard is built on a decoupled, modular full-stack architecture:<br/>"
                     "• <b>Web & Application Layer:</b> Python Flask 3.1 structured across 9 independent Blueprints (Auth, Admin, Dashboard, Image, Video, Result, History, Report, Profile).<br/>"
                     "• <b>AI/ML Inference Engine:</b> A custom-trained neural network (FeatureNet) deployed via ONNX Runtime for platform-independent, sub-second CPU inference.<br/>"
                     "• <b>Database Layer:</b> MongoDB document database managing users, analyses, risk telemetry, and generated report metadata.<br/>"
                     "• <b>Forensic Reporting:</b> ReportLab generating 3-page verifiable PDF forensic audit certificates with SHA-256 verification."
            },
            {
                "q": "Q3: Why did you choose ONNX Runtime instead of a standard TensorFlow/PyTorch server?",
                "a": "Portability and environment compatibility were critical architectural decisions. TensorFlow 2.x currently lacks official pre-compiled wheels for newer Python runtimes (like Python 3.14 on Windows), causing installation and cross-platform deployment friction. By training our neural network and compiling it into an optimized <b>ONNX (Open Neural Network Exchange)</b> graph with embedded normalization nodes, DeepGuard runs anywhere with zero heavy dependencies, achieving blazing-fast inference (< 0.16s) directly on standard multi-core CPUs."
            }
        ]
    },
    {
        "category": "Section 2: Machine Learning, Feature Engineering & Training",
        "items": [
            {
                "q": "Q4: How does DeepGuard detect AI-generated images? What features does it extract?",
                "a": "Rather than acting as an unexplainable 'black-box', DeepGuard extracts <b>7 distinct physical and statistical signal vectors</b> from every image:<br/>"
                     "1. <b>High-Frequency Blur/Noise Residual:</b> Computes Gaussian filter pixel deltas. AI diffusion images display unnaturally smooth noise residuals (1.5–3.5) compared to real physical camera sensors (>8.0).<br/>"
                     "2. <b>Local Pixel Variance:</b> Measures heterogeneity across 32x32 pixel patches to detect organic skin/material texture vs generative smoothing.<br/>"
                     "3. <b>Color Shannon Entropy:</b> Evaluates color distribution richness across RGB histogram channels.<br/>"
                     "4. <b>Vibrancy & Saturation Dispersion:</b> Measures color boundary spreads to identify synthetic oversaturation.<br/>"
                     "5. <b>Edge Coefficient of Variation (CV):</b> Analyzes boundary transition variance using Laplacian/edge filters.<br/>"
                     "6. <b>Gradient CV:</b> Measures sub-pixel horizontal and vertical intensity change rates.<br/>"
                     "7. <b>Provenance & Format Score:</b> Inspects C2PA digital provenance, Google AI metadata (e.g. SynthID, trainedAlgorithmicMedia), and camera hardware EXIF tags."
            },
            {
                "q": "Q5: Describe the neural network architecture of FeatureNet.",
                "a": "FeatureNet is a multi-layer feed-forward neural network (MLP) with the following topology:<br/>"
                     "• <b>Input Layer:</b> 7 dimensions (the normalized physical feature vector).<br/>"
                     "• <b>Embedded Normalization:</b> ONNX Sub and Div operators baked into the graph to standardize features against precomputed population means and standard deviations.<br/>"
                     "• <b>Hidden Layer 1:</b> 64 units with ReLU activation and He weight initialization.<br/>"
                     "• <b>Regularization:</b> 30% dropout during training to prevent co-adaptation.<br/>"
                     "• <b>Hidden Layer 2:</b> 32 units with ReLU activation.<br/>"
                     "• <b>Output Layer:</b> 1 unit with Sigmoid activation producing a calibrated probability score [0.0 = Authentic, 1.0 = AI-Generated/Manipulated]."
            },
            {
                "q": "Q6: How did you train the model, and how did you prevent false positives on compressed social media photos?",
                "a": "The model was trained on 10,000 calibrated image distributions across balanced AI and Real cohorts. A critical engineering breakthrough was modeling <b>compressed social media images (such as WhatsApp JPEG compression)</b>. Social platforms aggressively downsample photos and strip EXIF, which causes naive heuristic models to falsely flag them as AI due to low noise. We specifically calibrated our training distribution to recognize compression smoothing patterns (low noise + natural edge ratios) as genuine, achieving <b>99.84% authentic confidence on WhatsApp photos</b> while correctly flagging AI portraits with <b>96.56% certainty</b>."
            }
        ]
    },
    {
        "category": "Section 3: Video Deepfake Detection & Temporal Processing",
        "items": [
            {
                "q": "Q7: How does DeepGuard analyze video deepfakes?",
                "a": "Video deepfake detection requires temporal consistency evaluation in addition to spatial analysis:<br/>"
                     "1. <b>Temporal Frame Extraction:</b> Using OpenCV (cv2.VideoCapture), the video stream is parsed to extract metadata (FPS, duration, resolution, total frame count) and evenly sampled across up to 20 representative frames.<br/>"
                     "2. <b>Independent Neural Inference:</b> Each frame is fed through the ONNX FeatureNet engine to compute frame-level fake probability.<br/>"
                     "3. <b>Multi-Frame Aggregation:</b> Frames exceeding 50% probability are tagged as 'Suspicious'. If the suspicious frame ratio >= 30%, the video is classified as <b>DEEPFAKE / MANIPULATED</b>; if <= 15%, it is classified as <b>LIKELY AUTHENTIC</b>; otherwise, it is flagged as <b>INCONCLUSIVE</b>.<br/>"
                     "4. <b>Interactive Visualization:</b> The web dashboard displays a color-coded frame timeline showing exact locations of anomalies."
            }
        ]
    },
    {
        "category": "Section 4: Backend Engineering, Database & Security",
        "items": [
            {
                "q": "Q8: How is authentication and Role-Based Access Control (RBAC) implemented?",
                "a": "Authentication is powered by Flask-Login with custom user wrappers. Passwords are encrypted using Werkzeug's modern scrypt key derivation function (scrypt:32768:8:1), which is resistant to hardware brute-force attacks. DeepGuard enforces strict role-based access: standard users have access to personal detection pipelines, historical records, and report downloads, while endpoints under /admin/ are protected with a custom @admin_required decorator verifying current_user.role == 'admin' before allowing administrative access."
            },
            {
                "q": "Q9: What database schema did you choose, and why MongoDB?",
                "a": "We chose MongoDB (NoSQL) for its schema flexibility and native JSON support. Forensic records have variable shapes: images contain EXIF dictionaries and 7 signal vectors, while videos contain nested arrays of frame-by-frame analysis and stream metadata. MongoDB stores these naturally in collections:<br/>"
                     "• <b>users:</b> User identity, hashed passwords, roles (admin / user), timestamps.<br/>"
                     "• <b>analyses:</b> File metadata, SHA-256 cryptographic hashes, prediction results, probabilities, and model versioning.<br/>"
                     "• <b>reports:</b> Generated PDF metadata, report IDs (DG-XXXXXXXXXXXX), and file paths."
            },
            {
                "q": "Q10: What security measures protect file uploads?",
                "a": "DeepGuard implements defense-in-depth for file ingestion:<br/>"
                     "1. <b>Filename Sanitization:</b> werkzeug.utils.secure_filename prevents directory traversal attacks.<br/>"
                     "2. <b>Extension Whitelisting:</b> Strict extension verification (ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS).<br/>"
                     "3. <b>Payload Size Caps:</b> Enforced MAX_CONTENT_LENGTH = 100 MB preventing Denial-of-Service buffer overflows.<br/>"
                     "4. <b>Tenant Isolation:</b> Uploaded files are partitioned into user-specific subdirectories (uploads/user_id/).<br/>"
                     "5. <b>SHA-256 Integrity:</b> Every uploaded asset is fingerprinted immediately upon ingestion."
            }
        ]
    },
    {
        "category": "Section 5: Executive PDF Reports & UI/UX Design System",
        "items": [
            {
                "q": "Q11: Explain how the PDF reporting engine works.",
                "a": "Reports are generated dynamically using ReportLab into a formal 3-page forensic document:<br/>"
                     "• <b>Page 1: Executive Certificate:</b> Features the DeepGuard corporate header with metallic shield logo, unique Report ID, investigator credentials, primary classification banner, and media metadata.<br/>"
                     "• <b>Page 2: Technical Breakdown:</b> Presents image resolution, EXIF camera tags, provenance status, and extracted physical signal scores (or frame-by-frame video tabular logs).<br/>"
                     "• <b>Page 3: Visual Analytics & Legal Notice:</b> Features a ReportLab vector pie chart of authenticity distribution, investigative summary, methodology notes, and legal compliance disclaimers."
            },
            {
                "q": "Q12: What design principles govern DeepGuard's UI/UX?",
                "a": "DeepGuard adheres to a professional Dark Navy & Soft Lavender enterprise SaaS design system:<br/>"
                     "• <b>Palette:</b> Deep Navy Blue (#0A1A2F) primary background, Navy Slate (#112240) card containers, Soft Lavender (#DCD0FF) glowing accents, and Muted Silver (#B0B7C0) secondary labels.<br/>"
                     "• <b>Typography:</b> Geometric Manrope for bold headings, Inter for data density and readability, and JetBrains Mono for cryptographic hashes.<br/>"
                     "• <b>Responsiveness:</b> Full mobile and desktop adaptability with collapsible drawer navigation."
            }
        ]
    },
    {
        "category": "Section 6: Testing, Edge Cases & Future Roadmap",
        "items": [
            {
                "q": "Q13: How do you handle edge cases and model limitations?",
                "a": "DeepGuard emphasizes transparency: results are probabilistic confidence scores rather than definitive legal conclusions. When an image falls within the ambiguous band (40% to 60% probability), DeepGuard classifies it as <b>INCONCLUSIVE</b> with a Medium risk rating. Furthermore, the system includes graceful fallback mechanisms: if neural models are unavailable, it cleanly falls back to heuristic analyzers with transparent UI disclaimers so users never receive fabricated predictions."
            },
            {
                "q": "Q14: If you had 3 more months on this project, what would you build next?",
                "a": "Our strategic roadmap focuses on three enterprise extensions:<br/>"
                     "1. <b>Audio Deepfake Detection:</b> Integrating a convolutional-recurrent model (e.g. RawNet) to detect cloned voice synthetic audio tracks.<br/>"
                     "2. <b>RESTful Public API:</b> Offering token-authenticated endpoints for automated corporate KYC, dating apps, and social platform moderation.<br/>"
                     "3. <b>Browser Extension:</b> Developing a lightweight Chrome extension that allows journalists and users to right-click any web image and receive instant forensic verification."
            }
        ]
    }
]

for sec in qa_sections:
    # Section Header Table
    t_sec = Table([[Paragraph(f"<b>{sec['category']}</b>", styles["category_title"])]], colWidths=[17.4 * cm])
    t_sec.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DG_ROW_ALT),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, DG_LAVENDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 0.25 * cm))

    for item in sec["items"]:
        q_p = Paragraph(f"<b>{item['q']}</b>", styles["q_title"])
        a_p = Paragraph(item["a"], styles["answer"])

        t_qa = Table([[q_p], [a_p]], colWidths=[17.4 * cm])
        t_qa.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DG_ROW_LIGHT),
            ("BACKGROUND", (0, 1), (-1, 1), DG_WHITE),
            ("BOX", (0, 0), (-1, -1), 0.5, DG_SLATE_BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t_qa)
        story.append(Spacer(1, 0.25 * cm))

# Footer Disclaimer
story.append(Spacer(1, 0.3 * cm))
story.append(HRFlowable(width="100%", color=DG_SLATE_BORDER, thickness=0.8))
story.append(Spacer(1, 0.15 * cm))
story.append(Paragraph(
    "DeepGuard – AI-Powered Deepfake Detection &amp; Media Forensics Platform &nbsp;|&nbsp; Author: Krish Patel",
    styles["small"]
))

doc.build(story)
print(f"Interview Guide PDF created successfully: {pdf_path}")
