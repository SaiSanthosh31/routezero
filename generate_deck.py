import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 widescreen

    blank_layout = prs.slide_layouts[6]

    # Color Palette: Minimalist Dark Theme
    COLOR_BG = RGBColor(10, 10, 10)
    COLOR_CARD = RGBColor(20, 20, 22)
    COLOR_BORDER = RGBColor(50, 50, 55)
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_GRAY = RGBColor(160, 160, 165)
    COLOR_RED = RGBColor(239, 68, 68)
    COLOR_AMBER = RGBColor(245, 158, 11)

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, title, body_bullets, tag=None, tag_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        txBox = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_after = Pt(10)

        if tag:
            run = p.add_run()
            run.text = f"  [{tag}]"
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = tag_color if tag_color else COLOR_AMBER

        for b in body_bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"- {b}"
            p_b.font.size = Pt(11.5)
            p_b.font.color.rgb = COLOR_GRAY
            p_b.space_after = Pt(5)

    # ----------------------------------------------------
    # SLIDE 1: COVER
    # ----------------------------------------------------
    slide_cover = prs.slides.add_slide(blank_layout)
    set_slide_background(slide_cover)

    tx = slide_cover.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11.0), Inches(3.5))
    tf = tx.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "VOYAGEHACK 4.0 | TRACK 4: AGENTIC REAL-TIME DAST"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_RED
    p0.space_after = Pt(14)

    p1 = tf.add_paragraph()
    p1.text = "RouteZero"
    p1.font.size = Pt(46)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_after = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "Autonomous Real-Time Application Security Agents for B2B Travel Platforms"
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_GRAY
    p2.space_after = Pt(28)

    p3 = tf.add_paragraph()
    p3.text = "Live Platform: https://saisanthosh31.github.io/routezero/  |  Team: RouteZero"
    p3.font.size = Pt(12)
    p3.font.color.rgb = COLOR_WHITE

    # ----------------------------------------------------
    # SLIDE 2: CORE PROBLEM & ARCHITECTURAL SOLUTION (Slide 1 of 2 content)
    # ----------------------------------------------------
    slide_sol = prs.slides.add_slide(blank_layout)
    set_slide_background(slide_sol)

    header_box = slide_sol.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.5), Inches(1.0))
    htf = header_box.text_frame
    hp = htf.paragraphs[0]
    hp.text = "01 | The Problem & Architectural Solution"
    hp.font.size = Pt(20)
    hp.font.bold = True
    hp.font.color.rgb = COLOR_WHITE

    sub = htf.add_paragraph()
    sub.text = "Moving from periodic, dumb vulnerability scanning to real-time, context-aware autonomous AppSec."
    sub.font.size = Pt(12)
    sub.font.color.rgb = COLOR_GRAY

    # Card 1: The Problem Context
    add_card(
        slide_sol,
        left=Inches(0.8), top=Inches(1.8), width=Inches(5.6), height=Inches(5.0),
        title="B2B Travel AppSec Bottlenecks",
        body_bullets=[
            "Frequent Code Deploys: TBO updates flight/hotel APIs daily; traditional weekly scans leave dangerous zero-day exposure windows.",
            "Blind to Business Logic: Traditional DAST sprays generic SQLi/XSS but misses critical logic abuse: price tampering ($1 flights), cross-agency IDOR, and duplicate refund state transitions.",
            "Zombie & Shadow APIs: Deprecated /v1/ routes and unmapped /internal/ debug telemetry remain live in production unmonitored.",
            "High False Positive Fatigue: Security teams are buried in 100-page scanner PDF dumps with zero reproduction proofs."
        ],
        tag="CURRENT STATUS QUO",
        tag_color=COLOR_RED
    )

    # Card 2: RouteZero Solution Architecture
    add_card(
        slide_sol,
        left=Inches(6.8), top=Inches(1.8), width=Inches(5.7), height=Inches(5.0),
        title="RouteZero Agentic Architecture",
        body_bullets=[
            "Autonomous Recon (Zero-Spec): Ingests traffic logs (HAR) and crawls UI to map live endpoints, query params, and body schemas without needing Swagger.",
            "Shadow & Zombie Inventory: Automatically identifies and flags active vs deprecated /v1 routes and undocumented internal endpoints.",
            "LLM-Driven Attack Planner: Analyzes business purpose per endpoint to generate targeted multi-step exploits (IDOR, fare manipulation, auth bypass).",
            "Safe Execution Engine: Scope allowlisting, role-based test credential vault, adaptive rate-limiting, and an interactive Kill Switch.",
            "Verifier & Proof Engine: Eliminates false positives, generates 1-click reproduction curl commands, and outputs an auto-generated OpenAPI 3.0 spec."
        ],
        tag="OUR INNOVATION",
        tag_color=COLOR_AMBER
    )

    # ----------------------------------------------------
    # SLIDE 3: WORKFLOW, METRICS & BUSINESS IMPACT (Slide 2 of 2 content)
    # ----------------------------------------------------
    slide_imp = prs.slides.add_slide(blank_layout)
    set_slide_background(slide_imp)

    header_box2 = slide_imp.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.5), Inches(1.0))
    htf2 = header_box2.text_frame
    hp2 = htf2.paragraphs[0]
    hp2.text = "02 | End-to-End Workflow, Validation & Business Impact"
    hp2.font.size = Pt(20)
    hp2.font.bold = True
    hp2.font.color.rgb = COLOR_WHITE

    sub2 = htf2.add_paragraph()
    sub2.text = "Demonstrating concrete business impact, sub-second deploy reaction, and actionable remediation."
    sub2.font.size = Pt(12)
    sub2.font.color.rgb = COLOR_GRAY

    # Card 3: Execution Loop
    add_card(
        slide_imp,
        left=Inches(0.8), top=Inches(1.8), width=Inches(5.6), height=Inches(5.0),
        title="Continuous Autonomous Loop",
        body_bullets=[
            "CI/CD Change Trigger: Deploy webhooks trigger delta scans within <50ms of commit deployment.",
            "Targeted Exploits Tested:",
            "  * Business Logic: Overrode $450 flight fare to $1.00 via client parameter tampering.",
            "  * Tenant IDOR: Agency-002 exfiltrated Agency-001 passenger passport PII without barrier.",
            "  * Zombie API: Deprecated /v1/legacy/discounts extracted active 50% discount voucher.",
            "  * Shadow API: /api/v2/internal/admin/stats exposed DB connection telemetry.",
            "Verified Ticket Output: Each finding is paired with side-by-side HTTP proof, CWE tagging, team owner, and an instant code patch."
        ],
        tag="VALIDATED POC",
        tag_color=COLOR_AMBER
    )

    # Card 4: Business Impact & TBO Value
    add_card(
        slide_imp,
        left=Inches(6.8), top=Inches(1.8), width=Inches(5.7), height=Inches(5.0),
        title="Enterprise Impact for TBO.com",
        body_bullets=[
            "Direct Revenue Protection: Halts revenue leakage from price tampering, coupon reuse, and double refund loop attacks across high-volume supplier inventories.",
            "Regulatory Compliance (DPDP Act 2023): Prevents heavy penalties by immediately flagging cross-agency IDOR leaks exposing passenger passport and contact PII.",
            "Sub-Minute MTTR (Mean Time to Remediation): Developers receive verified curl reproduction commands and code remediation snippets immediately upon code deploy.",
            "Zero Overhead & Zero Lock-in: Runs on lightweight heuristics with multi-LLM support; exports OpenAPI 3.0 catalog as a by-product for API governance.",
            "Demonstrated Prototype: Production-tested against mock B2B travel portal with live interactive web dashboard."
        ],
        tag="TBO VALUE & ROI",
        tag_color=COLOR_WHITE
    )

    # ----------------------------------------------------
    # SLIDE 4: THANK YOU
    # ----------------------------------------------------
    slide_ty = prs.slides.add_slide(blank_layout)
    set_slide_background(slide_ty)

    tx_ty = slide_ty.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(3.5))
    tf_ty = tx_ty.text_frame
    tf_ty.word_wrap = True

    pty0 = tf_ty.paragraphs[0]
    pty0.text = "THANK YOU"
    pty0.font.size = Pt(44)
    pty0.font.bold = True
    pty0.font.color.rgb = COLOR_WHITE
    pty0.space_after = Pt(12)

    pty1 = tf_ty.add_paragraph()
    pty1.text = "RouteZero: The Autonomous Real-Time AppSec Agent"
    pty1.font.size = Pt(18)
    pty1.font.color.rgb = COLOR_RED
    pty1.space_after = Pt(20)

    pty2 = tf_ty.add_paragraph()
    pty2.text = "Live Interactive Dashboard: https://saisanthosh31.github.io/routezero/\nSource Code: https://github.com/SaiSanthosh31/routezero"
    pty2.font.size = Pt(13)
    pty2.font.color.rgb = COLOR_GRAY

    output_path = "RouteZero_VoyageHack_Submission.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}!")

if __name__ == "__main__":
    create_deck()
