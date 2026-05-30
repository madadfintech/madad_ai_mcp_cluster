#!/usr/bin/env python3
"""Generate only the two cleaned certificate pages."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "report_output"
OUT_PDF = OUT_DIR / "Clean_Certificate_Pages_Only.pdf"

PW, PH = A4
LM = RM = 0.85 * inch
TM = 0.85 * inch
BM = 0.85 * inch
CW = PW - LM - RM

FONT = "Times-Roman"
FONT_B = "Times-Bold"
BODY = 11

sample = getSampleStyleSheet()

s_body = ParagraphStyle(
    "Body",
    parent=sample["Normal"],
    fontName=FONT,
    fontSize=BODY,
    leading=17,
    alignment=TA_JUSTIFY,
    spaceAfter=7,
)
s_center_title = ParagraphStyle(
    "CenterTitle",
    parent=s_body,
    fontName=FONT_B,
    fontSize=12,
    leading=18,
    alignment=TA_CENTER,
    spaceAfter=8,
)
s_center_heading = ParagraphStyle(
    "CenterHeading",
    parent=s_body,
    fontName=FONT_B,
    fontSize=13,
    leading=18,
    alignment=TA_CENTER,
    spaceAfter=10,
)
s_left = ParagraphStyle(
    "Left",
    parent=s_body,
    alignment=TA_LEFT,
    spaceAfter=3,
)
s_right = ParagraphStyle(
    "Right",
    parent=s_body,
    alignment=TA_RIGHT,
    spaceAfter=3,
)
s_left_bold = ParagraphStyle(
    "LeftBold",
    parent=s_left,
    fontName=FONT_B,
)
s_right_bold = ParagraphStyle(
    "RightBold",
    parent=s_right,
    fontName=FONT_B,
)


def u(text):
    return f"<u>{text}</u>"


def bu(text):
    return f"<b><u>{text}</u></b>"


def signature_table(rows, top_padding=2, bottom_padding=2):
    table = Table(rows, colWidths=[CW * 0.48, CW * 0.52], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 6),
                ("LEFTPADDING", (1, 0), (1, -1), 6),
                ("RIGHTPADDING", (1, 0), (1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), top_padding),
                ("BOTTOMPADDING", (0, 0), (-1, -1), bottom_padding),
            ]
        )
    )
    return table


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    story = []

    # Page 1: Student declaration and supervisor approval certificate.
    story.append(Paragraph(bu("STUDENT DECLARATION & SUPERVISOR APPROVAL CERTIFICATE"), s_center_title))
    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            "We, Ishaan Jain and Sumit Kumar Pathak, bearing Roll Numbers 221011150016 and "
            "221011150037 respectively, hereby declare that we have successfully prepared the "
            "project report titled “Smart Air Quality Predictor”.",
            s_body,
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "We further declare that the project report has been completed by us and has been duly "
            "reviewed, finalized, and approved by our Supervisor/Guide. The work presented in this "
            "report is original and has not been submitted elsewhere for any other academic qualification.",
            s_body,
        )
    )
    story.append(Spacer(1, 22))
    story.append(
        signature_table(
            [
                [
                    Paragraph("Student Name: Ishaan Jain", s_left),
                    Paragraph("Student Signature: ____________________", s_right),
                ],
                [
                    Paragraph("Student Name: Sumit Kumar Pathak", s_left),
                    Paragraph("Student Signature: ____________________", s_right),
                ],
            ],
            top_padding=5,
            bottom_padding=5,
        )
    )
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width=CW, thickness=0.6, color=colors.black))
    story.append(Spacer(1, 14))
    story.append(Paragraph(u("<b>Supervisor/Guide Approval</b>"), s_left_bold))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "I hereby certify that the above-mentioned project report has been reviewed and approved "
            "by me and is ready for submission.",
            s_body,
        )
    )
    story.append(Spacer(1, 36))
    story.append(
        signature_table(
            [
                [
                    Paragraph("Date: 30 April 2026", s_left),
                    Paragraph("Supervisor/Guide Signature: ____________________", s_right),
                ],
                [
                    Paragraph("Place: Gurugram", s_left),
                    Paragraph("Name of Supervisor: Dr. Jyoti Rani", s_right),
                ],
                [
                    Paragraph("", s_left),
                    Paragraph("Designation: Assistant Professor", s_right),
                ],
                [
                    Paragraph("", s_left),
                    Paragraph("Department: Bachelor of Technology", s_right),
                ],
                [
                    Paragraph("", s_left),
                    Paragraph("Institution: Gurugram University", s_right),
                ],
            ],
            top_padding=4,
            bottom_padding=4,
        )
    )

    story.append(PageBreak())

    # Page 2: Certificate from supervisor.
    story.append(Paragraph(bu("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING"), s_center_title))
    story.append(Paragraph(bu("GURUGRAM UNIVERSITY GURUGRAM"), s_center_title))
    story.append(Spacer(1, 10))
    story.append(Paragraph(bu("CERTIFICATE"), s_center_heading))
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "This is to certify that the work contained in the PROJECT entitled “Smart Air Quality "
            "Predictor”, submitted by Ishaan Jain (221011150016) and Sumit Kumar Pathak "
            "(221011150037) for the award of the B.Tech. Computer Science and Engineering (IoT) "
            "to the Department of Engineering and Technology, Gurugram University, Gurugram, "
            "Haryana, is a record of bonafide work carried out by them under my direct supervision "
            "and guidance. I consider that the PROJECT has reached the standards and fulfills the "
            "requirements of the rules and regulations relating to the nature of the degree. The "
            "contents embodied in the PROJECT have not been submitted for the award of any other "
            "degree or diploma in this or any other university.",
            s_body,
        )
    )
    story.append(Spacer(1, 56))
    story.append(
        signature_table(
            [
                [
                    Paragraph("Date: 30 April 2026", s_left),
                    Paragraph("Supervisor Signature: ____________________", s_right),
                ],
                [
                    Paragraph("Place: Gurugram", s_left),
                    Paragraph("<b>Dr. Jyoti Rani</b>", s_right),
                ],
                [
                    Paragraph("", s_left),
                    Paragraph("Assistant Professor", s_right),
                ],
                [
                    Paragraph("", s_left),
                    Paragraph("Bachelors of Technology", s_right),
                ],
            ],
            top_padding=5,
            bottom_padding=5,
        )
    )

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=LM,
        rightMargin=RM,
        topMargin=TM,
        bottomMargin=BM,
        title="Clean Certificate Pages",
        author="Ishaan Jain, Sumit Kumar Pathak",
    )
    doc.build(story)
    print(OUT_PDF)


if __name__ == "__main__":
    build()
