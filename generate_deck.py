import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_modern_pitch_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 Widescreen
    blank_layout = prs.slide_layouts[6]

    # Modern Tech Palette: Rich Midnight Slate with Cyan & Crisp White
    C_BG = RGBColor(11, 15, 25)          # Deep Midnight Slate (#0b0f19)
    C_CARD = RGBColor(19, 27, 46)        # Rich Navy Slate Surface (#131b2e)
    C_BORDER = RGBColor(35, 48, 77)      # Clean Slate Border (#23304d)
    C_CYAN = RGBColor(56, 189, 248)      # Electric Cyan Highlight (#38bdf8)
    C_WHITE = RGBColor(255, 255, 255)
    C_LIGHT = RGBColor(241, 245, 249)    # Slate 100
    C_GRAY = RGBColor(148, 163, 184)     # Slate 400
    C_RED = RGBColor(239, 68, 68)        # Critical Accent
    C_GREEN = RGBColor(52, 211, 153)     # Emerald Verified

    def apply_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()

    def draw_card(slide, x, y, w, h, bg=C_CARD, border=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = bg
        card.line.color.rgb = border
        card.line.width = Pt(1.5)
        return card

    def add_tag(slide, x, y, text, color=C_CYAN):
        tag_w = Inches(len(text) * 0.11 + 0.4)
        t_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, tag_w, Inches(0.38))
        t_shape.fill.solid()
        t_shape.fill.fore_color.rgb = RGBColor(16, 23, 38)
        t_shape.line.color.rgb = color
        t_shape.line.width = Pt(1)
        tf = t_shape.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = color
        return t_shape

    # ========================================================
    # SLIDE 1: COVER SLIDE
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    # Category Pill
    add_tag(s1, Inches(1.2), Inches(1.2), "VOYAGEHACK 4.0  //  TRACK 4: AGENTIC REAL-TIME DAST", color=C_CYAN)

    # Hero Title (Large & Bold)
    h_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.3))
    htf = h_box.text_frame
    htf.word_wrap = True
    
    hp1 = htf.paragraphs[0]
    hp1.text = "RouteZero"
    hp1.font.size = Pt(60)
    hp1.font.bold = True
    hp1.font.color.rgb = C_WHITE
    hp1.space_after = Pt(10)

    hp2 = htf.add_paragraph()
    hp2.text = "Autonomous Real-Time Security Agent for B2B Travel Platforms"
    hp2.font.size = Pt(22)
    hp2.font.color.rgb = C_CYAN
    hp2.space_after = Pt(6)

    hp3 = htf.add_paragraph()
    hp3.text = "Detects hidden APIs, plans targeted business-logic exploits & proves vulnerabilities in seconds."
    hp3.font.size = Pt(15)
    hp3.font.color.rgb = C_GRAY

    # 3 Large Feature Columns
    cols = [
        ("ZERO-SPEC RECON", "Maps all APIs automatically from traffic logs with zero documentation."),
        ("AI ATTACK ENGINE", "Exploits real business-logic flaws: $1 flight tickets & IDOR passport leaks."),
        ("REAL-TIME RESPONSE", "Reacts to code deploys in <50ms with 0% false positives & verified proofs.")
    ]

    for i, (title, desc) in enumerate(cols):
        cx = Inches(1.2 + i * 3.75)
        draw_card(s1, cx, Inches(4.5), Inches(3.45), Inches(2.0))
        
        cbox = s1.shapes.add_textbox(cx + Inches(0.25), Inches(4.65), Inches(2.95), Inches(1.7))
        ctf = cbox.text_frame
        ctf.word_wrap = True
        
        cp0 = ctf.paragraphs[0]
        cp0.text = title
        cp0.font.size = Pt(13)
        cp0.font.bold = True
        cp0.font.color.rgb = C_CYAN
        cp0.space_after = Pt(8)

        cp1 = ctf.add_paragraph()
        cp1.text = desc
        cp1.font.size = Pt(14)
        cp1.font.color.rgb = C_LIGHT

    # ========================================================
    # SLIDE 2: THE PROBLEM & SOLUTION (Content Slide 1)
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)

    # Big Header
    head2 = s2.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.3), Inches(1.0))
    h2_tf = head2.text_frame
    p_h2 = h2_tf.paragraphs[0]
    p_h2.text = "The Problem & Our Agentic Solution"
    p_h2.font.size = Pt(32)
    p_h2.font.bold = True
    p_h2.font.color.rgb = C_WHITE

    p_h2_sub = h2_tf.add_paragraph()
    p_h2_sub.text = "Why traditional security tools fail on TBO travel APIs — and how RouteZero fixes it."
    p_h2_sub.font.size = Pt(16)
    p_h2_sub.font.color.rgb = C_GRAY

    # Left: The 3 Core Problems (Big & Readable)
    draw_card(s2, Inches(1.0), Inches(1.8), Inches(5.35), Inches(5.0))
    add_tag(s2, Inches(1.3), Inches(2.1), "THE PROBLEM TODAY", color=C_RED)

    p_box = s2.shapes.add_textbox(Inches(1.3), Inches(2.65), Inches(4.75), Inches(3.9))
    ptf = p_box.text_frame
    ptf.word_wrap = True

    probs = [
        ("Daily Deploys vs Slow Scans", "TBO updates APIs daily. Traditional scanners run weekly, leaving wide windows for hackers to attack."),
        ("Blind to Business Logic", "Scanners spray generic SQL injection but completely miss travel logic bugs like $1 flight price tampering and cross-agency IDOR."),
        ("Forgotten Zombie & Shadow APIs", "Deprecated /v1 routes and undocumented debug endpoints stay live and unprotected in production.")
    ]

    for title, desc in probs:
        p_t = ptf.add_paragraph() if ptf.paragraphs[0].text else ptf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE
        p_t.space_after = Pt(3)

        p_d = ptf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(14)
        p_d.font.color.rgb = C_GRAY
        p_d.space_after = Pt(14)

    # Right: The RouteZero Solution (Big & Readable)
    draw_card(s2, Inches(6.98), Inches(1.8), Inches(5.35), Inches(5.0))
    add_tag(s2, Inches(7.28), Inches(2.1), "OUR SOLUTION: ROUTEZERO", color=C_CYAN)

    s_box = s2.shapes.add_textbox(Inches(7.28), Inches(2.65), Inches(4.75), Inches(3.9))
    stf = s_box.text_frame
    stf.word_wrap = True

    solns = [
        ("Zero-Spec API Mapping", "Passively sniffs traffic to discover all active, zombie (/v1), and shadow endpoints without Swagger."),
        ("LLM Attack Planner", "Reasons like a human hacker to test travel workflows (fare manipulation, customer passport leaks, duplicate refunds)."),
        ("Safe Exploit Sandbox & Auto-Fix", "Safely fires attacks with rate limiting, verifies with minimal curl proof, and generates instant code fixes.")
    ]

    for title, desc in solns:
        s_t = stf.add_paragraph() if stf.paragraphs[0].text else stf.paragraphs[0]
        s_t.text = title
        s_t.font.size = Pt(16)
        s_t.font.bold = True
        s_t.font.color.rgb = C_WHITE
        s_t.space_after = Pt(3)

        s_d = stf.add_paragraph()
        s_d.text = desc
        s_d.font.size = Pt(14)
        s_d.font.color.rgb = C_GRAY
        s_d.space_after = Pt(14)

    # ========================================================
    # SLIDE 3: WORKFLOW & TBO ROI (Content Slide 2)
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)

    head3 = s3.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.3), Inches(1.0))
    h3_tf = head3.text_frame
    p_h3 = h3_tf.paragraphs[0]
    p_h3.text = "Validated Results & Impact for TBO"
    p_h3.font.size = Pt(32)
    p_h3.font.bold = True
    p_h3.font.color.rgb = C_WHITE

    p_h3_sub = h3_tf.add_paragraph()
    p_h3_sub.text = "Demonstrated live on real travel booking flows with zero false positives."
    p_h3_sub.font.size = Pt(16)
    p_h3_sub.font.color.rgb = C_GRAY

    # Top 3 Big Stat Numbers
    stats = [
        ("<50ms", "Deploy-to-Attack Reaction Time", "Delta scan triggered on git deploy"),
        ("5 / 5", "Critical Vulnerabilities Caught", "Caught $1 price tamper, IDOR & leaks"),
        ("0%", "False Positive Rate", "Every exploit verified with curl PoC")
    ]

    for k, (num, lbl, sub_lbl) in enumerate(stats):
        sx = Inches(1.0 + k * 3.85)
        draw_card(s3, sx, Inches(1.8), Inches(3.6), Inches(1.6), bg=RGBColor(16, 24, 42))

        s_box = s3.shapes.add_textbox(sx + Inches(0.2), Inches(1.9), Inches(3.2), Inches(1.4))
        stf = s_box.text_frame
        stf.word_wrap = True

        sp0 = stf.paragraphs[0]
        sp0.text = num
        sp0.font.size = Pt(38)
        sp0.font.bold = True
        sp0.font.color.rgb = C_CYAN
        sp0.space_after = Pt(2)

        sp1 = stf.add_paragraph()
        sp1.text = lbl
        sp1.font.size = Pt(13)
        sp1.font.bold = True
        sp1.font.color.rgb = C_WHITE

        sp2 = stf.add_paragraph()
        sp2.text = sub_lbl
        sp2.font.size = Pt(11)
        sp2.font.color.rgb = C_GRAY

    # Bottom Left: Tested Exploits (Large & Punchy)
    draw_card(s3, Inches(1.0), Inches(3.65), Inches(5.35), Inches(3.2))
    add_tag(s3, Inches(1.3), Inches(3.9), "5 TESTED EXPLOITS (PROVEN LIVE)", color=C_CYAN)

    eb = s3.shapes.add_textbox(Inches(1.3), Inches(4.4), Inches(4.75), Inches(2.3))
    etf = eb.text_frame
    etf.word_wrap = True

    exploits = [
        ("Price Tampering (CRITICAL):", "Booked $450 flight for $1.00 via client parameter override."),
        ("Cross-Agency IDOR (CRITICAL):", "Agency B exfiltrated Agency A customer passport PII."),
        ("Zombie Promo Leak (HIGH):", "Deprecated /v1 route leaked valid 50% discount codes."),
        ("Shadow API Leak (HIGH):", "Exposed internal database connection & debug telemetry.")
    ]

    for title, desc in exploits:
        ep_t = etf.add_paragraph() if etf.paragraphs[0].text else etf.paragraphs[0]
        ep_t.text = f"{title} {desc}"
        ep_t.font.size = Pt(12.5)
        ep_t.font.color.rgb = C_LIGHT
        ep_t.space_after = Pt(6)

    # Bottom Right: Enterprise Value for TBO
    draw_card(s3, Inches(6.98), Inches(3.65), Inches(5.35), Inches(3.2))
    add_tag(s3, Inches(7.28), Inches(3.9), "BUSINESS IMPACT FOR TBO.COM", color=C_GREEN)

    rb = s3.shapes.add_textbox(Inches(7.28), Inches(4.4), Inches(4.75), Inches(2.3))
    rtf = rb.text_frame
    rtf.word_wrap = True

    rois = [
        ("Stops Revenue Theft:", "Prevents massive financial loss from fare tampering and refund draining."),
        ("DPDP Act Compliance:", "Eliminates customer passport and PII leaks across agencies."),
        ("Instant Remediation:", "Developers get ready-to-merge code patches within seconds of deploying."),
        ("Auto API Spec Bonus:", "Generates live OpenAPI 3.0 docs automatically as a by-product.")
    ]

    for title, desc in rois:
        rp_t = rtf.add_paragraph() if rtf.paragraphs[0].text else rtf.paragraphs[0]
        rp_t.text = f"{title} {desc}"
        rp_t.font.size = Pt(12.5)
        rp_t.font.color.rgb = C_LIGHT
        rp_t.space_after = Pt(6)

    # ========================================================
    # SLIDE 4: THANK YOU SLIDE
    # ========================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)

    draw_card(s4, Inches(2.0), Inches(1.8), Inches(9.333), Inches(3.8), bg=C_CARD)

    tyb = s4.shapes.add_textbox(Inches(2.5), Inches(2.2), Inches(8.333), Inches(3.0))
    tytf = tyb.text_frame
    tytf.word_wrap = True

    tp0 = tytf.paragraphs[0]
    tp0.text = "ROUTEZERO // TBO VOYAGEHACK 4.0"
    tp0.font.size = Pt(13)
    tp0.font.bold = True
    tp0.font.color.rgb = C_CYAN
    tp0.space_after = Pt(12)

    tp1 = tytf.add_paragraph()
    tp1.text = "Thank You"
    tp1.font.size = Pt(56)
    tp1.font.bold = True
    tp1.font.color.rgb = C_WHITE
    tp1.space_after = Pt(14)

    tp2 = tytf.add_paragraph()
    tp2.text = "LIVE PLATFORM:   https://saisanthosh31.github.io/routezero/\nSOURCE CODE:     https://github.com/SaiSanthosh31/routezero"
    tp2.font.size = Pt(16)
    tp2.font.bold = True
    tp2.font.color.rgb = C_LIGHT

    prs.save("RouteZero_VoyageHack_Submission.pptx")
    print("Clean modern pitch deck successfully generated!")

if __name__ == "__main__":
    build_modern_pitch_deck()
