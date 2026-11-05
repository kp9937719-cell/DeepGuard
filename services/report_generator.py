"""
DeepGuard – Professional PDF Report Generator using ReportLab.
Executive Navy & Soft Lavender Corporate Theme.
"""

import os
import uuid
import logging
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from bson import ObjectId

logger = logging.getLogger(__name__)

# ── Colors: Clean Executive Theme (High Contrast on White Paper) ─────────────
DG_NAVY_DARK    = colors.HexColor("#0A1A2F")   # Deep Navy
DG_NAVY_HEADER  = colors.HexColor("#071120")   # Header Background
DG_SLATE_BORDER = colors.HexColor("#CBD5E1")   # Crisp Table Grid
DG_ROW_LIGHT    = colors.HexColor("#F8FAFC")   # Row 1 Background
DG_ROW_ALT      = colors.HexColor("#EDF2F7")   # Row 2 Background
DG_TEXT_MAIN    = colors.HexColor("#0F172A")   # Deep Charcoal Text
DG_TEXT_MUTED   = colors.HexColor("#64748B")   # Muted Slate
DG_LAVENDER     = colors.HexColor("#DCD0FF")   # Lavender Text / Accent
DG_WHITE        = colors.white

DG_REAL         = colors.HexColor("#059669")   # Emerald Green
DG_FAKE         = colors.HexColor("#E11D48")   # Vivid Deep Red
DG_INCONCLUSIVE = colors.HexColor("#D97706")   # Amber


def _prediction_color(prediction: str):
    p = (prediction or "").upper()
    if "REAL" in p and "AI" not in p and "FAKE" not in p:
        return DG_REAL
    if "INCONCLUSIVE" in p:
        return DG_INCONCLUSIVE
    return DG_FAKE


def _styles():
    return {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold",
                                fontSize=17, textColor=DG_WHITE, alignment=TA_CENTER, spaceAfter=2),
        "subtitle": ParagraphStyle("subtitle", fontName="Helvetica",
                                   fontSize=8.5, textColor=DG_LAVENDER, alignment=TA_CENTER, spaceAfter=2),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold",
                                  fontSize=10.5, textColor=DG_NAVY_DARK, spaceBefore=4, spaceAfter=2),
        "body": ParagraphStyle("body", fontName="Helvetica",
                               fontSize=8, textColor=DG_TEXT_MAIN, spaceAfter=1, leading=10),
        "small": ParagraphStyle("small", fontName="Helvetica",
                                fontSize=7.5, textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER),
        "mono": ParagraphStyle("mono", fontName="Courier",
                               fontSize=7.5, textColor=DG_TEXT_MAIN, leading=9),
        "disclaimer": ParagraphStyle("disclaimer", fontName="Helvetica-Oblique",
                                     fontSize=7, textColor=DG_TEXT_MUTED, alignment=TA_CENTER, leading=9),
        "result_label": ParagraphStyle("result_label", fontName="Helvetica-Bold",
                                       fontSize=13, alignment=TA_CENTER, spaceAfter=1),
    }


def _header_table(report_id: str, generated_at: str, styles: dict):
    """Return a clean, compact header block with logo."""
    emblem_path = os.path.join("static", "images", "logo_emblem.png")
    logo_path = os.path.join("static", "images", "logo.png")
    chosen_path = emblem_path if os.path.exists(emblem_path) else logo_path

    header_content = []
    if os.path.exists(chosen_path):
        header_content.append(RLImage(chosen_path, width=3.2 * cm, height=2.0 * cm))
    header_content.extend([
        Paragraph("<b>DeepGuard</b>", styles["title"]),
        Paragraph("AI-Powered Deepfake Detection &amp; Media Forensics System", styles["subtitle"]),
        Paragraph("Official Forensic Analysis Report", styles["subtitle"]),
        Paragraph(f"Report ID: <font name='Courier'><b>{report_id}</b></font> &nbsp;|&nbsp; Generated: {generated_at}", styles["small"]),
    ])

    data = [[item] for item in header_content]
    t = Table(data, colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DG_NAVY_HEADER),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _info_table(rows: list, styles: dict):
    """Clean two-column table with high contrast on white background."""
    table_data = [[
        Paragraph(f"<b>{k}</b>", styles["body"]),
        Paragraph(str(v), styles["mono"] if len(str(v)) > 25 else styles["body"])
    ] for k, v in rows]
    t = Table(table_data, colWidths=[5.0 * cm, 12.0 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DG_ROW_LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, -1), DG_TEXT_MAIN),
        ("GRID", (0, 0), (-1, -1), 0.5, DG_SLATE_BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [DG_ROW_LIGHT, DG_ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _pie_chart(real_pct: float, fake_pct: float):
    """Build a balanced, compact pie chart drawing without overlapping text."""
    d = Drawing(200, 120)
    pie = Pie()
    pie.x = 45
    pie.y = 15
    pie.width = 90
    pie.height = 90
    pie.data = [real_pct, fake_pct]
    # Keep side labels only if significant, otherwise omit direct overlap
    pie.labels = [f"Real {real_pct:.1f}%" if real_pct > 5 else "", f"Fake {fake_pct:.1f}%" if fake_pct > 5 else ""]
    pie.slices[0].fillColor = DG_REAL
    pie.slices[1].fillColor = DG_FAKE
    pie.slices.strokeWidth = 0.5
    d.add(pie)
    return d


def generate_report(analysis: dict, user: dict, reports_folder: str) -> dict:
    """
    Generate a 3-page professional PDF report.
    Returns: {"report_id": str, "pdf_path": str, "pdf_filename": str, "generated_at": datetime}
    """
    report_id = f"DG-{uuid.uuid4().hex[:12].upper()}"
    generated_at = datetime.now(timezone.utc)
    generated_str = generated_at.strftime("%Y-%m-%d %H:%M:%S UTC")

    os.makedirs(reports_folder, exist_ok=True)
    pdf_filename = f"{report_id}.pdf"
    pdf_path = os.path.join(reports_folder, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = _styles()
    story = []

    prediction = analysis.get("prediction", "UNKNOWN")
    pred_color = _prediction_color(prediction)
    file_type = analysis.get("file_type", "image")
    is_video = file_type == "video"
    is_demo = analysis.get("is_demo", False)

    # ── PAGE 1: Cover & Summary ─────────────────────────────────────────────
    story.append(_header_table(report_id, generated_str, styles))
    story.append(Spacer(1, 0.2 * cm))

    if is_demo:
        demo_style = ParagraphStyle(
            "demo_warn", fontName="Helvetica-Bold", fontSize=9.5,
            textColor=DG_INCONCLUSIVE, alignment=TA_CENTER,
            spaceAfter=2, spaceBefore=2,
        )
        demo_box = Table(
            [[Paragraph(
                "⚠  DEMO MODEL — UNTRAINED RANDOM WEIGHTS  ⚠<br/>"
                "<font size='8' color='#64748B'>Prediction scores in this report are for demonstration only. "
                "The model was not trained on real forensic data.</font>",
                demo_style,
            )]],
            colWidths=[17 * cm],
        )
        demo_box.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
            ("LINEBELOW",     (0, 0), (-1, -1), 1.5, DG_INCONCLUSIVE),
            ("LINEABOVE",     (0, 0), (-1, -1), 1.5, DG_INCONCLUSIVE),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ]))
        story.append(demo_box)
        story.append(Spacer(1, 0.2 * cm))

    # Detection Result Banner
    result_style = ParagraphStyle("res", fontName="Helvetica-Bold",
                                  fontSize=14, textColor=pred_color, alignment=TA_CENTER)
    story.append(Paragraph(f"Detection Result: {prediction}", result_style))
    story.append(Spacer(1, 0.15 * cm))
    story.append(HRFlowable(width="100%", color=DG_SLATE_BORDER, thickness=1))
    story.append(Spacer(1, 0.2 * cm))

    # User Information
    story.append(Paragraph("User Information", styles["section"]))
    story.append(_info_table([
        ("Investigator Name", user.get("name", "N/A")),
        ("Account Email", user.get("email", "N/A")),
        ("Analysis Record ID", str(analysis.get("_id", "N/A"))),
    ], styles))
    story.append(Spacer(1, 0.25 * cm))

    # Media Information
    story.append(Paragraph("Media Information", styles["section"]))
    file_size_mb = round(analysis.get("file_size", 0) / (1024 * 1024), 3)
    story.append(_info_table([
        ("File Name", analysis.get("file_name", "N/A")),
        ("Media Type", file_type.capitalize()),
        ("File Format", (analysis.get("file_format") or "N/A").upper()),
        ("File Size", f"{file_size_mb} MB"),
        ("SHA-256 Checksum", analysis.get("file_hash", "N/A")),
        ("Upload Timestamp", str(analysis.get("created_at", "N/A"))[:19]),
    ], styles))
    story.append(Spacer(1, 0.25 * cm))

    # Detection Summary
    story.append(Paragraph("Detection Summary", styles["section"]))
    summary_rows = [
        ("Final Classification", prediction),
        ("Confidence Score", f"{analysis.get('confidence', 0):.2f}%"),
        ("Risk Assessment", analysis.get("risk", "N/A")),
        ("Authentic Probability", f"{analysis.get('real_probability', 0):.2f}%"),
        ("Manipulated Probability", f"{analysis.get('fake_probability', 0):.2f}%"),
        ("Forensics Model", analysis.get("model_name", "DeepGuard FeatureNet")),
        ("Model Version", analysis.get("model_version", "1.0-onnx")),
        ("Verification Status", "Verified Production Model" if not is_demo else "Demo Mode"),
        ("Inference Execution Time", f"{analysis.get('processing_time', 0):.3f} seconds"),
    ]
    story.append(_info_table(summary_rows, styles))

    story.append(PageBreak())

    # ── PAGE 2: Technical Analysis ──────────────────────────────────────────
    story.append(Paragraph("Technical Analysis &amp; Signal Extraction", styles["section"]))
    story.append(HRFlowable(width="100%", color=DG_SLATE_BORDER, thickness=1))
    story.append(Spacer(1, 0.3 * cm))

    if is_video:
        video_info = analysis.get("video_info") or {}
        story.append(Paragraph("Video Stream Attributes", styles["section"]))
        story.append(_info_table([
            ("Duration", f"{video_info.get('duration_seconds', 'N/A')} s"),
            ("FPS (Frame Rate)", str(video_info.get("fps", "N/A"))),
            ("Resolution", f"{video_info.get('width', '?')} × {video_info.get('height', '?')} px"),
            ("Total Encoded Frames", str(video_info.get("total_frames", "N/A"))),
            ("Extracted Sample Frames", str(analysis.get("total_frames_extracted", len(analysis.get("frame_analysis") or [])))),
        ], styles))
        story.append(Spacer(1, 0.3 * cm))

        frame_results = analysis.get("frame_analysis") or []
        story.append(Paragraph("Frame-Level Forensic Breakdown", styles["section"]))
        if frame_results:
            frame_data = [["Frame #", "Fake Prob %", "Real Prob %", "Suspicious Status"]]
            for fr in frame_results[:30]:
                frame_data.append([
                    str(fr.get("frame_number", "")),
                    f"{fr.get('fake_probability', 0):.1f}%",
                    f"{fr.get('real_probability', 0):.1f}%",
                    "FLAGGED" if fr.get("is_suspicious") else "Normal",
                ])
            ft = Table(frame_data, colWidths=[3 * cm, 4 * cm, 4 * cm, 6 * cm])
            ft.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), DG_NAVY_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), DG_WHITE),
                ("BACKGROUND", (0, 1), (-1, -1), DG_ROW_LIGHT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DG_ROW_LIGHT, DG_ROW_ALT]),
                ("GRID", (0, 0), (-1, -1), 0.5, DG_SLATE_BORDER),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(ft)
        else:
            story.append(Paragraph("No frame-level data available.", styles["body"]))
    else:
        # Image Analysis
        img_meta = analysis.get("image_metadata") or {}
        # Also check on disk if not stored
        if not img_meta and analysis.get("file_path") and os.path.exists(analysis.get("file_path")):
            try:
                from services.metadata_analysis import analyse_metadata
                img_meta = analyse_metadata(analysis["file_path"])
            except Exception:
                img_meta = {}

        story.append(Paragraph("Image Metadata &amp; Physical Characteristics", styles["section"]))
        rows = [
            ("Image Resolution", f"{img_meta.get('width', '?')} × {img_meta.get('height', '?')} px"),
            ("Color Mode", img_meta.get("mode", "RGB")),
            ("File Format Encoding", (img_meta.get("format") or analysis.get("file_format", "N/A")).upper()),
            ("Contains EXIF Header", "Yes (Camera hardware recorded)" if img_meta.get("has_exif") else "No (Synthetic or stripped)"),
        ]
        exif = img_meta.get("exif", {})
        for k in ["Make", "Model", "DateTime", "Software", "DigitalSourceType"]:
            if k in exif:
                rows.append((f"EXIF Hardware / Provenance ({k})", str(exif[k])))
        story.append(_info_table(rows, styles))
        story.append(Spacer(1, 0.35 * cm))

        # Neural feature scores breakdown
        h_scores = analysis.get("heuristic_scores")
        if not h_scores and analysis.get("file_path") and os.path.exists(analysis.get("file_path")):
            try:
                from services.onnx_predictor import extract_features
                feats = extract_features(analysis["file_path"])[0]
                h_scores = {
                    "blur_noise": round(float(feats[0]), 3),
                    "local_var": round(float(feats[1]), 1),
                    "color_entropy": round(float(feats[2]), 3),
                    "vibrancy": round(float(feats[3]), 3),
                    "edge_cv": round(float(feats[4]), 3),
                    "gradient_cv": round(float(feats[5]), 3),
                    "format_score": round(float(feats[6]), 3),
                }
            except Exception:
                h_scores = None

        if h_scores:
            story.append(Paragraph("Extracted Deep Signal Distributions", styles["section"]))
            signal_rows = [
                ("High-Frequency Blur / Noise Residual", f"{h_scores.get('blur_noise')}  (AI generative models typically measure 1.5 - 3.5; camera photos > 8.0)"),
                ("Local Pixel Variance", f"{h_scores.get('local_var')}  (Measures organic texture heterogeneity vs AI smoothing)"),
                ("Color Shannon Entropy", f"{h_scores.get('color_entropy')}  (Measures color distribution complexity)"),
                ("Vibrancy / Saturation Dispersion", f"{h_scores.get('vibrancy')}  (Generative engines typically exhibit boosted saturation)"),
                ("Edge Coefficient of Variation", f"{h_scores.get('edge_cv')}  (Edge gradient consistency across boundaries)"),
                ("Gradient Coefficient of Variation", f"{h_scores.get('gradient_cv')}  (Sub-pixel transition variance)"),
                ("Provenance &amp; Header Authenticity", f"{h_scores.get('format_score')}  (0.0 = Authentic Camera EXIF, 1.0 = Provenance AI Watermark/PNG)"),
            ]
            story.append(_info_table(signal_rows, styles))

    story.append(PageBreak())

    # ── PAGE 3: Visualisation & Conclusion ─────────────────────────────────
    story.append(Paragraph("Visualisation &amp; Forensic Conclusion", styles["section"]))
    story.append(HRFlowable(width="100%", color=DG_SLATE_BORDER, thickness=1))
    story.append(Spacer(1, 0.3 * cm))

    real_pct = float(analysis.get("real_probability") or 0)
    fake_pct = float(analysis.get("fake_probability") or 0)

    story.append(Paragraph("Authenticity Probability Distribution", styles["section"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_pie_chart(real_pct, fake_pct))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Investigative Summary", styles["section"]))
    summary = (
        f"The submitted {'video' if is_video else 'image'} was evaluated across DeepGuard's "
        f"multi-layer forensic pipeline. The neural feature classifier categorized the media as "
        f"<b>{prediction}</b> with an overall confidence level of "
        f"<b>{analysis.get('confidence', 0):.2f}%</b> (Authentic Probability: {real_pct:.2f}%, "
        f"Manipulated Probability: {fake_pct:.2f}%)."
    )
    story.append(Paragraph(summary, styles["body"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Methodology &amp; Standards", styles["section"]))
    story.append(Paragraph(
        "• <b>Neural Feature Classification:</b> Evaluates sub-pixel noise residuals, frequency gradients, and format provenance.<br/>"
        "• <b>Multi-Frame Temporal Coherence:</b> Detects face-swap artifacts, boundary tearing, and lighting inconsistencies across video clips.<br/>"
        "• <b>Tamper Evidence:</b> Identifies missing or synthetic metadata tags in accordance with C2PA digital provenance standards.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Limitations &amp; Legal Notice", styles["section"]))
    story.append(Paragraph(
        "• AI detection assessments are probabilistic determinations and should be corroborative rather than solely determinative in judicial contexts.<br/>"
        "• Extreme image compression or hostile adversarial post-processing can influence statistical feature distributions.<br/>"
        "• Results should be interpreted alongside independent cryptographic and contextual chain-of-custody evidence.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.5 * cm))

    story.append(HRFlowable(width="100%", color=DG_SLATE_BORDER, thickness=0.8))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "This confidential report was generated automatically by the DeepGuard AI Media Forensics Engine. "
        "Unauthorized reproduction or tampering invalidates this digital certificate.",
        styles["disclaimer"]
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "DeepGuard Inc. – Advanced Media Authenticity &amp; Integrity Verification",
        styles["disclaimer"]
    ))

    # Build document
    doc.build(story)

    return {
        "report_id": report_id,
        "pdf_path": pdf_path,
        "pdf_filename": pdf_filename,
        "generated_at": generated_at,
    }


def save_report_record(db, user_id: str, analysis_id: str, report_data: dict):
    """Persist report metadata to MongoDB."""
    doc = {
        "user_id": ObjectId(user_id),
        "analysis_id": ObjectId(analysis_id),
        "report_id": report_data["report_id"],
        "pdf_path": report_data["pdf_path"],
        "pdf_filename": report_data["pdf_filename"],
        "generated_at": report_data["generated_at"],
    }
    db.reports.insert_one(doc)
