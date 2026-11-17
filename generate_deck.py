import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_designer_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 Widescreen
    blank_layout = prs.slide_layouts[6]

    # Minimalist High-End Design Palette (Dark Terminal / Linear Style)
    C_BG = RGBColor(8, 8, 10)            # True dark slate
    C_SURFACE = RGBColor(16, 16, 20)     # Panel background
    C_SURFACE_ALT = RGBColor(22, 22, 28) # Elevated metric card
    C_BORDER = RGBColor(38, 38, 45)      # Subtle border
    C_BORDER_HI = RGBColor(65, 65, 75)   # Accent border
    C_WHITE = RGBColor(255, 255, 255)
    C_LIGHT = RGBColor(228, 228, 231)    # Zinc 200
    C_MUTED = RGBColor(161, 161, 170)    # Zinc 400
    C_FAINT = RGBColor(113, 113, 122)    # Zinc 500
    C_RED = RGBColor(239, 68, 68)        # Critical Alert
    C_AMBER = RGBColor(245, 158, 11)     # Warning / High

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()

    def draw_box(slide, x, y, w, h, bg=C_SURFACE, border=C_BORDER, line_w=1):
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
        s.fill.solid()
        s.fill.fore_color.rgb = bg
        s.line.color.rgb = border
        s.line.width = Pt(line_w)
        return s

    def draw_pill(slide, x, y, text, border=C_BORDER_HI, text_color=C_LIGHT, bg=C_SURFACE_ALT):
        w = Inches(len(text) * 0.08 + 0.35)
        h = Inches(0.32)
        p_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        p_shape.fill.solid()
        p_shape.fill.fore_color.rgb = bg
        p_shape.line.color.rgb = border
        p_shape.line.width = Pt(0.75)
        tf = p_shape.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = text_color
        return p_shape

    # ========================================================
    # SLIDE 1: COVER SLIDE
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Top Tag
    draw_pill(s1, Inches(1.0), Inches(1.1), "VOYAGEHACK 4.0  //  TRACK 4: AGENTIC REAL-TIME DAST", border=C_BORDER_HI, text_color=C_WHITE)

    # Hero Titles
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(11.3), Inches(2.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p_title = tf1.paragraphs[0]
    p_title.text = "RouteZero"
    p_title.font.size = Pt(54)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE
    p_title.space_after = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Autonomous Security Agent Testing B2B Travel APIs in Near Real-Time"
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = C_MUTED
    p_sub.space_after = Pt(4)

    p_detail = tf1.add_paragraph()
    p_detail.text = "Zero-spec route discovery  *  Continuous shadow/zombie mapping  *  LLM business-logic exploits"
    p_detail.font.size = Pt(12)
    p_detail.font.color.rgb = C_FAINT

    # 3 High-Impact Cards across middle
    cards_data = [
        ("01 / RECON", "Zero-Spec Auto Discovery", "Passively observes traffic & HAR logs to infer endpoints, parameters & schemas with zero Swagger documentation required."),
        ("02 / ATTACK", "Business-Logic Reasoning", "LLM targets travel workflows rather than blind SQLi/XSS: tests fare tampering ($1 flights), cross-agency IDOR & duplicate refunds."),
        ("03 / DEFENSE", "Instant Verifiable Proof", "Reacts to code deploys in <50ms, confirms findings with reproducible curl scripts & delivers immediate developer remediation patches.")
    ]

    for idx, (step_num, title, body) in enumerate(cards_data):
        cx = Inches(1.0 + idx * 3.85)
        draw_box(s1, cx, Inches(4.2), Inches(3.65), Inches(2.3), bg=C_SURFACE, border=C_BORDER)

        tb = s1.shapes.add_textbox(cx + Inches(0.22), Inches(4.35), Inches(3.2), Inches(2.0))
        tf_b = tb.text_frame
        tf_b.word_wrap = True
        
        p0 = tf_b.paragraphs[0]
        p0.text = step_num
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = C_FAINT
        p0.space_after = Pt(6)

        p1 = tf_b.add_paragraph()
        p1.text = title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_after = Pt(6)

        p2 = tf_b.add_paragraph()
        p2.text = body
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = C_MUTED

    # Footer
    fbox = s1.shapes.add_textbox(Inches(1.0), Inches(6.8), Inches(11.3), Inches(0.4))
    ftf = fbox.text_frame
    fp = ftf.paragraphs[0]
    fp.text = "PROTOTYPE LIVE: saisanthosh31.github.io/routezero   |   SOURCE: github.com/SaiSanthosh31/routezero"
    fp.font.size = Pt(10)
    fp.font.color.rgb = C_FAINT

    # ========================================================
    # SLIDE 2: PROBLEM VS ROUTEZERO ARCHITECTURE (Content 1 of 2)
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)

    # Header
    h2 = s2.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.9))
    htf2 = h2.text_frame
    p_h2 = htf2.paragraphs[0]
    p_h2.text = "01 | The Problem & Architectural Solution"
    p_h2.font.size = Pt(21)
    p_h2.font.bold = True
    p_h2.font.color.rgb = C_WHITE

    p_h2_sub = htf2.add_paragraph()
    p_h2_sub.text = "Replacing periodic, blind vulnerability scans with an autonomous, context-aware AppSec agent."
    p_h2_sub.font.size = Pt(11.5)
    p_h2_sub.font.color.rgb = C_MUTED

    # Left: The Problem
    draw_box(s2, Inches(0.8), Inches(1.45), Inches(5.6), Inches(5.5), bg=C_SURFACE)
    draw_pill(s2, Inches(1.05), Inches(1.7), "THE PROBLEM: B2B TRAVEL ATTACK SURFACE", border=C_BORDER_HI, text_color=C_WHITE)

    pb = s2.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(4.5))
    pbtf = pb.text_frame
    pbtf.word_wrap = True

    problems = [
        ("Daily Deploys vs Periodic Scans", "TBO engineers ship microservice updates constantly. Periodic scans leave multi-day windows where new vulnerabilities remain exposed in production."),
        ("Blind to Business Logic", "Conventional scanners spray generic SQLi/XSS payloads. They fail completely on business logic flaws: price tampering ($1 flights), cross-agency IDOR, and duplicate refunds."),
        ("Zombie & Shadow API Sprawl", "Deprecated legacy routes (e.g. /v1/ discounts) and unmapped debug endpoints (/internal/stats) sit open without authentication, inventory tracking, or traffic logs."),
        ("False-Positive Fatigue", "Developers are flooded with 100-page generic scanner PDF dumps lacking reproducible proofs, leading to ignored security alerts.")
    ]

    for title, desc in problems:
        p_t = pbtf.add_paragraph() if pbtf.paragraphs[0].text else pbtf.paragraphs[0]
        p_t.text = f"[X]  {title}"
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE
        p_t.space_after = Pt(2)

        p_d = pbtf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_MUTED
        p_d.space_after = Pt(10)

    # Right: The Architecture (5 Connected Pipeline Blocks)
    draw_box(s2, Inches(6.8), Inches(1.45), Inches(5.7), Inches(5.5), bg=C_SURFACE)
    draw_pill(s2, Inches(7.05), Inches(1.7), "OUR SOLUTION: ROUTEZERO 5-STAGE PIPELINE", border=C_BORDER_HI, text_color=C_WHITE)

    ab = s2.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(4.5))
    abtf = ab.text_frame
    abtf.word_wrap = True

    pipeline = [
        ("Stage 1: Autonomous Recon", "Ingests live traffic & HAR logs to extract endpoints, HTTP methods, query params, and body schemas with zero API documentation."),
        ("Stage 2: Zombie / Shadow Classifier", "Analyzes call history to tag Active APIs, forgotten routes with no traffic (Zombie), and undocumented public routes (Shadow)."),
        ("Stage 3: LLM Attack Planner", "Reasons over the travel business model to synthesize tailored exploits: IDOR across agency IDs, fare overrides, and state race conditions."),
        ("Stage 4: Safe Execution Sandbox", "Guarded by domain allowlisting, role-based test credential vault, adaptive rate-limiting, and an interactive Kill Switch."),
        ("Stage 5: Proof Verifier & OpenAPI Spec", "Validates hits with reproducible 1-click curl commands, assigns team ownership, and auto-generates an OpenAPI 3.0 catalog as a by-product.")
    ]

    for title, desc in pipeline:
        p_at = abtf.add_paragraph() if abtf.paragraphs[0].text else abtf.paragraphs[0]
        p_at.text = f"[>]  {title}"
        p_at.font.size = Pt(11.5)
        p_at.font.bold = True
        p_at.font.color.rgb = C_WHITE
        p_at.space_after = Pt(2)

        p_ad = abtf.add_paragraph()
        p_ad.text = desc
        p_ad.font.size = Pt(10)
        p_ad.font.color.rgb = C_MUTED
        p_ad.space_after = Pt(8)

    # ========================================================
    # SLIDE 3: WORKFLOW, VALIDATION & ROI (Content 2 of 2)
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)

    # Header
    h3 = s3.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.9))
    htf3 = h3.text_frame
    p_h3 = htf3.paragraphs[0]
    p_h3.text = "02 | End-to-End Workflow, Validated PoCs & TBO ROI"
    p_h3.font.size = Pt(21)
    p_h3.font.bold = True
    p_h3.font.color.rgb = C_WHITE

    p_h3_sub = htf3.add_paragraph()
    p_h3_sub.text = "Continuous automated security validation tested live against real B2B travel booking flows."
    p_h3_sub.font.size = Pt(11.5)
    p_h3_sub.font.color.rgb = C_MUTED

    # Top Row: 4 Quantitative Stat Cards
    stat_metrics = [
        ("<50ms", "Deploy-to-Attack Speed", "Reaction time from webhook to delta scan."),
        ("0%", "False Positive Rate", "Every bug validated with raw curl execution proof."),
        ("5 / 5", "Target Exploits Caught", "Caught all seeded logic & shadow vulnerabilities."),
        ("100%", "DPDP PII Protection", "Eliminates tenant data leaks & passport leaks.")
    ]

    for k, (metric_val, metric_label, metric_detail) in enumerate(stat_metrics):
        mx = Inches(0.8 + k * 2.98)
        draw_box(s3, mx, Inches(1.45), Inches(2.8), Inches(1.35), bg=C_SURFACE_ALT, border=C_BORDER)

        m_box = s3.shapes.add_textbox(mx + Inches(0.15), Inches(1.5), Inches(2.5), Inches(1.2))
        m_tf = m_box.text_frame
        m_tf.word_wrap = True

        m0 = m_tf.paragraphs[0]
        m0.text = metric_val
        m0.font.size = Pt(22)
        m0.font.bold = True
        m0.font.color.rgb = C_WHITE
        m0.space_after = Pt(2)

        m1 = m_tf.add_paragraph()
        m1.text = metric_label
        m1.font.size = Pt(10)
        m1.font.bold = True
        m1.font.color.rgb = C_LIGHT

        m2 = m_tf.add_paragraph()
        m2.text = metric_detail
        m2.font.size = Pt(8.5)
        m2.font.color.rgb = C_FAINT

    # Bottom Left: Confirmed Live Target Exploits
    draw_box(s3, Inches(0.8), Inches(3.0), Inches(5.6), Inches(4.0), bg=C_SURFACE)
    draw_pill(s3, Inches(1.05), Inches(3.2), "PROVEN LIVE EXPLOITS ON TARGET PLATFORM", border=C_BORDER_HI, text_color=C_WHITE)

    eb = s3.shapes.add_textbox(Inches(1.05), Inches(3.65), Inches(5.1), Inches(3.2))
    ebtf = eb.text_frame
    ebtf.word_wrap = True

    vuln_list = [
        ("Booking Price Tampering [CRITICAL]", "Overrode $450 flight ticket to $1.00 via client parameter trust in /api/v2/bookings/create."),
        ("Tenant IDOR & PII Exfiltration [CRITICAL]", "Agency-002 accessed Agency-001's customer booking data & leaked passport numbers."),
        ("Zombie Route Voucher Leak [HIGH]", "Unauthenticated deprecated /v1/ route leaked valid 50% internal staff discount code."),
        ("Shadow Admin Telemetry Leak [HIGH]", "Publicly exposed internal database connection string & runtime telemetry in /internal/stats."),
        ("Double Refund State Transition [HIGH]", "Executed infinite payout state loops without booking cancellation verification.")
    ]

    for v_title, v_desc in vuln_list:
        v_p = ebtf.add_paragraph() if ebtf.paragraphs[0].text else ebtf.paragraphs[0]
        v_p.text = f"- {v_title}"
        v_p.font.size = Pt(10)
        v_p.font.bold = True
        v_p.font.color.rgb = C_WHITE

        v_pd = ebtf.add_paragraph()
        v_pd.text = f"  {v_desc}"
        v_pd.font.size = Pt(9)
        v_pd.font.color.rgb = C_MUTED
        v_pd.space_after = Pt(4)

    # Bottom Right: Enterprise Value & TBO ROI
    draw_box(s3, Inches(6.8), Inches(3.0), Inches(5.7), Inches(4.0), bg=C_SURFACE)
    draw_pill(s3, Inches(7.05), Inches(3.2), "ENTERPRISE VALUE & ROI FOR TBO.COM", border=C_BORDER_HI, text_color=C_WHITE)

    rb = s3.shapes.add_textbox(Inches(7.05), Inches(3.65), Inches(5.2), Inches(3.2))
    rbtf = rb.text_frame
    rbtf.word_wrap = True

    roi_list = [
        ("Financial Loss Prevention", "Halts immediate revenue leakage from client fare manipulation, promo code reuse, and supplier refund pool depletion across massive booking volumes."),
        ("India DPDP Act 2023 Compliance", "Enforces tenant authorization barriers to protect passenger passport and personal data, mitigating devastating regulatory penalties."),
        ("Sub-Minute Mean Time to Remediation (MTTR)", "Engineers receive verified curl reproduction commands and developer code remediation snippets within seconds of deploying."),
        ("Automated API Governance", "Automatically generates and updates an OpenAPI 3.0 catalog as a by-product, permanently eliminating shadow API sprawl.")
    ]

    for r_title, r_desc in roi_list:
        r_p = rbtf.add_paragraph() if rbtf.paragraphs[0].text else rbtf.paragraphs[0]
        r_p.text = f"[#]  {r_title}"
        r_p.font.size = Pt(10.5)
        r_p.font.bold = True
        r_p.font.color.rgb = C_WHITE

        r_pd = rbtf.add_paragraph()
        r_pd.text = r_desc
        r_pd.font.size = Pt(9.5)
        r_pd.font.color.rgb = C_MUTED
        r_pd.space_after = Pt(5)

    # ========================================================
    # SLIDE 4: THANK YOU SLIDE
    # ========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)

    draw_box(s4, Inches(2.2), Inches(1.8), Inches(8.933), Inches(3.9), bg=C_SURFACE, border=C_BORDER)

    tyb = s4.shapes.add_textbox(Inches(2.7), Inches(2.2), Inches(8.0), Inches(3.1))
    tytf = tyb.text_frame
    tytf.word_wrap = True

    tp0 = tytf.paragraphs[0]
    tp0.text = "ROUTEZERO // TBO VOYAGEHACK 4.0"
    tp0.font.size = Pt(11)
    tp0.font.bold = True
    tp0.font.color.rgb = C_FAINT
    tp0.space_after = Pt(10)

    tp1 = tytf.add_paragraph()
    tp1.text = "Thank You."
    tp1.font.size = Pt(48)
    tp1.font.bold = True
    tp1.font.color.rgb = C_WHITE
    tp1.space_after = Pt(12)

    tp2 = tytf.add_paragraph()
    tp2.text = "Explore the working prototype, inspect reproducible proofs, and run live exploits:"
    tp2.font.size = Pt(13)
    tp2.font.color.rgb = C_MUTED
    tp2.space_after = Pt(20)

    tp3 = tytf.add_paragraph()
    tp3.text = "LIVE PLATFORM:   https://saisanthosh31.github.io/routezero/\nSOURCE REPO:     https://github.com/SaiSanthosh31/routezero"
    tp3.font.size = Pt(12)
    tp3.font.bold = True
    tp3.font.color.rgb = C_WHITE

    prs.save("RouteZero_VoyageHack_Submission.pptx")
    print("Designer presentation successfully compiled!")

if __name__ == "__main__":
    build_designer_deck()
