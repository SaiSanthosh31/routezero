import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_premium_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 Widescreen
    blank_layout = prs.slide_layouts[6]

    # Premium Monochrome Palette (Linear / Vercel style)
    C_BG = RGBColor(9, 9, 11)           # Zinc 950
    C_CARD = RGBColor(18, 18, 20)       # Dark Card surface
    C_CARD_ALT = RGBColor(24, 24, 27)   # Slightly elevated surface
    C_BORDER = RGBColor(45, 45, 50)     # Crisp 1px border
    C_BORDER_ACC = RGBColor(70, 70, 78) # Highlighted border
    C_WHITE = RGBColor(255, 255, 255)
    C_MUTED = RGBColor(161, 161, 170)   # Zinc 400
    C_FAINT = RGBColor(113, 113, 122)   # Zinc 500
    C_RED = RGBColor(239, 68, 68)       # Strict alert accent
    C_AMBER = RGBColor(245, 158, 11)   # Strict warning accent
    C_EMERALD = RGBColor(16, 185, 129)  # Verified accent

    def apply_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()

    def draw_panel(slide, x, y, w, h, bg_color=C_CARD, border_color=C_BORDER):
        panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
        panel.fill.solid()
        panel.fill.fore_color.rgb = bg_color
        panel.line.color.rgb = border_color
        panel.line.width = Pt(1)
        return panel

    def add_badge(slide, x, y, text, border_color=C_BORDER, text_color=C_MUTED):
        badge = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(len(text) * 0.085 + 0.3), Inches(0.32))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(15, 15, 17)
        badge.line.color.rgb = border_color
        badge.line.width = Pt(0.75)
        tf = badge.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = text_color
        return badge

    # ========================================================
    # SLIDE 1: COVER SLIDE
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    # Top metadata pill
    add_badge(s1, Inches(1.0), Inches(1.2), "VOYAGEHACK 4.0  |  TRACK 4: AGENTIC REAL-TIME DAST", border_color=C_BORDER_ACC, text_color=C_WHITE)

    # Title
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "RouteZero"
    p1.font.size = Pt(56)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "Autonomous Real-Time Application Security Agent for B2B Travel Platforms"
    p2.font.size = Pt(18)
    p2.font.color.rgb = C_MUTED

    # Bottom 3 Overview Metric Cards
    metrics = [
        ("AUTONOMOUS RECON", "Zero-Spec API Mapping", "Sniffs traffic & HAR logs to infer endpoints, query params & schemas without Swagger."),
        ("BUSINESS LOGIC", "Targeted Multi-Step Exploits", "AI reasons over travel workflows to catch $1 fare tampering, IDOR & duplicate refunds."),
        ("CONTINUOUS AUDIT", "<50ms CI/CD Reaction", "Reacts instantly to deployments, eliminates false positives & delivers 1-click curl PoCs.")
    ]

    for i, (m_tag, m_title, m_desc) in enumerate(metrics):
        cx = Inches(1.0 + i * 3.85)
        draw_panel(s1, cx, Inches(4.3), Inches(3.65), Inches(2.2), bg_color=C_CARD)
        
        box = s1.shapes.add_textbox(cx + Inches(0.2), Inches(4.45), Inches(3.25), Inches(1.9))
        btf = box.text_frame
        btf.word_wrap = True
        
        bp0 = btf.paragraphs[0]
        bp0.text = m_tag
        bp0.font.size = Pt(9.5)
        bp0.font.bold = True
        bp0.font.color.rgb = C_FAINT
        bp0.space_after = Pt(6)

        bp1 = btf.add_paragraph()
        bp1.text = m_title
        bp1.font.size = Pt(14)
        bp1.font.bold = True
        bp1.font.color.rgb = C_WHITE
        bp1.space_after = Pt(6)

        bp2 = btf.add_paragraph()
        bp2.text = m_desc
        bp2.font.size = Pt(10.5)
        bp2.font.color.rgb = C_MUTED

    # Footer
    f_box = s1.shapes.add_textbox(Inches(1.0), Inches(6.8), Inches(11.3), Inches(0.4))
    ftf = f_box.text_frame
    fp = ftf.paragraphs[0]
    fp.text = "LIVE PLATFORM: saisanthosh31.github.io/routezero   |   SOURCE: github.com/SaiSanthosh31/routezero"
    fp.font.size = Pt(10)
    fp.font.color.rgb = C_FAINT

    # ========================================================
    # SLIDE 2: PROBLEM VS ROUTEZERO ARCHITECTURE (Content Slide 1)
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)

    # Header Bar
    h_box = s2.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.9))
    htf = h_box.text_frame
    hp = htf.paragraphs[0]
    hp.text = "01 | The Problem & Architectural Solution"
    hp.font.size = Pt(22)
    hp.font.bold = True
    hp.font.color.rgb = C_WHITE

    hp_sub = htf.add_paragraph()
    hp_sub.text = "Transforming AppSec from slow, dumb vulnerability scanning to real-time, context-aware autonomous red-teaming."
    hp_sub.font.size = Pt(11.5)
    hp_sub.font.color.rgb = C_MUTED

    # Left Column: The Problem (Legacy Bottlenecks)
    draw_panel(s2, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4), bg_color=C_CARD)
    add_badge(s2, Inches(1.05), Inches(1.75), "LEGACY APPSEC LIMITATIONS", border_color=C_BORDER_ACC, text_color=C_WHITE)

    prob_box = s2.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(4.5))
    ptf = prob_box.text_frame
    ptf.word_wrap = True

    prob_items = [
        ("Frequent Deploys vs Blind Scans", "TBO ships daily microservice updates. Periodic weekly scans leave wide zero-day attack windows where new vulnerabilities live undetected."),
        ("Blind to Business Logic", "Conventional scanners spray generic SQLi/XSS payloads but completely miss business logic flaws: fare tampering ($1 tickets), cross-agency IDOR, and duplicate refund loops."),
        ("Zombie & Shadow API Blindspots", "Deprecated /v1/ routes and unmapped /internal/ telemetry endpoints remain open in production without authentication or traffic monitoring."),
        ("False Positive Alert Fatigue", "Security engineers drown in 100-page scanner PDF dumps containing hypothetical warnings with zero reproducible proof.")
    ]

    for title, desc in prob_items:
        p_t = ptf.add_paragraph() if ptf.paragraphs[0].text else ptf.paragraphs[0]
        p_t.text = f"[!]  {title}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE
        p_t.space_after = Pt(2)

        p_d = ptf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_MUTED
        p_d.space_after = Pt(10)

    # Right Column: RouteZero Architecture (5 Modular Agents)
    draw_panel(s2, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), bg_color=C_CARD)
    add_badge(s2, Inches(7.05), Inches(1.75), "ROUTZERO AGENTIC SYSTEM", border_color=C_BORDER_ACC, text_color=C_WHITE)

    arch_box = s2.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(4.5))
    atf = arch_box.text_frame
    atf.word_wrap = True

    arch_items = [
        ("1. Zero-Spec Recon Engine", "Ingests live traffic (HAR) to infer routes, parameters, and bodies without requiring OpenAPI documentation."),
        ("2. Shadow & Zombie Classifier", "Continuously isolates active production routes, abandoned /v1 routes (Zombie), and unlisted admin endpoints (Shadow)."),
        ("3. LLM-Driven Attack Planner", "Reasons over travel logic (pricing, tenant boundaries, refund flows) to synthesize targeted exploit payloads."),
        ("4. Safe Execution Sandbox", "Guarded by domain allowlisting, test credential vaults, adaptive rate-limiting, and an instant Kill Switch."),
        ("5. Proof Verifier & OpenAPI Generator", "Confirms vulnerabilities with 1-click reproduction curl scripts, team ownership, and auto-generates OpenAPI 3.0 specs.")
    ]

    for title, desc in arch_items:
        a_t = atf.add_paragraph() if atf.paragraphs[0].text else atf.paragraphs[0]
        a_t.text = f"[>]  {title}"
        a_t.font.size = Pt(12)
        a_t.font.bold = True
        a_t.font.color.rgb = C_WHITE
        a_t.space_after = Pt(2)

        a_d = atf.add_paragraph()
        a_d.text = desc
        a_d.font.size = Pt(10)
        a_d.font.color.rgb = C_MUTED
        a_d.space_after = Pt(9)

    # ========================================================
    # SLIDE 3: WORKFLOW, METRICS & BUSINESS IMPACT (Content Slide 2)
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)

    # Header Bar
    h_box3 = s3.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.9))
    htf3 = h_box3.text_frame
    hp3 = htf3.paragraphs[0]
    hp3.text = "02 | End-to-End Workflow, Validated PoCs & TBO ROI"
    hp3.font.size = Pt(22)
    hp3.font.bold = True
    hp3.font.color.rgb = C_WHITE

    hp3_sub = htf3.add_paragraph()
    hp3_sub.text = "Proven automated testing against live B2B travel flows with measurable speed, accuracy, and compliance impact."
    hp3_sub.font.size = Pt(11.5)
    hp3_sub.font.color.rgb = C_MUTED

    # 4 Key Quantitative Metrics across top
    metric_cards = [
        ("<50ms", "Deploy-to-Attack Speed", "Reaction time via CI/CD deploy webhook."),
        ("0%", "False Positive Rate", "Every finding verified by minimal curl PoC."),
        ("5 / 5", "Critical Exploits Caught", "Caught all seeded logic & shadow vulnerabilities."),
        ("100%", "DPDP PII Protection", "Eliminates tenant data leaks & passport leaks.")
    ]

    for j, (num, lbl, sub_lbl) in enumerate(metric_cards):
        mx = Inches(0.8 + j * 2.98)
        draw_panel(s3, mx, Inches(1.5), Inches(2.8), Inches(1.4), bg_color=C_CARD_ALT)
        
        mbox = s3.shapes.add_textbox(mx + Inches(0.15), Inches(1.55), Inches(2.5), Inches(1.3))
        mtf = mbox.text_frame
        mtf.word_wrap = True
        
        mp0 = mtf.paragraphs[0]
        mp0.text = num
        mp0.font.size = Pt(24)
        mp0.font.bold = True
        mp0.font.color.rgb = C_WHITE
        mp0.space_after = Pt(2)

        mp1 = mtf.add_paragraph()
        mp1.text = lbl
        mp1.font.size = Pt(10.5)
        mp1.font.bold = True
        mp1.font.color.rgb = C_MUTED

        mp2 = mtf.add_paragraph()
        mp2.text = sub_lbl
        mp2.font.size = Pt(8.5)
        mp2.font.color.rgb = C_FAINT

    # Bottom Left: Proven Exploits on Target App
    draw_panel(s3, Inches(0.8), Inches(3.1), Inches(5.6), Inches(3.8), bg_color=C_CARD)
    add_badge(s3, Inches(1.05), Inches(3.3), "VALIDATED TARGET EXPLOITS", border_color=C_BORDER_ACC, text_color=C_WHITE)

    exp_box = s3.shapes.add_textbox(Inches(1.05), Inches(3.7), Inches(5.1), Inches(3.0))
    etf = exp_box.text_frame
    etf.word_wrap = True

    exploits = [
        ("Booking Price Tampering (CRITICAL)", "Overrode $450 flight fare to $1.00 via client parameter tampering in /api/v2/bookings/create."),
        ("Tenant IDOR & PII Exfiltration (CRITICAL)", "Agency-002 queried Agency-001's customer booking records & extracted passport PII."),
        ("Zombie Route Voucher Leak (HIGH)", "Unauthenticated deprecated /v1/ route leaked valid 50% internal staff discount code."),
        ("Shadow Admin Telemetry Leak (HIGH)", "Exposed internal database connection string & system environment telemetry."),
        ("Duplicate Refund Abuse (HIGH)", "Infinite payout state transition without booking cancellation validation.")
    ]

    for exp_title, exp_desc in exploits:
        ep_t = etf.add_paragraph() if etf.paragraphs[0].text else etf.paragraphs[0]
        ep_t.text = f"- {exp_title}"
        ep_t.font.size = Pt(10.5)
        ep_t.font.bold = True
        ep_t.font.color.rgb = C_WHITE

        ep_d = etf.add_paragraph()
        ep_d.text = f"  {exp_desc}"
        ep_d.font.size = Pt(9.5)
        ep_d.font.color.rgb = C_MUTED
        ep_d.space_after = Pt(4)

    # Bottom Right: Enterprise Value & TBO ROI
    draw_panel(s3, Inches(6.8), Inches(3.1), Inches(5.7), Inches(3.8), bg_color=C_CARD)
    add_badge(s3, Inches(7.05), Inches(3.3), "TBO ENTERPRISE VALUE & ROI", border_color=C_BORDER_ACC, text_color=C_WHITE)

    roi_box = s3.shapes.add_textbox(Inches(7.05), Inches(3.7), Inches(5.2), Inches(3.0))
    rtf = roi_box.text_frame
    rtf.word_wrap = True

    roi_items = [
        ("Revenue Leakage Elimination", "Stops margin theft, manipulated vouchers, and escrow payout depletion across high-volume supplier channels."),
        ("India DPDP Act 2023 Compliance", "Enforces strict tenant isolation and prevents devastating regulatory fines for customer data breaches."),
        ("Sub-Minute Mean Time to Remediation", "Developers receive verified reproduction curl commands and exact code fixes instantly upon git push."),
        ("Continuous Automated Governance", "Generates and maintains a live OpenAPI 3.0 catalog as a by-product, ending shadow API sprawl.")
    ]

    for roi_t, roi_d in roi_items:
        rp_t = rtf.add_paragraph() if rtf.paragraphs[0].text else rtf.paragraphs[0]
        rp_t.text = f"[#]  {roi_t}"
        rp_t.font.size = Pt(11)
        rp_t.font.bold = True
        rp_t.font.color.rgb = C_WHITE

        rp_d = rtf.add_paragraph()
        rp_d.text = roi_d
        rp_d.font.size = Pt(9.5)
        rp_d.font.color.rgb = C_MUTED
        rp_d.space_after = Pt(6)

    # ========================================================
    # SLIDE 4: THANK YOU SLIDE
    # ========================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)

    draw_panel(s4, Inches(2.2), Inches(1.8), Inches(8.933), Inches(3.9), bg_color=C_CARD)

    ty_box = s4.shapes.add_textbox(Inches(2.7), Inches(2.2), Inches(8.0), Inches(3.1))
    tytf = ty_box.text_frame
    tytf.word_wrap = True

    tp0 = tytf.paragraphs[0]
    tp0.text = "ROUTEZERO"
    tp0.font.size = Pt(12)
    tp0.font.bold = True
    tp0.font.color.rgb = C_FAINT
    tp0.space_after = Pt(10)

    tp1 = tytf.add_paragraph()
    tp1.text = "Thank You."
    tp1.font.size = Pt(50)
    tp1.font.bold = True
    tp1.font.color.rgb = C_WHITE
    tp1.space_after = Pt(12)

    tp2 = tytf.add_paragraph()
    tp2.text = "Explore the working prototype, inspect reproducible proofs, and test live exploits:"
    tp2.font.size = Pt(13)
    tp2.font.color.rgb = C_MUTED
    tp2.space_after = Pt(20)

    tp3 = tytf.add_paragraph()
    tp3.text = "LIVE PLATFORM:   https://saisanthosh31.github.io/routezero/\nSOURCE REPO:     https://github.com/SaiSanthosh31/routezero"
    tp3.font.size = Pt(12.5)
    tp3.font.bold = True
    tp3.font.color.rgb = C_WHITE

    prs.save("RouteZero_VoyageHack_Submission.pptx")
    print("Premium presentation generated successfully!")

if __name__ == "__main__":
    build_premium_deck()
