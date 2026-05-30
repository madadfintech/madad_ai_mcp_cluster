#!/usr/bin/env python3
"""Generate the corrected Smart Air Quality Predictor report PDF.

Fixes requested:
- Preserve the original cover page.
- Certificate: Date/Place on the left, supervisor details on the right.
- Justified body text.
- References expanded into university-style sub-categories.
- Every chapter starts on a fresh page.
"""

from pathlib import Path

import fitz
from PIL import Image as PILImage
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
SOURCE_PDF = Path("/Users/ishaanjainlock10/Downloads/final_report (1).pdf")
OUT_DIR = ROOT / "report_output"
ASSET_DIR = OUT_DIR / "assets"
OUT_PDF = OUT_DIR / "Smart_Air_Quality_Predictor_Report_Fixed.pdf"

PW, PH = A4
LM = RM = 1.18 * inch
TM = BM = 1.0 * inch
CW = PW - LM - RM

FONT = "Times-Roman"
FONT_B = "Times-Bold"
FONT_I = "Times-Italic"
BODY_SIZE = 11


def extract_assets():
    """Render the source cover and available figure pages into local images."""
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(SOURCE_PDF)
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(ASSET_DIR / "cover_page.png")

    for page_number, name in [(39, "photo_p40.png"), (40, "photo_p41.png")]:
        if page_number >= doc.page_count:
            continue
        images = doc[page_number].get_images(full=True)
        if images:
            extracted = doc.extract_image(images[0][0])
            (ASSET_DIR / name).write_bytes(extracted["image"])
        else:
            pix = doc[page_number].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            pix.save(ASSET_DIR / name)


def p(text):
    return Paragraph(text, s_normal)


def b(text):
    return f"<b>{text}</b>"


def u(text):
    return f"<u>{text}</u>"


def bu(text):
    return f"<b><u>{text}</u></b>"


class FullPageImage(Flowable):
    def __init__(self, path):
        super().__init__()
        self.path = str(path)
        self.width = PW
        self.height = PH

    def draw(self):
        self.canv.drawImage(self.path, -LM, -BM, width=PW, height=PH, preserveAspectRatio=False)

    def wrap(self, availWidth, availHeight):
        return 0, 0


_ss = getSampleStyleSheet()
s_normal = ParagraphStyle(
    "Body",
    parent=_ss["Normal"],
    fontName=FONT,
    fontSize=BODY_SIZE,
    leading=16,
    alignment=TA_JUSTIFY,
    spaceAfter=6,
)
s_center = ParagraphStyle("Center", parent=s_normal, alignment=TA_CENTER)
s_center_bold = ParagraphStyle("CenterBold", parent=s_center, fontName=FONT_B)
s_title = ParagraphStyle(
    "Title",
    parent=s_center,
    fontName=FONT_B,
    fontSize=14,
    leading=20,
    alignment=TA_CENTER,
    spaceAfter=10,
)
s_chapter = ParagraphStyle(
    "Chapter",
    parent=s_center,
    fontName=FONT_B,
    fontSize=13,
    leading=20,
    alignment=TA_CENTER,
    spaceAfter=12,
)
s_section = ParagraphStyle(
    "Section",
    parent=s_normal,
    fontName=FONT_B,
    alignment=TA_LEFT,
    spaceBefore=10,
    spaceAfter=4,
)
s_left = ParagraphStyle("Left", parent=s_normal, alignment=TA_LEFT, spaceAfter=4)
s_left_bold = ParagraphStyle("LeftBold", parent=s_left, fontName=FONT_B)
s_bullet = ParagraphStyle(
    "Bullet",
    parent=s_normal,
    leftIndent=24,
    firstLineIndent=-12,
    spaceAfter=4,
)
s_ref_cat = ParagraphStyle(
    "RefCategory",
    parent=s_left_bold,
    leading=18,
    spaceBefore=10,
    spaceAfter=4,
)
s_ref = ParagraphStyle(
    "Reference",
    parent=s_normal,
    leftIndent=24,
    firstLineIndent=-24,
    spaceAfter=6,
)
s_caption = ParagraphStyle(
    "Caption",
    parent=s_center,
    fontName=FONT_I,
    fontSize=9,
    leading=12,
    alignment=TA_CENTER,
)


def h(text):
    return Paragraph(u(b(text)), s_section)


def bullet_items(story, items):
    for item in items:
        story.append(Paragraph(f"&bull;&nbsp; {item}", s_bullet))


def add_table(story, data, widths, header=True, highlight_last=False):
    tbl = Table(data, colWidths=widths, hAlign="CENTER")
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#D0D0D0")),
            ("FONTNAME", (0, 0), (-1, 0), FONT_B),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ]
    if highlight_last:
        style.append(("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1), HexColor("#E8F4E8")))
        style.append(("FONTNAME", (0, len(data) - 1), (-1, len(data) - 1), FONT_B))
    tbl.setStyle(TableStyle(style))
    story.append(tbl)


def signature_table(rows, left_ratio=0.45):
    tbl = Table(rows, colWidths=[CW * left_ratio, CW * (1 - left_ratio)])
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return tbl


def add_front_matter(story):
    story.append(FullPageImage(ASSET_DIR / "cover_page.png"))
    story.append(PageBreak())

    story.append(Paragraph(bu("Abstract"), s_title))
    abstract = [
        "Air pollution is one of the most pressing environmental and public health challenges of the 21st century. According to the World Health Organization, more than 7 million people die annually due to air pollution-related diseases, and approximately 99% of the world's population breathes air that exceeds WHO quality guidelines. India's major cities consistently rank among the most polluted globally, with Delhi and Gurugram frequently recording Air Quality Index values in the Very Poor and Severe categories.",
        "This project, Smart Air Quality Predictor, proposes a low-cost IoT-based solution that continuously monitors air quality parameters and forecasts future AQI trends using a lightweight machine learning model. The system is built around an ESP32 microcontroller connected to an MQ135 gas sensor for CO2/VOC measurement and a DHT11 temperature and humidity sensor. Sensor readings are pushed to Firebase Realtime Database every 30 seconds through Wi-Fi.",
        "A Firebase Cloud Function applies a linear regression model on recent sensor data to predict the next-hour AQI. The system features a real-time web dashboard built with Next.js and Chart.js, automated alerts when the predicted AQI exceeds unhealthy thresholds, and complete historical data logging. The total hardware cost is under INR 620, making it accessible for schools, homes, and research institutions.",
        "The project demonstrates the integration of Internet of Things, cloud computing, and machine learning within a minimal budget, providing a practical alternative to expensive commercial AQI monitoring stations that cost several lakhs. The work contributes toward democratizing pollution intelligence at the community level.",
    ]
    for para in abstract:
        story.append(p(para))
    story.append(PageBreak())

    story.append(Paragraph(bu("STUDENT DECLARATION & SUPERVISOR APPROVAL CERTIFICATE"), s_title))
    story.append(p("We, Ishaan Jain and Sumit Kumar Pathak, bearing Roll Numbers 221011150016 and 221011150037 respectively, hereby declare that we have successfully prepared the project report titled Smart Air Quality Predictor."))
    story.append(p("We further declare that the project report has been completed by us and has been duly reviewed, finalized, and approved by our Supervisor/Guide. The work presented in this report is original and has not been submitted elsewhere for any other academic qualification."))
    story.append(Spacer(1, 14))
    story.append(Paragraph("Student Name: Ishaan Jain &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Student Signature: _______________", s_left))
    story.append(Paragraph("Student Name: Sumit Kumar Pathak &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Student Signature: _______________", s_left))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width=CW, thickness=0.5, color=colors.black))
    story.append(Spacer(1, 8))
    story.append(Paragraph(bu("Supervisor/Guide Approval"), s_left_bold))
    story.append(p("I hereby certify that the above-mentioned project report has been reviewed and approved by me and is ready for submission."))
    story.append(Spacer(1, 14))
    story.append(Paragraph("Supervisor/Guide Signature: _______________", s_left))
    story.append(Paragraph("Name of Supervisor: Dr. Jyoti Rani", s_left))
    story.append(Paragraph("Designation: Assistant Professor", s_left))
    story.append(Paragraph("Department: Bachelor of Technology", s_left))
    story.append(Paragraph("Institution: Gurugram University", s_left))
    story.append(Spacer(1, 14))
    story.append(signature_table([[Paragraph("Date: 30 April 2026", s_left), Paragraph("", s_left)], [Paragraph("Place: Gurugram", s_left), Paragraph("", s_left)]]))
    story.append(PageBreak())

    story.append(Paragraph(bu("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING GURUGRAM UNIVERSITY GURUGRAM"), s_title))
    story.append(Paragraph(bu("CERTIFICATE"), s_title))
    story.append(p("This is to certify that the work contained in the PROJECT entitled Smart Air Quality Predictor, submitted by Ishaan Jain (221011150016) and Sumit Kumar Pathak (221011150037) for the award of the B.Tech. Computer Science and Engineering (IoT) to the Department of Engineering and Technology, Gurugram University, Gurugram, Haryana, is a record of bonafide work carried out by them under my direct supervision and guidance. I consider that the PROJECT has reached the standards and fulfills the requirements of the rules and regulations relating to the nature of the degree. The contents embodied in the PROJECT have not been submitted for the award of any other degree or diploma in this or any other university."))
    story.append(Spacer(1, 28))
    story.append(
        signature_table(
            [
                [Paragraph("Date: 30 April 2026", s_left), Paragraph("Supervisor Signature", s_left)],
                [Paragraph("Place: Gurugram", s_left), Paragraph(b("Dr. Jyoti Rani"), s_left)],
                [Paragraph("", s_left), Paragraph("Assistant Professor", s_left)],
                [Paragraph("", s_left), Paragraph("Bachelors of Technology", s_left)],
            ]
        )
    )
    story.append(PageBreak())

    story.append(Paragraph(bu("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING GURUGRAM UNIVERSITY GURUGRAM"), s_title))
    story.append(Paragraph(bu("CANDIDATE'S DECLARATION"), s_title))
    story.append(p("I certify that"))
    decl_items = [
        "The work contained in the project is original and has been done by us under the supervision of our supervisor.",
        "The work has not been submitted to any other Institute for any degree or diploma.",
        "We have conformed to the norms and guidelines given in the Ethical Code of Conduct of the Institute.",
        "Whenever we have used materials from other sources, we have given due credit by citing them in the text of the project and in the references.",
        "Whenever we have quoted written materials from other sources, due credit is given to the sources by citing them.",
        "From the plagiarism test, it is found that the similarity index of the whole project is within 25% and single paper is less than 10% as per the university guidelines.",
    ]
    for letter, item in zip("abcdef", decl_items):
        story.append(Paragraph(f"{letter}.&nbsp;&nbsp;&nbsp;{item}", s_normal))
    story.append(Spacer(1, 16))
    story.append(signature_table([[Paragraph("Date: 30 April 2026", s_left), Paragraph("Student Signatures", s_left)], [Paragraph("Place: Gurugram", s_left), Paragraph("Ishaan Jain (221011150016)", s_left)], [Paragraph("", s_left), Paragraph("Sumit Pathak (221011150037)", s_left)]]))
    story.append(PageBreak())

    story.append(Paragraph(bu("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING GURUGRAM UNIVERSITY GURUGRAM"), s_title))
    story.append(Paragraph(bu("ACKNOWLEDGEMENT"), s_title))
    for para in [
        "We would like to express our sincere gratitude to our project guide, Dr. Jyoti Rani, Assistant Professor, Department of Engineering & Technology, Gurugram University, for their continuous support, valuable guidance, and encouragement throughout the development of this project. Their insightful suggestions and constructive feedback helped us complete this work successfully.",
        "We are extremely thankful to the Chairperson, S.S. Tyagi, and all the faculty members of the Department of Engineering and Technology, Gurugram University, Gurugram, for providing the necessary facilities and academic support.",
        "We would also like to thank our friends and classmates for their cooperation, motivation, and helpful discussions during the course of this project. Special thanks to the open-source community behind Arduino, Firebase, and Chart.js for making powerful tools freely available.",
    ]:
        story.append(p(para))
    story.append(Spacer(1, 18))
    story.append(signature_table([[Paragraph("Date: 30 April 2026", s_left), Paragraph("Student Signatures", s_left)], [Paragraph("Place: Gurugram", s_left), Paragraph("Ishaan Jain (221011150016)", s_left)], [Paragraph("", s_left), Paragraph("Sumit Pathak (221011150037)", s_left)]]))
    story.append(PageBreak())

    story.append(Paragraph(bu("TABLE OF CONTENTS"), s_title))
    toc_items = [
        "Certificate from Supervisor",
        "Candidate Declaration",
        "Acknowledgement",
        "Abstract",
        "Table of Contents",
        "List of Tables",
        "List of Figures",
        "List of Abbreviations",
        "CHAPTER 1: INTRODUCTION",
        "CHAPTER 2: LITERATURE REVIEW",
        "CHAPTER 3: SYSTEM ANALYSIS AND REQUIREMENTS",
        "CHAPTER 4: IMPLEMENTATION, TESTING AND RESULTS",
        "CHAPTER 5: CONCLUSION AND FUTURE SCOPE",
        "REFERENCES",
    ]
    for i, item in enumerate(toc_items, 1):
        story.append(Paragraph(f"{item}<font color='white'>................................................</font>{i}", ParagraphStyle("toc", parent=s_left, fontName=FONT_B if "CHAPTER" in item or item == "REFERENCES" else FONT, leading=20)))
    story.append(PageBreak())


def add_chapter_1(story):
    story.append(Paragraph(u(b("Chapter 1: Introduction")), s_chapter))
    for para in [
        "Air pollution has emerged as one of the most critical and complex environmental challenges of the twenty-first century. Rapid industrialisation, exponential growth in vehicular traffic, large-scale construction activity, and seasonal agricultural burning have collectively driven atmospheric pollutant concentrations far beyond safe thresholds in cities across South Asia, East Asia, Sub-Saharan Africa, and Latin America. The World Health Organization estimates that more than 7 million premature deaths occur globally every year as a direct consequence of outdoor and household air pollution.",
        "In the Indian context, the situation is particularly alarming. India is home to several of the world's most polluted cities, and Delhi, Gurugram, Noida, Ghaziabad, and Faridabad routinely breach severe AQI thresholds during the October-February winter season. Atmospheric temperature inversions trap vehicular exhaust, industrial emissions, and crop-residue smoke in a dense near-surface layer.",
        "The Smart Air Quality Predictor project addresses these gaps by designing, building, and validating a low-cost, open-source IoT-based environmental monitoring system that integrates real-time sensing, cloud data pipelines, machine learning forecasting, and an interactive web dashboard within a hardware budget of under INR 620.",
    ]:
        story.append(p(para))
    story.append(h("1.1 Background"))
    story.append(p("The Air Quality Index communicates daily air quality information in an intuitive form. India's National AQI framework is administered by the Central Pollution Control Board and considers pollutants including PM2.5, PM10, NO2, SO2, CO, O3, NH3, and Pb. Each pollutant sub-index is computed using breakpoint concentration tables, and the overall AQI is the maximum sub-index across measured pollutants."))
    add_table(
        story,
        [
            [Paragraph(b("AQI Range"), s_center_bold), Paragraph(b("Category"), s_center_bold), Paragraph(b("Health Implication"), s_center_bold)],
            ["0-50", "Good", "Minimal impact; suitable for all outdoor activities."],
            ["51-100", "Satisfactory", "Minor discomfort for sensitive individuals."],
            ["101-200", "Moderate", "Breathing discomfort for asthma and heart patients."],
            ["201-300", "Poor", "Breathing discomfort for most people."],
            ["301-400", "Very Poor", "Respiratory illness on prolonged exposure."],
            ["401+", "Severe", "Serious health risk; avoid outdoor exposure."],
        ],
        [CW * 0.18, CW * 0.22, CW * 0.60],
    )
    story.append(h("1.2 Motivation"))
    for para in [
        "The primary motivation for this project is rooted in lived experience. Both project members reside and study in Gurugram, a city that illustrates urban air pollution at its most extreme. During winter, vehicular exhaust, industrial emissions, construction dust, and residue smoke create a near-permanent haze.",
        "Most residents have no real-time access to hyperlocal AQI data for their specific neighbourhood. Existing apps and government websites report city-level averages or readings from fixed monitoring stations that may be several kilometres away and unrepresentative of local conditions.",
        "The project also aligns with the Government of India's National Clean Air Programme and the global movement toward citizen science and open environmental data. Affordable community-deployable sensor nodes can complement official networks by providing denser hyperlocal data.",
    ]:
        story.append(p(para))
    story.append(h("1.3 Scope of the Project"))
    bullet_items(
        story,
        [
            f"{b('Real-time continuous sensing')} of CO2 and VOC using the MQ135 gas sensor with temperature and humidity acquisition using DHT11.",
            f"{b('Wireless transmission')} of structured JSON sensor payloads to Firebase Realtime Database at a configurable interval.",
            f"{b('Machine learning forecasting')} of next-hour AQI using linear regression on recent historical readings.",
            f"{b('Responsive web dashboard')} built with Next.js and Chart.js for live readings, historical trends, and forecast overlays.",
            f"{b('Automated alerting')} through email and push notifications when predicted AQI crosses unhealthy thresholds.",
        ],
    )
    story.append(h("1.4 Problem Overview"))
    story.append(p("A comparative analysis of existing air quality monitoring solutions shows that no commercially available low-budget system provides real-time sensing, predictive intelligence, cloud storage, and automated alerting simultaneously. The Smart Air Quality Predictor uniquely combines these capabilities at an accessible cost."))
    add_table(
        story,
        [
            [Paragraph(b("System / Product"), s_center_bold), Paragraph(b("Cost"), s_center_bold), Paragraph(b("Real-Time"), s_center_bold), Paragraph(b("Predictive"), s_center_bold), Paragraph(b("Cloud"), s_center_bold), Paragraph(b("Alerts"), s_center_bold)],
            ["CPCB CAAQMS Station", "5-50 Lakhs", "Yes", "No", "Yes", "Limited"],
            ["AirVisual Pro", "20,000+", "Yes", "Limited", "Yes", "Yes"],
            ["Basic Arduino + MQ135", "800", "Yes", "No", "No", "No"],
            ["Smart Air Quality Predictor", "580-620", "Yes", "Yes", "Yes", "Yes"],
        ],
        [CW * 0.32, CW * 0.14, CW * 0.12, CW * 0.12, CW * 0.12, CW * 0.12],
        highlight_last=True,
    )


def add_chapter_2(story):
    story.append(Paragraph(u(b("Chapter 2: Literature Review")), s_chapter))
    story.append(p("A systematic review was conducted to establish the theoretical, scientific, and engineering foundations required for the Smart Air Quality Predictor system. The review focuses on low-cost sensing technology, robust IoT and serverless cloud architecture, and short-term time-series forecasting models."))
    sections = [
        ("2.1 Review Methodology and Foundational Concepts", "The literature was sourced from peer-reviewed publications, environmental science databases, manufacturer datasheets, and platform documentation from Firebase, Espressif, and CPCB. The CPCB National AQI framework provides the project's primary output metric and health alerting basis."),
        ("2.2 Low-Cost Chemiresistive Sensing and Environmental Compensation", "Research confirms that MQ-series sensors can serve as effective proxies when properly conditioned. Studies show that MQ135 sensors, after burn-in and calibration, can correlate strongly with CO2 and VOC trends. Pairing MQ135 with DHT11 helps compensate for humidity-related cross-sensitivity."),
        ("2.3 Serverless IoT Architecture and Cloud Data Pipeline", "The ESP32 provides integrated Wi-Fi, dual-core processing, and ADC capabilities in a low-cost package. Firebase Realtime Database and Cloud Functions support low-latency ingestion, persistent storage, real-time dashboard synchronization, and serverless model execution."),
        ("2.4 Time Series Forecasting and Modeling Rationale", "Linear regression was selected because it is lightweight, interpretable, and suitable for short-term next-hour prediction. While LSTM and ARIMA models can capture more complex patterns, the simple model is adequate for distinguishing major AQI category transitions within the project's constraints."),
        ("2.5 Comparative Analysis and Gap Identification", "The review identifies a gap between expensive regulatory systems and affordable hobbyist prototypes. Existing low-cost systems generally lack cloud persistence, automated alerts, and prediction. This project fills that feature-complete low-budget segment."),
    ]
    for title, body in sections:
        story.append(h(title))
        story.append(p(body))


def add_chapter_3(story):
    story.append(Paragraph(u(b("Chapter 3: System Analysis and Requirements")), s_chapter))
    story.append(p("The proposed air quality monitoring system is designed as a low-cost IoT-enabled platform capable of real-time sensing, cloud integration, and predictive analysis. The architecture combines hardware sensors, wireless communication, cloud storage, and machine learning components into a unified framework."))
    objectives = [
        ("O1: Real-Time Sensing", "Continuously measure gas concentration using MQ135 and environmental conditions using DHT11. Readings are averaged to reduce ADC noise while preserving slowly varying pollution dynamics."),
        ("O2: Cloud Data Pipeline", "Transmit structured sensor data from ESP32 to Firebase Realtime Database every 30 seconds with automatic error handling and retry logic."),
        ("O3: ML-Based Forecasting", "Generate next-hour AQI predictions from recent historical data using ordinary least squares linear regression in a serverless Cloud Function."),
        ("O4: Alert System", "Notify registered users through email and push notifications when predicted AQI exceeds the unhealthy threshold, while enforcing a cooldown to prevent notification fatigue."),
        ("O5: Web Dashboard", "Provide real-time visualisation of live sensor data, historical trends, forecast values, temperature, humidity, and alert status through a responsive web dashboard."),
        ("O6: Low-Cost Deployment", "Achieve the system within a total hardware cost under INR 620 using free and open-source software tools and free-tier cloud services."),
    ]
    for title, body in objectives:
        story.append(h(title))
        story.append(p(body))
    story.append(h("Hardware Bill of Materials"))
    add_table(
        story,
        [
            [Paragraph(b("Component"), s_center_bold), Paragraph(b("Specification"), s_center_bold), Paragraph(b("Cost (INR)"), s_center_bold)],
            ["ESP32 DevKit v1", "240 MHz dual-core, Wi-Fi 802.11 b/g/n, 12-bit ADC", "~250"],
            ["MQ135 Gas Sensor", "CO2/VOC chemiresistive, 5V heater, analog output", "~100"],
            ["DHT11 Sensor", "+/-2 C, +/-5% RH, single-wire digital protocol", "~150"],
            ["Breadboard + Jumper Wires", "830-point solderless breadboard and jumper set", "~80"],
            ["Micro-USB Cable", "Power and programming", "Owned"],
            ["TOTAL", "", "INR 580-620"],
        ],
        [CW * 0.25, CW * 0.55, CW * 0.20],
        highlight_last=True,
    )


def add_chapter_4(story):
    story.append(Paragraph(u(b("Chapter 4: Implementation, Testing and Results")), s_chapter))
    story.append(p("This chapter presents the complete implementation of the hardware prototype, ESP32 firmware, Firebase Cloud Function, alerting system, and web dashboard. The components were tested individually before full integration."))
    story.append(h("4.1 Hardware Assembly and Circuit Design"))
    story.append(p("The hardware prototype was assembled on a standard solderless breadboard. The ESP32 DevKit v1 is mounted centrally, the MQ135 module is connected to GPIO36 through its analog output, and the DHT11 data pin is connected to GPIO4 with a pull-up resistor. A common ground rail is maintained across all components."))
    add_table(
        story,
        [
            [Paragraph(b("Component"), s_center_bold), Paragraph(b("Pin"), s_center_bold), Paragraph(b("ESP32 GPIO"), s_center_bold), Paragraph(b("Notes"), s_center_bold)],
            ["MQ135", "AOUT", "GPIO36", "ADC1 channel; works during Wi-Fi operation"],
            ["MQ135", "VCC", "5V", "Heater requires 5V"],
            ["DHT11", "DATA", "GPIO4", "Digital input with pull-up"],
            ["DHT11", "VCC", "3.3V", "3.3V compatible"],
            ["All", "GND", "GND", "Common ground rail"],
        ],
        [CW * 0.15, CW * 0.12, CW * 0.20, CW * 0.53],
    )
    sections = [
        ("4.2 ESP32 Firmware Implementation", "The firmware uses 5-sample averaging, ADC-to-AQI mapping, trend detection with hysteresis, HTTPS upload to Firebase, and automatic Wi-Fi reconnection with exponential backoff."),
        ("4.3 Firebase Cloud Function - ML Forecasting", "A scheduled Cloud Function fetches recent readings, computes the OLS slope and intercept, extrapolates the AQI one hour ahead, clamps the result to the valid range, and stores the latest forecast in Firebase."),
        ("4.4 Alert System", "When predicted AQI exceeds 150, the backend checks a cooldown timestamp and dispatches email and push notifications containing the predicted AQI, category, precautions, and dashboard link."),
        ("4.5 Web Dashboard", "The dashboard uses Firebase real-time listeners and Chart.js components to show the current AQI, recent trend, forecast overlay, temperature, humidity, and alert status."),
        ("4.6 Testing and Validation", "Unit testing verified sensor response, DHT11 accuracy, AQI category boundaries, Firebase writes, forecast generation, dashboard refresh latency, and alert delivery."),
    ]
    for title, body in sections:
        story.append(h(title))
        story.append(p(body))
    for image_name, caption in [
        ("photo_p40.png", "Figure 1: Arduino IDE and sensor validation evidence from the source report"),
        ("photo_p41.png", "Figure 2: Working hardware assembly evidence from the source report"),
    ]:
        img_path = ASSET_DIR / image_name
        if img_path.exists():
            with PILImage.open(img_path) as im:
                ratio = im.height / im.width
            width = CW * 0.68
            story.append(Image(str(img_path), width=width, height=width * ratio))
            story.append(Paragraph(caption, s_caption))
            story.append(Spacer(1, 6))
    story.append(h("4.7 System Performance Results"))
    story.append(p("The complete system was operated continuously and the observed metrics were within the expected range. Upload failures were attributable to temporary Wi-Fi disconnections, and the reconnection logic recovered automatically."))
    add_table(
        story,
        [
            [Paragraph(b("Metric"), s_center_bold), Paragraph(b("Target"), s_center_bold), Paragraph(b("Observed"), s_center_bold), Paragraph(b("Status"), s_center_bold)],
            ["System uptime", "> 72 hours", "96 hours", "PASS"],
            ["Upload success rate", "> 95%", "98.3%", "PASS"],
            ["Dashboard latency", "< 2 seconds", "1.1s average", "PASS"],
            ["Alert delivery", "< 60 seconds", "42s average", "PASS"],
            ["Forecast MAE", "<= 12 AQI units", "9.4 AQI units", "PASS"],
        ],
        [CW * 0.35, CW * 0.22, CW * 0.25, CW * 0.18],
    )


def add_chapter_5(story):
    story.append(Paragraph(u(b("Chapter 5: Conclusion and Future Scope")), s_chapter))
    for para in [
        "The Smart Air Quality Predictor demonstrates that a comprehensive IoT-based environmental monitoring system encompassing real-time sensing, cloud data pipelines, machine learning forecasting, and multi-channel alerting can be implemented at a hardware cost under INR 620.",
        "The ESP32 platform, MQ135 and DHT11 sensors, Firebase serverless backend, and responsive web dashboard together provide an accessible and extensible foundation for community-level environmental intelligence.",
        "The linear regression forecasting model achieved acceptable next-hour prediction performance for category-level decision-making. The continuous operation test demonstrated reliability, successful cloud ingestion, dashboard responsiveness, and autonomous recovery from Wi-Fi disconnections.",
    ]:
        story.append(p(para))
    story.append(h("5.1 Future Scope"))
    bullet_items(
        story,
        [
            f"{b('PM2.5 and PM10 Sensor Integration.')} Adding an SDS011 or equivalent particle counter would improve scientific rigour and bring the system closer to CPCB-comparable monitoring.",
            f"{b('Advanced ML Forecasting with LSTM.')} A recurrent neural network could improve accuracy during non-stationary pollution events.",
            f"{b('Multi-Gas Sensor Expansion.')} Additional sensors for NO2, O3, CO, and SO2 could convert the prototype into a fuller multi-pollutant node.",
            f"{b('Distributed Sensing Network and Heatmaps.')} Multiple nodes deployed across a campus or city could create real-time pollution heatmaps.",
            f"{b('OLED Display for Offline Readout.')} A small local display would make the system useful even when internet access is unavailable.",
            f"{b('Solar-Powered Outdoor Enclosure.')} A weatherproof enclosure, solar panel, and battery would enable autonomous outdoor deployment.",
            f"{b('Edge ML with TinyML.')} Running a quantised forecasting model on-device could reduce dependence on cloud connectivity.",
        ],
    )
    story.append(p("In summary, the Smart Air Quality Predictor is a scalable, extensible, and open platform for community-level environmental intelligence. Its low cost and modular design make meaningful IoT and ML-based pollution monitoring accessible to students and communities."))


def add_references(story):
    story.append(Paragraph(u(b("References")), s_chapter))
    refs = [
        ("A. Journal Articles and Research Papers", [
            "[1] Kumar, P., et al. (2021). Low-cost sensors: The future of air quality monitoring. <i>Atmospheric Environment</i>, 245, 118021. https://doi.org/10.1016/j.atmosenv.2020.118021",
            "[2] Qin, D., et al. (2020). PM2.5 forecasting based on LSTM deep learning. <i>IEEE Access</i>, 8, 172073-172084. https://doi.org/10.1109/ACCESS.2020.3025005",
            "[3] Mukherjee, A., &amp; Toohey, D. (2016). Low-cost sensor accuracy for air quality monitoring. <i>Environmental Science &amp; Technology</i>, 50(11), 5540-5548.",
        ]),
        ("B. Books and Textbooks", [
            "[4] Geron, A. (2022). <i>Hands-On Machine Learning with Scikit-Learn, Keras &amp; TensorFlow</i> (3rd ed.). O'Reilly Media.",
        ]),
        ("C. Government Reports and Standards", [
            "[5] CPCB (2024). <i>National Air Quality Index Manual</i>. Central Pollution Control Board, Ministry of Environment, Forest and Climate Change, India. https://cpcb.nic.in/national-air-quality-index/",
            "[6] WHO (2022). Ambient Air Pollution Data. World Health Organization. https://www.who.int/data/gho/data/themes/air-pollution",
            "[7] IQAir (2023). <i>World Air Quality Report 2023</i>. IQAir. https://www.iqair.com/world-air-quality-report",
        ]),
        ("D. Technical Documentation and Datasheets", [
            "[8] Espressif Systems (2023). <i>ESP32 Technical Reference Manual</i>. https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf",
            "[9] Winsen Electronics (2022). <i>MQ135 Gas Sensor Datasheet</i>. Zhengzhou Winsen Electronics Technology Co., Ltd. https://www.winsen-sensor.com/sensors/gas-sensor/mq135.html",
            "[10] Adafruit (2023). DHT11 Sensor Datasheet and Arduino Library. https://www.adafruit.com/product/385",
        ]),
        ("E. Software Documentation and Online Resources", [
            "[11] Google Firebase (2024). Firebase Realtime Database Documentation. https://firebase.google.com/docs/database",
            "[12] Arduino (2024). Arduino Reference Documentation. https://www.arduino.cc/reference/en",
            "[13] Vercel (2024). Next.js Documentation. https://nextjs.org/docs",
            "[14] Chart.js Contributors (2024). Chart.js Documentation. https://www.chartjs.org/docs/latest",
            "[15] SendGrid (2024). SendGrid Email API Documentation. https://docs.sendgrid.com",
            "[16] Mobizt (2023). Firebase ESP Client Library for Arduino. https://github.com/mobizt/Firebase-ESP-Client",
            "[17] Blanchon, B. (2023). ArduinoJson: Efficient JSON Serialisation for Arduino. https://arduinojson.org/",
            "[18] Google Firebase (2024). Firebase Cloud Messaging Documentation. https://firebase.google.com/docs/cloud-messaging",
        ]),
    ]
    for category, entries in refs:
        story.append(Paragraph(category, s_ref_cat))
        story.append(HRFlowable(width=CW, thickness=0.5, color=colors.black))
        story.append(Spacer(1, 4))
        for entry in entries:
            story.append(Paragraph(entry, s_ref))
        story.append(Spacer(1, 6))


def build_pdf():
    if not SOURCE_PDF.exists():
        raise FileNotFoundError(f"Source PDF not found: {SOURCE_PDF}")
    extract_assets()
    story = []
    add_front_matter(story)
    add_chapter_1(story)
    story.append(PageBreak())
    add_chapter_2(story)
    story.append(PageBreak())
    add_chapter_3(story)
    story.append(PageBreak())
    add_chapter_4(story)
    story.append(PageBreak())
    add_chapter_5(story)
    story.append(PageBreak())
    add_references(story)

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=LM,
        rightMargin=RM,
        topMargin=TM,
        bottomMargin=BM,
        title="Smart Air Quality Predictor",
        author="Ishaan Jain, Sumit Kumar Pathak",
        allowSplitting=1,
    )
    doc.build(story)
    reader = PdfReader(str(OUT_PDF))
    print(f"PDF built: {OUT_PDF}")
    print(f"Total pages: {len(reader.pages)}")


if __name__ == "__main__":
    build_pdf()
