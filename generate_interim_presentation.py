"""
Redesigned Generator Script for ClauseIQ Interim Presentation PPT.
Priority: LESS CONTENT + MUCH LARGER TEXT + STRONG VISUALS + EASY TO PRESENT.
Follows all font size requirements:
- Titles: 30-34 pt
- Main Content: 22-26 pt
- Secondary/Labels: 18-21 pt
- Important Numbers: 36-48 pt
- Table Text: 18-22 pt
- Code: 18-20 pt
- Footers: 10-11 pt
All detailed explanations moved into speaker notes.
"""

from pathlib import Path
import shutil
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
BASE_DIR = Path(__file__).resolve().parent
INTERIM_DIR = BASE_DIR / "Aditional_files" / "Report & PPT" / "Interim"
PRESENTATION_DIR = BASE_DIR / "Aditional_files" / "Report & PPT" / "presentation"
OUTPUT_PPTX = INTERIM_DIR / "ClauseIQ_Interim_Presentation.pptx"

# Figures
FIG_MODEL_COMP = BASE_DIR / "results" / "model_comparison.png"
FIG_CONF_MAT = BASE_DIR / "results" / "confusion_matrices" / "logistic_regression_cm.png"
FIG_CLASS_DIST = BASE_DIR / "reports" / "interim_report" / "figures" / "class_distribution.png"

# Color Palette
COLOR_DARK_NAVY = RGBColor(23, 37, 68)      # #172544 - Title & Thank You
COLOR_LIGHT_BG = RGBColor(248, 250, 252)    # #F8FAFC - Main slide background
COLOR_CARD_BG = RGBColor(255, 255, 255)     # #FFFFFF - Container cards
COLOR_CARD_BORDER = RGBColor(210, 220, 230) # #D2DCE6 - Subtle card borders
COLOR_OUTER_BORDER = RGBColor(210, 220, 230)# Outer slide border
COLOR_NAVY_TITLE = RGBColor(15, 23, 42)     # #0F172A - Slide title text
COLOR_SUBTITLE = RGBColor(71, 85, 105)      # #475569 - Subtitle text
COLOR_BODY_TEXT = RGBColor(30, 41, 59)      # #1E293B - High contrast body text
COLOR_MUTED_TEXT = RGBColor(100, 116, 139)  # #64748B - Footers
COLOR_PRIMARY_BLUE = RGBColor(30, 58, 138)  # #1E3A8A - Deep Academic Blue
COLOR_ACCENT_BLUE = RGBColor(37, 99, 235)   # #2563EB - Highlights & badges
COLOR_LIGHT_BLUE = RGBColor(239, 246, 255)  # #EFF6FF - Light blue fill
COLOR_SUCCESS_GREEN = RGBColor(5, 150, 105) # #059669 - Green highlights
COLOR_LIGHT_GREEN = RGBColor(236, 253, 245) # #ECFDF5 - Light green fill
COLOR_AMBER = RGBColor(217, 119, 6)         # #D97706 - Amber/Warning
COLOR_LIGHT_AMBER = RGBColor(254, 243, 199) # #FEF3C7 - Light amber fill
COLOR_RED = RGBColor(220, 38, 38)           # #DC2626 - Red/Alert
COLOR_CODE_BG = RGBColor(15, 23, 42)        # #0F172A - Code dark background
COLOR_CODE_TEXT = RGBColor(241, 245, 249)   # #F1F5F9 - Code light text
COLOR_WHITE = RGBColor(255, 255, 255)

FONT_HEADING = "Trebuchet MS"
FONT_BODY = "Calibri"
FONT_CODE = "Consolas"


def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_slide_frame_and_header(slide, title_text, subtitle_text, slide_number, category_tag="INTERIM PROGRESS"):
    # Outer frame
    border_rect = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.20), Inches(0.20), Inches(12.93), Inches(7.10)
    )
    border_rect.fill.background()
    border_rect.line.color.rgb = COLOR_OUTER_BORDER
    border_rect.line.width = Pt(1.5)

    # Category Tag Badge (Top Left)
    tag_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.60), Inches(0.38), Inches(2.50), Inches(0.36)
    )
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = COLOR_LIGHT_BLUE
    tag_box.line.color.rgb = COLOR_ACCENT_BLUE
    tag_box.line.width = Pt(1.0)
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = category_tag.upper()
    p_tag.alignment = PP_ALIGN.CENTER
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(11.0)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_ACCENT_BLUE

    # Title & Subtitle box (Title 30-32pt bold!)
    title_box = slide.shapes.add_textbox(Inches(0.60), Inches(0.80), Inches(12.13), Inches(0.95))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_title = tf.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(31.0)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY_TITLE

    p_sub = tf.add_paragraph()
    p_sub.text = subtitle_text
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(18.0)
    p_sub.font.color.rgb = COLOR_SUBTITLE

    # Footer Left (11pt)
    footer_l = slide.shapes.add_textbox(Inches(0.60), Inches(7.05), Inches(6.50), Inches(0.25))
    tf_l = footer_l.text_frame
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
    p_fl = tf_l.paragraphs[0]
    p_fl.text = "ClauseIQ — Contract Clause Classification & Intelligent Search"
    p_fl.font.name = FONT_BODY
    p_fl.font.size = Pt(11.0)
    p_fl.font.color.rgb = COLOR_MUTED_TEXT

    # Footer Right (11pt)
    footer_r = slide.shapes.add_textbox(Inches(7.50), Inches(7.05), Inches(5.23), Inches(0.25))
    tf_r = footer_r.text_frame
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
    p_fr = tf_r.paragraphs[0]
    p_fr.alignment = PP_ALIGN.RIGHT
    p_fr.text = f"Dept. of Computer Applications, MACE | Slide {slide_number}"
    p_fr.font.name = FONT_BODY
    p_fr.font.size = Pt(11.0)
    p_fr.font.color.rgb = COLOR_MUTED_TEXT


def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER, border_width=1.5):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(border_width)
    return card


def set_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text.strip()


def build_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    print("Building Slide 1: Title (Clean & Dominant)...")
    # =========================================================================
    # SLIDE 1: Title Slide (Clean & Dominant)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, COLOR_DARK_NAVY)

    border1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.30), Inches(0.30), Inches(12.73), Inches(6.90))
    border1.fill.background()
    border1.line.color.rgb = RGBColor(51, 65, 85)
    border1.line.width = Pt(1.5)

    # Main Title Area
    tbox1 = slide1.shapes.add_textbox(Inches(0.80), Inches(1.10), Inches(11.73), Inches(3.20))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "ClauseIQ"
    p1.alignment = PP_ALIGN.CENTER
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(56.0)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Machine Learning-Based Contract Clause Classification\nand Intelligent Search System"
    p2.alignment = PP_ALIGN.CENTER
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(28.0)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(147, 197, 253)

    p3 = tf1.add_paragraph()
    p3.text = "Interim Project Presentation"
    p3.alignment = PP_ALIGN.CENTER
    p3.font.name = FONT_BODY
    p3.font.size = Pt(22.0)
    p3.font.color.rgb = RGBColor(226, 232, 240)

    # Metadata Card (Centered & Clean)
    c_meta = add_card(slide1, Inches(2.66), Inches(4.50), Inches(8.00), Inches(2.20), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(71, 85, 105))
    tf_m = c_meta.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_right = Inches(0.30)
    tf_m.margin_top = Inches(0.25)

    p = tf_m.paragraphs[0]
    p.text = "MOHAMMED FARHAN K"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    p = tf_m.add_paragraph()
    p.text = "MCA  |  Department of Computer Applications  |  Reg. No: MAC25MCA-2042"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(18.0)
    p.font.color.rgb = RGBColor(203, 213, 225)

    p = tf_m.add_paragraph()
    p.text = "Mar Athanasius College of Engineering (MACE), Kothamangalam"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(18.0)
    p.font.color.rgb = RGBColor(148, 163, 184)

    set_speaker_notes(slide1, """Good morning respected evaluators and guide Dr. Sonia Abraham. 
I am Mohammed Farhan K, presenting the Interim Project Presentation for my MCA mini project: 'ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System'.
In our first presentation, we proposed the conceptual framework and dataset exploration. Today, for this interim review, I am presenting the verified empirical results of our completed machine learning pipeline. This includes training and tuning four classifiers, evaluating them on our held-out test set, selecting Logistic Regression based on our primary metric, analyzing errors with a full 41x41 confusion matrix, and demonstrating our intelligent search prototype.""")

    print("Building Slide 2: Problem & Motivation (3 Cards + Goal)...")
    # =========================================================================
    # SLIDE 2: Problem Statement & Motivation
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide2, "PROBLEM & MOTIVATION", "Operational Bottlenecks in Legal Contract Review", 2, "MOTIVATION")

    col_w = Inches(3.80)
    top_pos = Inches(1.85)
    h_pos = Inches(3.60)

    # 3 Large Cards
    cards_data = [
        ("MANUAL REVIEW", "Large contracts require time-consuming clause identification.", COLOR_PRIMARY_BLUE),
        ("KEYWORD SEARCH", "Exact keyword search misses variations in legal wording.", COLOR_PRIMARY_BLUE),
        ("CLASSIFICATION CHALLENGE", "41 legal clause categories are highly imbalanced.", COLOR_PRIMARY_BLUE)
    ]

    for idx, (title, text, clr) in enumerate(cards_data):
        x = Inches(0.60 + idx * 4.15)
        c = add_card(slide2, x, top_pos, col_w, h_pos)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.30)
        tf.margin_top = Inches(0.40)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(24.0)
        p.font.bold = True
        p.font.color.rgb = clr

        p = tf.add_paragraph()
        p.text = "\n" + text
        p.font.name = FONT_BODY
        p.font.size = Pt(22.0)
        p.font.color.rgb = COLOR_BODY_TEXT

    # Bottom Goal Card
    c_goal = add_card(slide2, Inches(0.60), Inches(5.70), Inches(12.13), Inches(1.10), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_g = c_goal.text_frame
    tf_g.word_wrap = True
    tf_g.margin_top = Inches(0.20)
    p = tf_g.paragraphs[0]
    p.text = "GOAL: Automatically classify contract clauses and retrieve relevant clauses using classical ML."
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    set_speaker_notes(slide2, """Legal contract review is currently bottlenecked by three main challenges:
First, manual review across lengthy legal contracts is exhausting, slow, and prone to human error.
Second, standard keyword search tools fail because lawyers use varying drafting conventions and synonyms—for example, 'limitation of liability' versus 'aggregate exposure'.
Third, automatic classification is difficult because contract clauses span 41 distinct categories that exhibit severe statistical imbalance.
Our project goal is to build a practical, lightweight classical machine learning system that automatically classifies clauses into 41 categories and provides intelligent semantic clause retrieval.""")

    print("Building Slide 3: Objectives & Current Scope (2 Sections)...")
    # =========================================================================
    # SLIDE 3: Objectives & Current Scope
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide3, "PROJECT OBJECTIVES & CURRENT SCOPE", "Deliverables Planned vs. Actually Completed at Interim Milestone", 3, "SCOPE AUDIT")

    card_w = Inches(5.90)
    card_h = Inches(4.85)

    # Left: Objectives
    c_obj = add_card(slide3, Inches(0.60), Inches(1.85), card_w, card_h)
    tf_o = c_obj.text_frame
    tf_o.word_wrap = True
    tf_o.margin_left = tf_o.margin_right = Inches(0.35)
    tf_o.margin_top = Inches(0.35)

    p = tf_o.paragraphs[0]
    p.text = "OBJECTIVES"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    bullets_obj = [
        "1. Classify clauses into 41 categories",
        "2. Build TF-IDF based clause search",
        "3. Evaluate multiple ML models"
    ]
    for b in bullets_obj:
        p = tf_o.add_paragraph()
        p.text = f"\n{b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(22.0)
        p.font.color.rgb = COLOR_BODY_TEXT

    # Right: Completed
    c_comp = add_card(slide3, Inches(6.80), Inches(1.85), card_w, card_h, bg_color=COLOR_LIGHT_GREEN, border_color=COLOR_SUCCESS_GREEN)
    tf_c = c_comp.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = Inches(0.35)
    tf_c.margin_top = Inches(0.35)

    p = tf_c.paragraphs[0]
    p.text = "CURRENTLY COMPLETED"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    bullets_comp = [
        "✓  Dataset + preprocessing",
        "✓  TF-IDF feature extraction",
        "✓  4 ML models trained & tuned",
        "✓  Model evaluation",
        "✓  Model selection",
        "✓  Search prototype",
        "✓  FastAPI prototype"
    ]
    for b in bullets_comp:
        p = tf_c.add_paragraph()
        p.text = b
        p.font.name = FONT_BODY
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY_TITLE

    set_speaker_notes(slide3, """This slide clearly establishes our interim project milestone.
Our overall objectives are threefold: classify clauses into 41 categories, build a TF-IDF clause search engine, and rigorously evaluate multiple ML models.
For this interim review, we have completed the entire machine learning core: data cleaning, TF-IDF vectorization, training and tuning all four candidate classifiers, evaluating them on the held-out test set, selecting our model, building our search prototype, and implementing our FastAPI backend. The frontend UI and database persistence are scheduled for our final phase.""")

    print("Building Slide 4: Dataset (Big Numbers)...")
    # =========================================================================
    # SLIDE 4: Dataset (Big Numbers)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide4, "DATASET SPECIFICATIONS", "CUAD-Derived Legal Contract Clause Corpus", 4, "DATASET")

    # 4 Big Number Stat Cards
    stat_cards = [
        ("510", "CONTRACTS", COLOR_ACCENT_BLUE),
        ("12,204", "CLAUSE RECORDS", COLOR_PRIMARY_BLUE),
        ("41", "CLAUSE CATEGORIES", COLOR_SUCCESS_GREEN),
        ("3", "CORE FEATURES", COLOR_AMBER)
    ]
    w_s = Inches(2.85)
    for idx, (num, lbl, clr) in enumerate(stat_cards):
        x = Inches(0.60 + idx * 3.10)
        c = add_card(slide4, x, Inches(1.95), w_s, Inches(2.60))
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.40)

        p = tf.paragraphs[0]
        p.text = num
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_HEADING
        p.font.size = Pt(46.0)
        p.font.bold = True
        p.font.color.rgb = clr

        p = tf.add_paragraph()
        p.text = lbl
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_HEADING
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY_TITLE

    # Bottom Schema Box
    c_sch = add_card(slide4, Inches(0.60), Inches(4.85), Inches(12.13), Inches(1.85))
    tf_s = c_sch.text_frame
    tf_s.word_wrap = True
    tf_s.margin_top = Inches(0.25)

    p = tf_s.paragraphs[0]
    p.text = "DATASET ATTRIBUTES"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_s.add_paragraph()
    p.text = "contract_id    |    clause_text    |    category"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_CODE
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_TITLE

    p = tf_s.add_paragraph()
    p.text = "100% Complete:  0 missing values  •  0 empty strings  •  0 duplicate rows"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(19.0)
    p.font.color.rgb = COLOR_MUTED_TEXT

    set_speaker_notes(slide4, """Slide 4 shows our verified dataset figures.
Our dataset is derived from the Contract Understanding Atticus Dataset (CUAD v1).
It contains 510 commercial contracts, yielding exactly 12,204 labeled clause records across 41 categories.
The schema is minimal and clean, with 3 columns: contract_id, clause_text, and category.
Through automated validation in src/clean_dataset.py, we verified 100% data completeness: exactly zero missing values, zero empty strings, and zero duplicates.""")

    print("Building Slide 5: EDA & Class Imbalance (Chart + 46.33:1)...")
    # =========================================================================
    # SLIDE 5: EDA & Class Imbalance
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide5, "EXPLORATORY DATA ANALYSIS", "Corpus Distribution and Severe Class Imbalance", 5, "DATA PROFILING")

    # Left: Imbalance Metrics Card
    c_imb = add_card(slide5, Inches(0.60), Inches(1.85), Inches(5.50), Inches(4.85))
    tf_i = c_imb.text_frame
    tf_i.word_wrap = True
    tf_i.margin_left = tf_i.margin_right = Inches(0.35)
    tf_i.margin_top = Inches(0.30)

    p = tf_i.paragraphs[0]
    p.text = "CLASS IMBALANCE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_i.add_paragraph()
    p.text = "\nLargest Category:\nParties — 1,251"
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_TITLE

    p = tf_i.add_paragraph()
    p.text = "\nSmallest Category:\nPrice Restrictions — 27"
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_TITLE

    p = tf_i.add_paragraph()
    p.text = "\nImbalance Ratio:"
    p.font.name = FONT_BODY
    p.font.size = Pt(19.0)
    p.font.color.rgb = COLOR_MUTED_TEXT

    p = tf_i.add_paragraph()
    p.text = "46.33 : 1"
    p.font.name = FONT_HEADING
    p.font.size = Pt(44.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    # Bottom Conclusion Box inside left
    c_con = add_card(slide5, Inches(0.80), Inches(5.75), Inches(5.10), Inches(0.80), bg_color=COLOR_LIGHT_GREEN, border_color=COLOR_SUCCESS_GREEN)
    tf_con = c_con.text_frame
    tf_con.word_wrap = True
    p = tf_con.paragraphs[0]
    p.text = "Macro-F1 is more informative than Accuracy for this dataset."
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(19.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    # Right: Actual Class Distribution Image
    c_img = add_card(slide5, Inches(6.40), Inches(1.85), Inches(6.33), Inches(4.85))
    if FIG_CLASS_DIST.is_file():
        slide5.shapes.add_picture(str(FIG_CLASS_DIST), Inches(6.55), Inches(1.95), width=Inches(6.03), height=Inches(4.65))

    set_speaker_notes(slide5, """Slide 5 highlights our exploratory analysis of class distribution.
The dataset exhibits extreme class imbalance: 'Parties' is the largest category with 1,251 instances, while 'Price Restrictions' has only 27 instances.
This creates a severe imbalance ratio of 46.33 to 1.
Because of this skew, standard accuracy is misleading: a model could achieve over 70% accuracy by only predicting common boilerplate while missing rare, high-consequence clauses. 
Therefore, Macro-F1—which weights all 41 classes equally—is our primary evaluation metric.""")

    print("Building Slide 6: Data Preprocessing (Horizontal Flow)...")
    # =========================================================================
    # SLIDE 6: Data Preprocessing (Horizontal Pipeline)
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide6, "DATA PREPROCESSING PIPELINE", "Standardized Text Normalization for Legal Terminology", 6, "PREPROCESSING")

    # Horizontal Flow Boxes
    p_steps = [
        "RAW CLAUSE",
        "LOWERCASE",
        "REMOVE URL/EMAIL",
        "CLEAN NOISE",
        "NORMALIZE SPACES",
        "CLEAN TEXT"
    ]
    w_box = Inches(1.85)
    for idx, name in enumerate(p_steps):
        x = Inches(0.60 + idx * 2.05)
        c = add_card(slide6, x, Inches(1.95), w_box, Inches(1.40), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.30)
        p = tf.paragraphs[0]
        p.text = name
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_HEADING
        p.font.size = Pt(18.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY_BLUE

    # Example Card
    c_ex = add_card(slide6, Inches(0.60), Inches(3.70), Inches(12.13), Inches(3.00))
    tf_e = c_ex.text_frame
    tf_e.word_wrap = True
    tf_e.margin_left = tf_e.margin_right = Inches(0.40)
    tf_e.margin_top = Inches(0.30)

    p = tf_e.paragraphs[0]
    p.text = "TEXT TRANSFORMATION EXAMPLE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_e.add_paragraph()
    p.text = '\nBefore:\n"This AGREEMENT shall be governed by Delaware! Contact legal@clauseiq.com or https://..."'
    p.font.name = FONT_CODE
    p.font.size = Pt(21.0)
    p.font.color.rgb = COLOR_BODY_TEXT

    p = tf_e.add_paragraph()
    p.text = '\nAfter:\n"this agreement shall be governed by delaware contact for terms"'
    p.font.name = FONT_CODE
    p.font.size = Pt(21.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    set_speaker_notes(slide6, """Slide 6 presents our text cleaning pipeline implemented in src/text_cleaner.py.
Raw clauses undergo case-folding, URL and email removal via regex, noise filtering while preserving legal punctuation, and whitespace normalization.
The example shows how web links and irregular casing are cleaned into standardized tokens while preserving all substantive legal terms like 'governed by delaware'.""")

    print("Building Slide 7: TF-IDF Feature Engineering (Visual Cards)...")
    # =========================================================================
    # SLIDE 7: TF-IDF Feature Engineering
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide7, "TF-IDF FEATURE ENGINEERING", "Sparse Vector Space Configuration & Anti-Leakage Protocol", 7, "FEATURE EXTRACTION")

    # 5 Configuration Cards
    tfidf_cards = [
        ("10,000", "FEATURES", COLOR_PRIMARY_BLUE),
        ("(1, 2)", "N-GRAMS", COLOR_ACCENT_BLUE),
        ("TRUE", "SUBLINEAR TF", COLOR_SUCCESS_GREEN),
        ("2", "MIN DF", COLOR_AMBER),
        ("0.95", "MAX DF", RGBColor(124, 58, 237))
    ]
    w_tc = Inches(2.25)
    for idx, (num, lbl, clr) in enumerate(tfidf_cards):
        x = Inches(0.60 + idx * 2.47)
        c = add_card(slide7, x, Inches(1.95), w_tc, Inches(2.20))
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.35)

        p = tf.paragraphs[0]
        p.text = num
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_HEADING
        p.font.size = Pt(38.0)
        p.font.bold = True
        p.font.color.rgb = clr

        p = tf.add_paragraph()
        p.text = lbl
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_HEADING
        p.font.size = Pt(20.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY_TITLE

    # Bottom Anti-Leakage Card
    c_leak = add_card(slide7, Inches(0.60), Inches(4.45), Inches(12.13), Inches(2.25), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_l = c_leak.text_frame
    tf_l.word_wrap = True
    tf_l.margin_top = Inches(0.30)

    p = tf_l.paragraphs[0]
    p.text = "TRAIN TEXT   →   FIT TF-IDF   →   TEST TEXT   →   TRANSFORM"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_l.add_paragraph()
    p.text = "\nVocabulary fitted only on training data to prevent data leakage."
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    p = tf_l.add_paragraph()
    p.text = "Unigrams + Bigrams capture compound legal collocations ('governing law', 'audit rights')."
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(19.0)
    p.font.color.rgb = COLOR_BODY_TEXT

    set_speaker_notes(slide7, """Slide 7 illustrates our feature extraction settings:
We configure 10,000 maximum features, unigrams and bigrams (1,2), sublinear TF scaling (1 + log(tf)), minimum document frequency of 2, and maximum document frequency of 0.95.
Bigrams are essential to capture two-word legal expressions like 'governing law' and 'prior written consent'.
Importantly, to prevent data leakage, the vectorizer was fitted strictly on the training partition and applied to the test partition via transform().""")

    print("Building Slide 8: Train / Test Split (Visual Split)...")
    # =========================================================================
    # SLIDE 8: Train / Test Split (Visual Split)
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide8, "DATASET PARTITIONING STRATEGY", "Stratified 80/20 Clause-Level Partition Preserving 41 Classes", 8, "DATA SPLIT")

    # Center Total Card
    c_tot = add_card(slide8, Inches(4.16), Inches(1.85), Inches(5.00), Inches(1.15))
    tf_t = c_tot.text_frame
    tf_t.word_wrap = True
    tf_t.margin_top = Inches(0.20)
    p = tf_t.paragraphs[0]
    p.text = "12,204 TOTAL CLAUSES"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    # Stratified Split Label
    c_split = add_card(slide8, Inches(4.16), Inches(3.20), Inches(5.00), Inches(0.85), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_sp = c_split.text_frame
    tf_sp.word_wrap = True
    p = tf_sp.paragraphs[0]
    p.text = "80 / 20 STRATIFIED SPLIT"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    # Two Split Cards
    w_sp = Inches(4.80)
    # Train
    c_tr = add_card(slide8, Inches(1.50), Inches(4.25), w_sp, Inches(1.65))
    tf_tr = c_tr.text_frame
    tf_tr.word_wrap = True
    tf_tr.margin_top = Inches(0.25)
    p = tf_tr.paragraphs[0]
    p.text = "9,763"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(44.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE
    p = tf_tr.add_paragraph()
    p.text = "TRAIN SAMPLES (80%)"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(20.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_BODY_TEXT

    # Test
    c_te = add_card(slide8, Inches(7.03), Inches(4.25), w_sp, Inches(1.65), bg_color=COLOR_LIGHT_GREEN, border_color=COLOR_SUCCESS_GREEN)
    tf_te = c_te.text_frame
    tf_te.word_wrap = True
    tf_te.margin_top = Inches(0.25)
    p = tf_te.paragraphs[0]
    p.text = "2,441"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(44.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN
    p = tf_te.add_paragraph()
    p.text = "TEST SAMPLES (20%)"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(20.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_TITLE

    # Bottom Note
    c_nt = add_card(slide8, Inches(0.60), Inches(6.10), Inches(12.13), Inches(0.75))
    tf_nt = c_nt.text_frame
    tf_nt.word_wrap = True
    p = tf_nt.paragraphs[0]
    p.text = "41 classes preserved  •  random_state = 42  •  Clause-level split — NOT contract-level"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(20.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    set_speaker_notes(slide8, """Slide 8 illustrates our dataset partition:
We performed an 80/20 stratified split with random_state=42, partitioning our 12,204 clauses into 9,763 training samples and 2,441 held-out test samples.
Stratification ensures all 41 categories maintain identical proportions in both splits.
Important clarification: this is a clause-level stratified split, not a contract-level split. All four models were evaluated on the exact same 2,441 held-out test instances.""")

    print("Building Slide 9: Four ML Models (4 Cards)...")
    # =========================================================================
    # SLIDE 9: Four ML Models (4 Cards)
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide9, "FOUR MACHINE LEARNING MODELS", "Candidate Architectures for High-Dimensional Sparse Text", 9, "MODELS")

    m_cards = [
        ("LOGISTIC REGRESSION", "Linear classifier", "Softmax decision surface with L2 regularization."),
        ("LINEAR SVM", "Maximum-margin classifier", "Separating hyperplane optimized for sparse text."),
        ("NAIVE BAYES", "Probabilistic baseline", "Fast generative word frequency baseline."),
        ("RANDOM FOREST", "Tree ensemble", "Decision tree ensemble evaluating non-linear bagging.")
    ]
    w_mc = Inches(2.85)
    for idx, (m_title, m_type, m_desc) in enumerate(m_cards):
        x = Inches(0.60 + idx * 3.10)
        c = add_card(slide9, x, Inches(1.95), w_mc, Inches(3.65))
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.20)
        tf.margin_top = Inches(0.35)

        p = tf.paragraphs[0]
        p.text = m_title
        p.font.name = FONT_HEADING
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY_BLUE

        p = tf.add_paragraph()
        p.text = f"\n{m_type}"
        p.font.name = FONT_HEADING
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT_BLUE

        p = tf.add_paragraph()
        p.text = f"\n{m_desc}"
        p.font.name = FONT_BODY
        p.font.size = Pt(18.0)
        p.font.color.rgb = COLOR_BODY_TEXT

    # Bottom Fair Benchmark Bar
    c_bb = add_card(slide9, Inches(0.60), Inches(5.80), Inches(12.13), Inches(0.95), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_bb = c_bb.text_frame
    tf_bb.word_wrap = True
    p = tf_bb.paragraphs[0]
    p.text = "Same TF-IDF Features   •   Same Training Set   •   Same Held-Out Test Set"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    set_speaker_notes(slide9, """Slide 9 presents our four candidate models:
Logistic Regression: a multinomial linear model with L2 regularization.
Linear SVM: a maximum-margin hyperplane classifier well-suited for sparse text.
Naive Bayes: a fast probabilistic generative baseline.
Random Forest: an ensemble of decision trees to test non-linear bagging on text.
Crucially, all four models were trained on the same training set and evaluated on the exact same held-out test set.""")

    print("Building Slide 10: Training & Hyperparameter Tuning (Compact Table)...")
    # =========================================================================
    # SLIDE 10: Training & Hyperparameter Tuning (Compact Table)
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide10, "TRAINING & HYPERPARAMETER TUNING", "Systematic Cross-Validation Results from Repository", 10, "TUNING")

    # Table: 5 rows x 3 cols
    tbl_shape = slide10.shapes.add_table(5, 3, Inches(0.60), Inches(1.95), Inches(12.13), Inches(3.60))
    table = tbl_shape.table
    table.columns[0].width = Inches(4.00)
    table.columns[1].width = Inches(4.00)
    table.columns[2].width = Inches(4.13)

    t_headers = ["MODEL", "METHOD", "BEST PARAMETER"]
    t_rows = [
        ["Naive Bayes", "GridSearchCV (5-Fold)", "alpha = 0.01"],
        ["Random Forest", "RandomizedSearchCV (3-Fold)", "200 trees, max_depth = 50"],
        ["Linear SVM", "GridSearchCV (3-Fold)", "C = 0.1"],
        ["Logistic Regression", "L2 Regularization", "C = 1.0"]
    ]

    for j, h in enumerate(t_headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
        p.font.name = FONT_HEADING
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    for i, r_data in enumerate(t_rows):
        bg = RGBColor(255, 255, 255) if i % 2 == 0 else RGBColor(241, 245, 249)
        for j, val in enumerate(r_data):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            p.font.name = FONT_BODY
            p.font.size = Pt(21.0)
            p.font.bold = (j == 0) or (j == 2 and i == 3)
            p.font.color.rgb = COLOR_BODY_TEXT

    # Bottom Metric Line
    c_mline = add_card(slide10, Inches(0.60), Inches(5.80), Inches(12.13), Inches(0.95), bg_color=COLOR_LIGHT_GREEN, border_color=COLOR_SUCCESS_GREEN)
    tf_ml = c_mline.text_frame
    tf_ml.word_wrap = True
    p = tf_ml.paragraphs[0]
    p.text = "Optimization Metric: Macro-F1 (Balances evaluation across all 41 categories)"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    set_speaker_notes(slide10, """Slide 10 summarizes the tuning parameters for all four classifiers.
All tuning was performed on the training partition using StratifiedKFold cross-validation optimizing for Macro-F1:
For Naive Bayes, GridSearchCV selected alpha = 0.01.
For Random Forest, RandomizedSearchCV selected 200 estimators and max_depth of 50.
For Linear SVM, grid search selected C = 0.1.
For Logistic Regression, L2 regularization with C = 1.0 and balanced class weights was utilized.""")

    print("Building Slide 11: Implementation Code (Large & Readable)...")
    # =========================================================================
    # SLIDE 11: Implementation Code (Large & Readable)
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide11, "IMPLEMENTATION CODE", "Verified Pipeline Logic from Repository (src/train_baseline.py)", 11, "SOURCE CODE")

    # Dark Code Box
    c_code = add_card(slide11, Inches(0.60), Inches(1.85), Inches(12.13), Inches(4.05), bg_color=COLOR_CODE_BG, border_color=COLOR_PRIMARY_BLUE)
    tf_co = c_code.text_frame
    tf_co.word_wrap = True
    tf_co.margin_left = tf_co.margin_right = Inches(0.35)
    tf_co.margin_top = Inches(0.30)

    code_lines = """# TF-IDF Feature Extraction
vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
X_train = vectorizer.fit_transform(X_train_text)
X_test  = vectorizer.transform(X_test_text)

# Model Training with Balanced Weights
clf = LogisticRegression(max_iter=1000, class_weight="balanced")
clf.fit(X_train, y_train)

# Inference on Held-Out Test Set (N=2,441)
y_pred = clf.predict(X_test)"""

    p = tf_co.paragraphs[0]
    p.text = code_lines
    p.font.name = FONT_CODE
    p.font.size = Pt(20.0)
    p.font.color.rgb = COLOR_CODE_TEXT

    # Bottom Pipeline Indicator
    c_flow = add_card(slide11, Inches(0.60), Inches(6.05), Inches(12.13), Inches(0.75), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_fl = c_flow.text_frame
    tf_fl.word_wrap = True
    p = tf_fl.paragraphs[0]
    p.text = "DATA   →   TF-IDF   →   MODEL   →   PREDICTION"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    set_speaker_notes(slide11, """Slide 11 shows the actual production code from our repository in src/feature_extraction.py and src/train_baseline.py.
First, we vectorize raw text using TfidfVectorizer with 10,000 features and unigram-bigram pairing. Notice that fit_transform is applied exclusively to X_train_text, while X_test_text is transformed using transform() to prevent data leakage.
Second, LogisticRegression is initialized with class_weight='balanced' to compensate for the 46:1 class imbalance.
Finally, the model fits on X_train and predicts on the 2,441 test samples.""")

    print("Building Slide 12: Model Evaluation (Big Table)...")
    # =========================================================================
    # SLIDE 12: Model Evaluation (Big Table)
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide12, "MODEL EVALUATION RESULTS", "Held-Out Test Set Benchmark (N = 2,441, 41 Classes)", 12, "EVALUATION")

    # Table 5 rows x 5 cols
    tbl_shape = slide12.shapes.add_table(5, 5, Inches(0.60), Inches(1.85), Inches(12.13), Inches(3.70))
    table = tbl_shape.table
    table.columns[0].width = Inches(3.33)
    table.columns[1].width = Inches(2.20)
    table.columns[2].width = Inches(2.20)
    table.columns[3].width = Inches(2.20)
    table.columns[4].width = Inches(2.20)

    eval_headers = ["Model", "Accuracy", "Precision", "Recall", "Macro-F1"]
    eval_rows = [
        ["Logistic Regression", "71.90%", "64.81%", "66.22%", "64.74%"],
        ["Linear SVM", "72.63%", "63.23%", "66.65%", "64.18%"],
        ["Naive Bayes", "69.27%", "60.24%", "58.67%", "58.53%"],
        ["Random Forest", "65.46%", "55.27%", "59.04%", "56.34%"]
    ]

    for j, h in enumerate(eval_headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
        p.font.name = FONT_HEADING
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    for i, r_data in enumerate(eval_rows):
        is_lr = (i == 0)
        bg = RGBColor(236, 253, 245) if is_lr else (RGBColor(255, 255, 255) if i % 2 == 1 else RGBColor(241, 245, 249))
        for j, val in enumerate(r_data):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            p.font.name = FONT_BODY
            p.font.size = Pt(22.0)
            p.font.bold = is_lr or (j == 1 and i == 1) or (j == 4 and is_lr)
            if is_lr:
                p.font.color.rgb = COLOR_SUCCESS_GREEN
            else:
                p.font.color.rgb = COLOR_BODY_TEXT

    # Large Bottom Footer
    c_foot = add_card(slide12, Inches(0.60), Inches(5.80), Inches(12.13), Inches(0.95), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_fo = c_foot.text_frame
    tf_fo.word_wrap = True
    p = tf_fo.paragraphs[0]
    p.text = "TEST SET: 2,441 samples   |   41 classes   |   Primary Metric: Macro-F1"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    set_speaker_notes(slide12, """Slide 12 is our core model evaluation table containing the verified results from results/model_comparison.csv:
Logistic Regression achieved 71.90% Accuracy, 64.81% Macro Precision, 66.22% Macro Recall, and 64.74% Macro-F1.
Linear SVM achieved 72.63% Accuracy, 63.23% Macro Precision, 66.65% Macro Recall, and 64.18% Macro-F1.
Naive Bayes achieved 69.27% Accuracy and 58.53% Macro-F1.
Random Forest achieved 65.46% Accuracy and 56.34% Macro-F1.
Notice that Linear SVM achieved the highest overall accuracy at 72.63%, but Logistic Regression achieved the highest Macro-F1 at 64.74%.""")

    print("Building Slide 13: Model Comparison Graph (Large 70% Chart)...")
    # =========================================================================
    # SLIDE 13: Model Comparison Graph (Large 70% Chart)
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide13, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide13, "MODEL COMPARISON VISUAL BENCHMARK", "Accuracy vs. Macro-F1 across All Four Architectures", 13, "COMPARISON")

    # Large Chart on Left (70% width)
    c_cg = add_card(slide13, Inches(0.60), Inches(1.85), Inches(8.50), Inches(4.90))
    if FIG_MODEL_COMP.is_file():
        slide13.shapes.add_picture(str(FIG_MODEL_COMP), Inches(0.75), Inches(1.95), width=Inches(8.20), height=Inches(4.70))

    # Right Observations Card
    c_ro = add_card(slide13, Inches(9.30), Inches(1.85), Inches(3.43), Inches(4.90))
    tf_ro = c_ro.text_frame
    tf_ro.word_wrap = True
    tf_ro.margin_left = tf_ro.margin_right = Inches(0.20)
    tf_ro.margin_top = Inches(0.35)

    p = tf_ro.paragraphs[0]
    p.text = "KEY TAKEAWAYS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_ro.add_paragraph()
    p.text = "\nSVM:\nHighest Accuracy\n72.63%"
    p.font.name = FONT_BODY
    p.font.size = Pt(21.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_TITLE

    p = tf_ro.add_paragraph()
    p.text = "\nLogistic Regression:\nHighest Macro-F1\n64.74%"
    p.font.name = FONT_BODY
    p.font.size = Pt(21.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    p = tf_ro.add_paragraph()
    p.text = "\nNB / RF:\nLower Macro-F1\n(58.53% / 56.34%)"
    p.font.name = FONT_BODY
    p.font.size = Pt(20.0)
    p.font.color.rgb = COLOR_MUTED_TEXT

    set_speaker_notes(slide13, """Slide 13 displays the model comparison bar chart generated at 300 DPI from results/model_comparison.png.
The chart visually shows the comparison across Accuracy, Macro-F1, and Weighted-F1:
Linear SVM leads in raw Accuracy with 72.63%.
Logistic Regression leads in Macro-F1 with 64.74%.
Both Naive Bayes and Random Forest lag significantly behind in Macro-F1, showing that linear models handle sparse high-dimensional TF-IDF vectors much better than tree ensembles.""")

    print("Building Slide 14: Why Logistic Regression? (Direct Comparison)...")
    # =========================================================================
    # SLIDE 14: Why Logistic Regression? (Direct Comparison)
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide14, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide14, "MODEL SELECTION: WHY LOGISTIC REGRESSION?", "Selection Decision Based on Primary Evaluation Metric", 14, "SELECTION")

    w_card = Inches(5.90)
    h_top = Inches(2.65)

    # Left: SVM Card
    c_svm = add_card(slide14, Inches(0.60), Inches(1.85), w_card, h_top)
    tf_svm = c_svm.text_frame
    tf_svm.word_wrap = True
    tf_svm.margin_left = tf_svm.margin_right = Inches(0.35)
    tf_svm.margin_top = Inches(0.30)

    p = tf_svm.paragraphs[0]
    p.text = "LINEAR SVM"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_svm.add_paragraph()
    p.text = "\nAccuracy:   72.63%  (Highest Accuracy)"
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_TITLE

    p = tf_svm.add_paragraph()
    p.text = "Macro-F1:  64.18%"
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.color.rgb = COLOR_MUTED_TEXT

    # Right: LR Card
    c_lr = add_card(slide14, Inches(6.80), Inches(1.85), w_card, h_top, bg_color=COLOR_LIGHT_GREEN, border_color=COLOR_SUCCESS_GREEN)
    tf_lr = c_lr.text_frame
    tf_lr.word_wrap = True
    tf_lr.margin_left = tf_lr.margin_right = Inches(0.35)
    tf_lr.margin_top = Inches(0.30)

    p = tf_lr.paragraphs[0]
    p.text = "LOGISTIC REGRESSION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    p = tf_lr.add_paragraph()
    p.text = "\nAccuracy:   71.90%"
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.color.rgb = COLOR_MUTED_TEXT

    p = tf_lr.add_paragraph()
    p.text = "Macro-F1:  64.74%  (Highest Macro-F1)"
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    # Large Center Selection Banner
    c_dec = add_card(slide14, Inches(0.60), Inches(4.75), Inches(12.13), Inches(2.00), bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_dec = c_dec.text_frame
    tf_dec.word_wrap = True
    tf_dec.margin_top = Inches(0.20)

    p = tf_dec.paragraphs[0]
    p.text = "PRIMARY METRIC: MACRO-F1"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    p = tf_dec.add_paragraph()
    p.text = "SELECTED MODEL: LOGISTIC REGRESSION"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(32.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_dec.add_paragraph()
    p.text = "Macro-F1 gives equal importance to all 41 classes regardless of sample frequency."
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(20.0)
    p.font.color.rgb = COLOR_BODY_TEXT

    set_speaker_notes(slide14, """Slide 14 explains our model selection decision.
Our evaluation strategy defined Macro-F1 as the primary metric and Accuracy as the secondary metric.
Linear SVM achieved a higher raw accuracy of 72.63% compared to 71.90% for Logistic Regression.
However, Logistic Regression achieved a higher Macro-F1 of 64.74% compared to 64.18% for Linear SVM.
In an imbalanced 41-class dataset, Macro-F1 is essential because it gives equal importance to rare, high-consequence clauses like Price Restrictions and Non-Compete, rather than being dominated by frequent boilerplate.
Therefore, Logistic Regression was selected because Macro-F1 was defined as the primary evaluation metric.""")

    print("Building Slide 15: Class-Level Performance (6 Representative Classes)...")
    # =========================================================================
    # SLIDE 15: Class-Level Performance (6 Representative Classes)
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide15, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide15, "CLASS-LEVEL PERFORMANCE", "Representative Category Metrics from Logistic Regression Report", 15, "PER-CLASS")

    # Table 7 rows x 4 cols
    tbl_shape = slide15.shapes.add_table(7, 4, Inches(0.60), Inches(1.85), Inches(12.13), Inches(3.80))
    table = tbl_shape.table
    table.columns[0].width = Inches(4.33)
    table.columns[1].width = Inches(2.60)
    table.columns[2].width = Inches(2.60)
    table.columns[3].width = Inches(2.60)

    cat_headers = ["Category", "Precision", "Recall", "F1-Score"]
    cat_rows = [
        ["Governing Law", "100.00%", "96.74%", "98.34%"],
        ["Parties", "97.19%", "96.80%", "96.99%"],
        ["Insurance", "97.25%", "94.64%", "95.93%"],
        ["Cap On Liability", "79.46%", "65.93%", "72.06%"],
        ["Affiliate License-Licensee", "21.95%", "39.13%", "28.12%"],
        ["Affiliate License-Licensor", "11.11%", "21.43%", "14.63%"]
    ]

    for j, h in enumerate(cat_headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
        p.font.name = FONT_HEADING
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    for i, r_data in enumerate(cat_rows):
        bg = RGBColor(255, 255, 255) if i % 2 == 0 else RGBColor(241, 245, 249)
        for j, val in enumerate(r_data):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            p.font.name = FONT_BODY
            p.font.size = Pt(21.0)
            p.font.bold = (j == 0)
            p.font.color.rgb = COLOR_BODY_TEXT

    # Conclusion Banner
    c_cb = add_card(slide15, Inches(0.60), Inches(5.85), Inches(12.13), Inches(0.90))
    tf_cb = c_cb.text_frame
    tf_cb.word_wrap = True
    p = tf_cb.paragraphs[0]
    p.text = "Performance varies significantly across categories due to class imbalance and vocabulary overlap."
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(20.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    set_speaker_notes(slide15, """Slide 15 shows class-level results from our verified classification report in results/classification_reports/logistic_regression_report.csv across six representative categories:
Distinctive categories like Governing Law and Parties achieve near-perfect F1-scores of 98.34% and 96.99%.
Moderate provisions like Cap On Liability achieve 72.06% F1.
Challenging provisions such as Affiliate License-Licensee and Licensor achieve lower F1-scores (28.12% and 14.63%) because they share virtually identical vocabulary, differing only in who grants the license to whom.""")

    print("Building Slide 16: Confusion Matrix (Large Visual)...")
    # =========================================================================
    # SLIDE 16: Confusion Matrix (Large Visual)
    # =========================================================================
    slide16 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide16, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide16, "CONFUSION MATRIX ANALYSIS", "41 x 41 Error Analysis for Logistic Regression (Test N = 2,441)", 16, "ERROR ANALYSIS")

    # Large CM Picture on Left (70% width)
    c_cmp = add_card(slide16, Inches(0.60), Inches(1.85), Inches(8.20), Inches(4.90))
    if FIG_CONF_MAT.is_file():
        slide16.shapes.add_picture(str(FIG_CONF_MAT), Inches(0.75), Inches(1.95), width=Inches(7.90), height=Inches(4.70))

    # Right Card: Structure & Errors
    c_cme = add_card(slide16, Inches(9.00), Inches(1.85), Inches(3.73), Inches(4.90))
    tf_ce = c_cme.text_frame
    tf_ce.word_wrap = True
    tf_ce.margin_left = tf_ce.margin_right = Inches(0.20)
    tf_ce.margin_top = Inches(0.30)

    p = tf_ce.paragraphs[0]
    p.text = "41 x 41 MATRIX"
    p.font.name = FONT_HEADING
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_ce.add_paragraph()
    p.text = "\n• Rows = True Labels\n• Columns = Predicted"
    p.font.name = FONT_BODY
    p.font.size = Pt(21.0)
    p.font.color.rgb = COLOR_NAVY_TITLE

    p = tf_ce.add_paragraph()
    p.text = "\n• Diagonal = Correct\n• Off-diagonal = Errors"
    p.font.name = FONT_BODY
    p.font.size = Pt(21.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    # Bottom error note
    c_en = add_card(slide16, Inches(9.15), Inches(5.15), Inches(3.43), Inches(1.40), bg_color=COLOR_LIGHT_AMBER, border_color=COLOR_AMBER)
    tf_en = c_en.text_frame
    tf_en.word_wrap = True
    p = tf_en.paragraphs[0]
    p.text = "Most errors occur between classes with similar legal wording (e.g., Licensee vs. Licensor)."
    p.font.name = FONT_BODY
    p.font.size = Pt(18.0)
    p.font.bold = True
    p.font.color.rgb = RGBColor(180, 83, 9)

    set_speaker_notes(slide16, """Slide 16 displays the full 41-by-41 confusion matrix for Logistic Regression on our held-out test set of 2,441 samples.
The vertical axis shows True Categories, and the horizontal axis shows Predicted Categories.
The bright diagonal confirms high accuracy on frequent provisions.
Off-diagonal errors are concentrated in specific pairs with similar wording, such as Affiliate License-Licensee versus Licensor, Cap On Liability versus Uncapped Liability, and Agreement Date versus Effective Date.""")

    print("Building Slide 17: Search Prototype & Key Findings...")
    # =========================================================================
    # SLIDE 17: Search Prototype & Key Findings
    # =========================================================================
    slide17 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide17, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide17, "SEARCH PROTOTYPE & KEY FINDINGS", "TF-IDF Semantic Retrieval Results and Core ML Insights", 17, "RETRIEVAL & FINDINGS")

    w_card = Inches(5.90)
    h_card = Inches(4.85)

    # Left: Search Prototype
    c_sp = add_card(slide17, Inches(0.60), Inches(1.85), w_card, h_card)
    tf_sp = c_sp.text_frame
    tf_sp.word_wrap = True
    tf_sp.margin_left = tf_sp.margin_right = Inches(0.35)
    tf_sp.margin_top = Inches(0.30)

    p = tf_sp.paragraphs[0]
    p.text = "SEARCH PROTOTYPE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p = tf_sp.add_paragraph()
    p.text = "TF-IDF + Cosine Similarity\n"
    p.font.name = FONT_BODY
    p.font.size = Pt(22.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    p = tf_sp.add_paragraph()
    p.text = "• Precision@1 = 80%\n• Precision@5 = 88%\n• Precision@10 = 86%"
    p.font.name = FONT_BODY
    p.font.size = Pt(24.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    # Ablation Box inside
    c_ab = add_card(slide17, Inches(0.85), Inches(5.15), Inches(5.40), Inches(1.35), bg_color=COLOR_LIGHT_AMBER, border_color=COLOR_AMBER)
    tf_ab = c_ab.text_frame
    tf_ab.word_wrap = True
    p = tf_ab.paragraphs[0]
    p.text = "BIGRAM ABLATION:\nPrecision@1 drops 80% → 60% without bigrams"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(20.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    # Right: Key Findings
    c_kf = add_card(slide17, Inches(6.80), Inches(1.85), w_card, h_card)
    tf_kf = c_kf.text_frame
    tf_kf.word_wrap = True
    tf_kf.margin_left = tf_kf.margin_right = Inches(0.35)
    tf_kf.margin_top = Inches(0.30)

    p = tf_kf.paragraphs[0]
    p.text = "KEY FINDINGS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    bullets_kf = [
        "✓  Linear models performed better on sparse TF-IDF features",
        "✓  Macro-F1 is essential for the imbalanced dataset",
        "✓  Similar legal vocabulary causes classification errors",
        "✓  Bigrams are critical for capturing legal collocations"
    ]
    for b in bullets_kf:
        p = tf_kf.add_paragraph()
        p.text = f"\n{b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(22.0)
        p.font.color.rgb = COLOR_BODY_TEXT

    set_speaker_notes(slide17, """Slide 17 summarizes our search prototype and core machine learning insights.
In our search evaluation using TF-IDF and Cosine Similarity, the retrieval engine achieves 80% Precision@1, 88% Precision@5, and 86% Precision@10.
Our ablation experiment confirmed that bigrams are essential: without bigrams, Precision@1 drops by 20% (from 80% to 60%).
Our key machine learning takeaways are:
First, linear models handle sparse text spaces much better than tree ensembles;
Second, Macro-F1 is essential for an imbalanced legal dataset;
And third, vocabulary overlap is the primary source of classification confusion.""")

    print("Building Slide 18: Current Status & Next Steps (2 Columns)...")
    # =========================================================================
    # SLIDE 18: Current Status & Next Steps (2 Columns)
    # =========================================================================
    slide18 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide18, COLOR_LIGHT_BG)
    add_slide_frame_and_header(slide18, "CURRENT STATUS & NEXT STEPS", "Interim Completed Scope vs. Upcoming Final Milestones", 18, "STATUS & NEXT")

    w_card = Inches(5.90)
    h_card = Inches(4.85)

    # Left: COMPLETED
    c_cp = add_card(slide18, Inches(0.60), Inches(1.85), w_card, h_card, bg_color=COLOR_LIGHT_GREEN, border_color=COLOR_SUCCESS_GREEN)
    tf_cp = c_cp.text_frame
    tf_cp.word_wrap = True
    tf_cp.margin_left = tf_cp.margin_right = Inches(0.35)
    tf_cp.margin_top = Inches(0.30)

    p = tf_cp.paragraphs[0]
    p.text = "COMPLETED ✓"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_GREEN

    completed_list = [
        "•  Dataset & EDA",
        "•  Preprocessing pipeline",
        "•  TF-IDF feature space",
        "•  4 ML models trained & tuned",
        "•  Model evaluation",
        "•  Logistic Regression selected",
        "•  Confusion matrix analysis",
        "•  Search prototype + ablation",
        "•  FastAPI prototype"
    ]
    for b in completed_list:
        p = tf_cp.add_paragraph()
        p.text = b
        p.font.name = FONT_BODY
        p.font.size = Pt(21.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY_TITLE

    # Right: NEXT PHASE
    c_np = add_card(slide18, Inches(6.80), Inches(1.85), w_card, h_card, bg_color=COLOR_LIGHT_BLUE, border_color=COLOR_ACCENT_BLUE)
    tf_np = c_np.text_frame
    tf_np.word_wrap = True
    tf_np.margin_left = tf_np.margin_right = Inches(0.35)
    tf_np.margin_top = Inches(0.30)

    p = tf_np.paragraphs[0]
    p.text = "NEXT PHASE →"
    p.font.name = FONT_HEADING
    p.font.size = Pt(26.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    next_list = [
        "•  Supabase integration",
        "•  React.js user interface",
        "•  End-to-end integration",
        "•  Cloud deployment",
        "•  Final validation & testing"
    ]
    for b in next_list:
        p = tf_np.add_paragraph()
        p.text = f"\n{b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(22.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY_TITLE

    set_speaker_notes(slide18, """Slide 18 provides an honest interim progress audit:
On the left, completed tasks include dataset validation, preprocessing, TF-IDF vectorization, training and tuning all four models, multi-metric evaluation, model selection of Logistic Regression, confusion matrix analysis, search prototype, and our FastAPI backend.
On the right, work scheduled for our final phase includes connecting the live Supabase database, building the React user interface, conducting end-to-end integration testing, and final cloud deployment.""")

    print("Building Slide 19: Thank You (Clean & Simple)...")
    # =========================================================================
    # SLIDE 19: Thank You (Clean & Simple)
    # =========================================================================
    slide19 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide19, COLOR_DARK_NAVY)

    border19 = slide19.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.30), Inches(0.30), Inches(12.73), Inches(6.90))
    border19.fill.background()
    border19.line.color.rgb = RGBColor(51, 65, 85)
    border19.line.width = Pt(1.5)

    tbox19 = slide19.shapes.add_textbox(Inches(0.80), Inches(1.50), Inches(11.73), Inches(2.30))
    tf19 = tbox19.text_frame
    tf19.word_wrap = True

    p = tf19.paragraphs[0]
    p.text = "THANK YOU"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(56.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    p = tf19.add_paragraph()
    p.text = "Questions & Discussion"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(28.0)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    c_ty = add_card(slide19, Inches(2.66), Inches(4.30), Inches(8.00), Inches(2.30), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(71, 85, 105))
    tf_ty = c_ty.text_frame
    tf_ty.word_wrap = True
    tf_ty.margin_top = Inches(0.30)

    p = tf_ty.paragraphs[0]
    p.text = "ClauseIQ"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(30.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    p = tf_ty.add_paragraph()
    p.text = "Machine Learning-Based Contract Clause Classification\nand Intelligent Search System"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(20.0)
    p.font.color.rgb = RGBColor(203, 213, 225)

    p = tf_ty.add_paragraph()
    p.text = "Mohammed Farhan K  |  MAC25MCA-2042  |  MACE"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_BODY
    p.font.size = Pt(18.0)
    p.font.color.rgb = RGBColor(148, 163, 184)

    set_speaker_notes(slide19, """Thank you very much, respected evaluators and guide, for your time and feedback. 
ClauseIQ has completed its core machine learning phase with verified empirical results, achieving 64.74% Macro-F1 with Logistic Regression across 41 imbalanced legal categories, alongside a verified search prototype.
I welcome your questions, feedback, and suggestions for our upcoming final phase.""")

    # Save to primary & backup destinations
    OUTPUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    revised_output = INTERIM_DIR / "ClauseIQ_Interim_Presentation_Revised.pptx"
    prs.save(str(revised_output))
    print(f"\nSuccessfully generated revised presentation at:\n  -> {revised_output}")

    try:
        prs.save(str(OUTPUT_PPTX))
        print(f"  -> Overwritten original: {OUTPUT_PPTX}")
    except PermissionError:
        print(f"  [NOTE] {OUTPUT_PPTX.name} is currently open in PowerPoint. Saved to {revised_output.name}!")

    PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)
    alt_output = PRESENTATION_DIR / "ClauseIQ_Interim_Presentation_Revised.pptx"
    shutil.copy2(str(revised_output), str(alt_output))
    print(f"  -> Backup copy saved to: {alt_output}")


if __name__ == "__main__":
    build_presentation()
