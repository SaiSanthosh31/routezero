import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_human_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 widescreen
    blank_layout = prs.slide_layouts[6]

    # Elegant, Human Executive Palette (Muted, zero loud neons)
    BG_COLOR = RGBColor(18, 19, 23)        # Warm dark charcoal / slate
    CARD_BG = RGBColor(27, 29, 36)         # Soft card surface
    BORDER_COLOR = RGBColor(46, 49, 61)    # Muted natural border
    TEXT_MAIN = RGBColor(255, 255, 255)    # Clean White
    TEXT_SUB = RGBColor(165, 170, 185)     # Warm Muted Gray
    TEXT_FAINT = RGBColor(115, 120, 135)   # Subtle Gray
    ACCENT_MUTE = RGBColor(130, 160, 210)  # Soft Muted Blue (Understated)

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()

    def draw_card(slide, left, top, width, height):
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        card.line.width = Pt(1)
        return card

    # ========================================================
    # SLIDE 1: COVER
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    tbox1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(10.9), Inches(4.5))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "TBO VOYAGEHACK 4.0  *  TRACK 4: AGENTIC REAL-TIME DAST"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_MUTE
    p0.space_after = Pt(16)

    p1 = tf1.add_paragraph()
    p1.text = "RouteZero"
    p1.font.size = Pt(56)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MAIN
    p1.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "Autonomous API Security Testing for Live Travel Platforms"
    p2.font.size = Pt(22)
    p2.font.color.rgb = TEXT_SUB
    p2.space_after = Pt(28)

    p3 = tf1.add_paragraph()
    p3.text = "An intelligent agent that continuously maps APIs from live traffic, discovers hidden & zombie endpoints, and safely verifies business-logic vulnerabilities before attackers do."
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_FAINT
    p3.space_after = Pt(36)

    p4 = tf1.add_paragraph()
    p4.text = "Live Interactive Demo: saisanthosh31.github.io/routezero   *   GitHub: github.com/SaiSanthosh31/routezero"
    p4.font.size = Pt(12)
    p4.font.color.rgb = TEXT_SUB

    # ========================================================
    # SLIDE 2: THE PROBLEM & OUR SOLUTION (Content Slide 1)
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)

    # Clean Header
    h2 = s2.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.3), Inches(0.9))
    htf2 = h2.text_frame
    hp2 = htf2.paragraphs[0]
    hp2.text = "The Problem & What We Built"
    hp2.font.size = Pt(28)
    hp2.font.bold = True
    hp2.font.color.rgb = TEXT_MAIN
    
    hp2_sub = htf2.add_paragraph()
    hp2_sub.text = "Why conventional security scanners fail at TBO, and how RouteZero solves it."
    hp2_sub.font.size = Pt(14)
    hp2_sub.font.color.rgb = TEXT_SUB

    # Left Column: The Problem at TBO
    draw_card(s2, Inches(1.0), Inches(1.7), Inches(5.4), Inches(5.2))
    pbox = s2.shapes.add_textbox(Inches(1.3), Inches(2.0), Inches(4.8), Inches(4.6))
    ptf = pbox.text_frame
    ptf.word_wrap = True

    p_title = ptf.paragraphs[0]
    p_title.text = "Where Traditional Tools Fail"
    p_title.font.size = Pt(18)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_MAIN
    p_title.space_after = Pt(16)

    prob_points = [
        ("Daily Deploys vs Slow Scans", "TBO updates booking APIs daily. Periodic weekly scans leave wide time windows where vulnerable code sits live in production."),
        ("Blind to Business Logic", "Scanners spray generic SQL injection but completely miss travel logic flaws—like changing a $450 flight to $1 or stealing booking records across agencies (IDOR)."),
        ("Zombie & Shadow APIs", "Old deprecated routes (like abandoned /v1 discounts) and unmapped debug endpoints stay alive without anyone tracking them.")
    ]

    for title, desc in prob_points:
        pt = ptf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = ACCENT_MUTE
        pt.space_after = Pt(2)

        pd = ptf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(13)
        pd.font.color.rgb = TEXT_SUB
        pd.space_after = Pt(14)

    # Right Column: The Solution
    draw_card(s2, Inches(6.9), Inches(1.7), Inches(5.4), Inches(5.2))
    sbox = s2.shapes.add_textbox(Inches(7.2), Inches(2.0), Inches(4.8), Inches(4.6))
    stf = sbox.text_frame
    stf.word_wrap = True

    s_title = stf.paragraphs[0]
    s_title.text = "How RouteZero Works"
    s_title.font.size = Pt(18)
    s_title.font.bold = True
    s_title.font.color.rgb = TEXT_MAIN
    s_title.space_after = Pt(16)

    sol_points = [
        ("Zero-Spec API Mapping", "Listens to live traffic logs (HAR) to automatically map active endpoints, query parameters, and payload schemas with zero manual documentation."),
        ("Smart Attack Planning", "Uses an LLM agent to understand what each endpoint does and crafts targeted business-logic exploits instead of spraying random payloads."),
        ("Safe Exploit Sandbox & Auto-Fix", "Executes attacks safely with rate limits, verifies the bug with a reproducible curl script, and gives developers ready-to-merge code fixes.")
    ]

    for title, desc in sol_points:
        st = stf.add_paragraph()
        st.text = title
        st.font.size = Pt(15)
        st.font.bold = True
        st.font.color.rgb = ACCENT_MUTE
        st.space_after = Pt(2)

        sd = stf.add_paragraph()
        sd.text = desc
        sd.font.size = Pt(13)
        sd.font.color.rgb = TEXT_SUB
        sd.space_after = Pt(14)

    # ========================================================
    # SLIDE 3: VALIDATED RESULTS & TBO ROI (Content Slide 2)
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)

    h3 = s3.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.3), Inches(0.9))
    htf3 = h3.text_frame
    hp3 = htf3.paragraphs[0]
    hp3.text = "Live Results & Value for TBO"
    hp3.font.size = Pt(28)
    hp3.font.bold = True
    hp3.font.color.rgb = TEXT_MAIN
    
    hp3_sub = htf3.add_paragraph()
    hp3_sub.text = "Tested and verified against live travel booking APIs with zero false positives."
    hp3_sub.font.size = Pt(14)
    hp3_sub.font.color.rgb = TEXT_SUB

    # Top 3 Clean Stat Callouts
    top_stats = [
        ("<50ms", "Deploy Reaction Time", "Delta scan triggered on git deploy webhook"),
        ("5 / 5", "Critical Bugs Caught", "All seeded business logic & shadow flaws caught"),
        ("0%", "False Positive Rate", "Every vulnerability proven with a working curl script")
    ]

    for k, (num, label, desc) in enumerate(top_stats):
        cx = Inches(1.0 + k * 3.85)
        draw_card(s3, cx, Inches(1.7), Inches(3.6), Inches(1.6))
        
        box = s3.shapes.add_textbox(cx + Inches(0.25), Inches(1.8), Inches(3.1), Inches(1.4))
        btf = box.text_frame
        btf.word_wrap = True

        p_num = btf.paragraphs[0]
        p_num.text = num
        p_num.font.size = Pt(32)
        p_num.font.bold = True
        p_num.font.color.rgb = TEXT_MAIN
        p_num.space_after = Pt(2)

        p_lbl = btf.add_paragraph()
        p_lbl.text = label
        p_lbl.font.size = Pt(13)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = ACCENT_MUTE

        p_desc = btf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_FAINT

    # Bottom Left: What the Agent Caught on Target
    draw_card(s3, Inches(1.0), Inches(3.55), Inches(5.4), Inches(3.35))
    l_box = s3.shapes.add_textbox(Inches(1.3), Inches(3.75), Inches(4.8), Inches(2.95))
    ltf = l_box.text_frame
    ltf.word_wrap = True

    ltitle = ltf.paragraphs[0]
    ltitle.text = "Proven Attacks on Live Mock Target"
    ltitle.font.size = Pt(16)
    ltitle.font.bold = True
    ltitle.font.color.rgb = TEXT_MAIN
    ltitle.space_after = Pt(10)

    exploits = [
        ("Price Tampering:", "Booked a $450 flight for $1.00 by tampering with client request payload."),
        ("Cross-Agency IDOR:", "Agency 2 extracted Agency 1 customer booking records & passport data."),
        ("Zombie Promo Leak:", "Unauthenticated legacy /v1 route leaked active 50% discount vouchers."),
        ("Shadow API Leak:", "Internal debug route leaked database credentials and server telemetry.")
    ]

    for label, desc in exploits:
        p = ltf.add_paragraph()
        p.text = f"- {label} {desc}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_SUB
        p.space_after = Pt(6)

    # Bottom Right: Value for TBO
    draw_card(s3, Inches(6.9), Inches(3.55), Inches(5.4), Inches(3.35))
    r_box = s3.shapes.add_textbox(Inches(7.2), Inches(3.75), Inches(4.8), Inches(2.95))
    rtf = r_box.text_frame
    rtf.word_wrap = True

    rtitle = rtf.paragraphs[0]
    rtitle.text = "What This Means for TBO.com"
    rtitle.font.size = Pt(16)
    rtitle.font.bold = True
    rtitle.font.color.rgb = TEXT_MAIN
    rtitle.space_after = Pt(10)

    values = [
        ("Stops Revenue Leakage:", "Prevents direct financial losses from price tampering and discount abuse across high-volume booking traffic."),
        ("Protects Customer Privacy:", "Enforces agency tenant boundaries to comply with India's DPDP Act 2023 and prevent passport leaks."),
        ("Instant Developer Fixes:", "Developers receive exact reproduction curls and code snippets within seconds of deploying."),
        ("Auto OpenAPI Documentation:", "Maintains an up-to-date OpenAPI 3.0 catalog as a by-product, ending unmapped API sprawl.")
    ]

    for label, desc in values:
        p = rtf.add_paragraph()
        p.text = f"- {label} {desc}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_SUB
        p.space_after = Pt(6)

    # ========================================================
    # SLIDE 4: THANK YOU
    # ========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)

    draw_card(s4, Inches(2.0), Inches(1.8), Inches(9.333), Inches(3.8))
    ty_box = s4.shapes.add_textbox(Inches(2.6), Inches(2.3), Inches(8.133), Inches(2.8))
    tytf = ty_box.text_frame
    tytf.word_wrap = True

    p_tag = tytf.paragraphs[0]
    p_tag.text = "VOYAGEHACK 4.0  *  ROUTEZERO"
    p_tag.font.size = Pt(12)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_MUTE
    p_tag.space_after = Pt(12)

    p_ty = tytf.add_paragraph()
    p_ty.text = "Thank You"
    p_ty.font.size = Pt(54)
    p_ty.font.bold = True
    p_ty.font.color.rgb = TEXT_MAIN
    p_ty.space_after = Pt(14)

    p_links = tytf.add_paragraph()
    p_links.text = "Live Interactive Demo:   https://saisanthosh31.github.io/routezero/\nGitHub Repository:       https://github.com/SaiSanthosh31/routezero"
    p_links.font.size = Pt(15)
    p_links.font.color.rgb = TEXT_SUB

    prs.save("RouteZero_VoyageHack_Submission.pptx")
    print("Human-crafted presentation successfully generated!")

if __name__ == "__main__":
    build_human_deck()
