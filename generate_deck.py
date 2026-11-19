import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_exact_template_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 Widescreen standard
    blank_layout = prs.slide_layouts[6]

    # Exact palette extracted from user reference images:
    C_TEAL_DARK = RGBColor(18, 52, 59)      # #12343B - Dark Teal Sidebar, Header Cards
    C_CORAL     = RGBColor(240, 138, 75)    # #F08A4B - Orange tags, dividers, root cause
    C_SAGE_TEAL = RGBColor(42, 157, 143)    # #2A9D8F - Sage Teal pills & subheadings
    C_LIGHT_BG  = RGBColor(255, 255, 255)   # #FFFFFF - Crisp white background
    C_ROW_BG    = RGBColor(238, 245, 247)   # #EEF5F7 - Soft blue-gray pill rows
    C_PEACH_BOX = RGBColor(253, 235, 221)   # #FDEBDD - Peach container for Pipeline
    C_WHITE     = RGBColor(255, 255, 255)
    C_TEXT_DARK = RGBColor(25, 30, 35)      # Charcoal primary text
    C_TEXT_MUTED= RGBColor(85, 95, 105)     # Slate secondary text

    def set_white_canvas(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_LIGHT_BG
        bg.line.fill.background()

    def add_shape(slide, x, y, w, h, fill_rgb, rounded=True, border_rgb=None):
        st = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
        s = slide.shapes.add_shape(st, x, y, w, h)
        s.fill.solid()
        s.fill.fore_color.rgb = fill_rgb
        if border_rgb:
            s.line.color.rgb = border_rgb
            s.line.width = Pt(1)
        else:
            s.line.fill.background()
        return s

    def add_footer(slide):
        f = slide.shapes.add_textbox(Inches(7.5), Inches(7.05), Inches(5.3), Inches(0.35))
        p = f.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        p.text = "ROUTEZERO  ·  VOYAGEHACK 4.0  ·  DESIGN THINKING"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = C_SAGE_TEAL

    # ========================================================
    # SLIDE 1: COVER SLIDE (Full-bleed Left Sidebar)
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s1)

    # Full Bleed Left Dark Teal Column
    add_shape(s1, Inches(0.0), Inches(0.0), Inches(4.5), Inches(7.5), C_TEAL_DARK, rounded=False)

    # Subtitle tag in Teal bar
    t_tag1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(3.4), Inches(0.4))
    pt0 = t_tag1.text_frame.paragraphs[0]
    pt0.text = "TRACK 4 · AGENTIC REAL-TIME DAST"
    pt0.font.size = Pt(11)
    pt0.font.bold = True
    pt0.font.color.rgb = C_CORAL

    # Title in Teal bar
    t_title1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(3.4), Inches(2.2))
    tf_t1 = t_title1.text_frame
    tf_t1.word_wrap = True
    p1 = tf_t1.paragraphs[0]
    p1.text = "RouteZero"
    p1.font.size = Pt(46)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(8)

    p1_sub = tf_t1.add_paragraph()
    p1_sub.text = "Autonomous API Security Agent"
    p1_sub.font.size = Pt(17)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = C_CORAL

    # Orange horizontal line
    add_shape(s1, Inches(0.8), Inches(4.2), Inches(0.8), Inches(0.06), C_CORAL, rounded=False)

    # Metric in Teal bar
    t_stat1 = s1.shapes.add_textbox(Inches(0.8), Inches(4.5), Inches(3.4), Inches(2.2))
    tf_s1 = t_stat1.text_frame
    tf_s1.word_wrap = True
    ps0 = tf_s1.paragraphs[0]
    ps0.text = "<50ms"
    ps0.font.size = Pt(48)
    ps0.font.bold = True
    ps0.font.color.rgb = C_WHITE
    ps0.space_after = Pt(4)

    ps1 = tf_s1.add_paragraph()
    ps1.text = "Deploy-to-attack reaction time upon git push, catching logic bugs before production release."
    ps1.font.size = Pt(11)
    ps1.font.color.rgb = C_ROW_BG

    # Right Content Area of Cover
    t_rc = s1.shapes.add_textbox(Inches(5.3), Inches(1.1), Inches(7.3), Inches(5.4))
    tf_rc = t_rc.text_frame
    tf_rc.word_wrap = True

    prc0 = tf_rc.paragraphs[0]
    prc0.text = "EXECUTIVE SUMMARY"
    prc0.font.size = Pt(12)
    prc0.font.bold = True
    prc0.font.color.rgb = C_SAGE_TEAL
    prc0.space_after = Pt(12)

    prc1 = tf_rc.add_paragraph()
    prc1.text = "B2B travel platforms like TBO deploy microservice updates multiple times a day. Conventional security testing is periodic and generic—blind to catastrophic business-logic vulnerabilities like $1 flight price tampering, cross-agency IDOR passport data leaks, duplicate refund exploits, and unmonitored zombie endpoints."
    prc1.font.size = Pt(13)
    prc1.font.color.rgb = C_TEXT_DARK
    prc1.space_after = Pt(18)

    prc2 = tf_rc.add_paragraph()
    prc2.text = "RouteZero is an agentic AppSec engine that sniffs live HTTP traffic to map schemas without swagger docs, auto-identifies shadow and deprecated routes, plans multi-step contextual business attacks, and generates verified curl reproduction proofs with exact code fixes."
    prc2.font.size = Pt(13)
    prc2.font.color.rgb = C_TEXT_MUTED
    prc2.space_after = Pt(28)

    # Links Box on Cover
    add_shape(s1, Inches(5.3), Inches(5.3), Inches(7.3), Inches(1.3), C_PEACH_BOX, rounded=True)
    t_c_links = s1.shapes.add_textbox(Inches(5.5), Inches(5.45), Inches(6.9), Inches(1.0))
    tc_tf = t_c_links.text_frame
    tc_p0 = tc_tf.paragraphs[0]
    tc_p0.text = "LIVE PLATFORM:  https://saisanthosh31.github.io/routezero/"
    tc_p0.font.size = Pt(11.5)
    tc_p0.font.bold = True
    tc_p0.font.color.rgb = C_CORAL
    tc_p0.space_after = Pt(6)

    tc_p1 = tc_tf.add_paragraph()
    tc_p1.text = "SOURCE REPO:     https://github.com/SaiSanthosh31/routezero"
    tc_p1.font.size = Pt(11.5)
    tc_p1.font.bold = True
    tc_p1.font.color.rgb = C_TEAL_DARK

    add_footer(s1)

    # ========================================================
    # SLIDE 2: EXACT IMAGE 2 TEMPLATE (Sidebar, Problem, Affected, Evidence, Pipeline)
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s2)

    # Left Dark Teal Sidebar (Full Bleed matching Image 2)
    add_shape(s2, Inches(0.0), Inches(0.0), Inches(4.5), Inches(7.5), C_TEAL_DARK, rounded=False)

    # Orange Tag at top: PROBLEM 2 (Spaced uppercase)
    t_p_tag = s2.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(3.4), Inches(0.4))
    ptag_p = t_p_tag.text_frame.paragraphs[0]
    ptag_p.text = "P R O B L E M   2"
    ptag_p.font.size = Pt(11)
    ptag_p.font.bold = True
    ptag_p.font.color.rgb = C_CORAL

    # Title in Teal bar (Large, crisp white, bold)
    t_p_title = s2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(3.4), Inches(2.2))
    tf_pt = t_p_title.text_frame
    tf_pt.word_wrap = True
    pt_title = tf_pt.paragraphs[0]
    pt_title.text = "Travel API Logic\n& Shadow Route\nVulnerabilities"
    pt_title.font.size = Pt(30)
    pt_title.font.bold = True
    pt_title.font.color.rgb = C_WHITE

    # Orange divider line
    add_shape(s2, Inches(0.8), Inches(4.1), Inches(0.8), Inches(0.06), C_CORAL, rounded=False)

    # Big Metric in Sidebar (Matching 5.8% style from Image 2)
    t_p_stat = s2.shapes.add_textbox(Inches(0.8), Inches(4.4), Inches(3.4), Inches(2.2))
    tf_ps = t_p_stat.text_frame
    tf_ps.word_wrap = True
    pps0 = tf_ps.paragraphs[0]
    pps0.text = "100%"
    pps0.font.size = Pt(50)
    pps0.font.bold = True
    pps0.font.color.rgb = C_WHITE
    pps0.space_after = Pt(4)

    pps1 = tf_ps.add_paragraph()
    pps1.text = "of business-logic exploits bypass conventional DAST scanners, remaining undetected until attackers strike."
    pps1.font.size = Pt(11)
    pps1.font.color.rgb = C_ROW_BG

    # ---------------- RIGHT CONTENT AREA ----------------
    # SECTION 1: THE PROBLEM
    t_prob_hdr = s2.shapes.add_textbox(Inches(5.2), Inches(0.6), Inches(7.5), Inches(0.3))
    pph = t_prob_hdr.text_frame.paragraphs[0]
    pph.text = "T H E   P R O B L E M"
    pph.font.size = Pt(10.5)
    pph.font.bold = True
    pph.font.color.rgb = C_SAGE_TEAL

    t_prob_txt = s2.shapes.add_textbox(Inches(5.2), Inches(0.9), Inches(7.5), Inches(0.95))
    pp_tf = t_prob_txt.text_frame
    pp_tf.word_wrap = True
    pp_p = pp_tf.paragraphs[0]
    pp_p.text = "B2B travel platforms change constantly. Existing security scans run periodically and spray generic SQLi/XSS payloads, missing business-logic flaws like $1 flight price overrides, cross-agency IDOR passport theft, duplicate refunds, and unmonitored zombie APIs."
    pp_p.font.size = Pt(10.5)
    pp_p.font.color.rgb = C_TEXT_DARK

    # SECTION 2: WHO IS AFFECTED
    t_who_hdr = s2.shapes.add_textbox(Inches(5.2), Inches(1.95), Inches(7.5), Inches(0.3))
    pwh = t_who_hdr.text_frame.paragraphs[0]
    pwh.text = "W H O   I S   A F F E C T E D"
    pwh.font.size = Pt(10.5)
    pwh.font.bold = True
    pwh.font.color.rgb = C_SAGE_TEAL

    # Row 1: DIRECT (Matching Image 2: Orange Badge + Light blue-gray container side-by-side)
    add_shape(s2, Inches(5.2), Inches(2.3), Inches(1.2), Inches(0.48), C_CORAL, rounded=True)
    t_tag_d = s2.shapes.add_textbox(Inches(5.2), Inches(2.32), Inches(1.2), Inches(0.44))
    t_tag_d.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    pt_d = t_tag_d.text_frame.paragraphs[0]
    pt_d.text = "DIRECT"
    pt_d.alignment = PP_ALIGN.CENTER
    pt_d.font.size = Pt(9.5)
    pt_d.font.bold = True
    pt_d.font.color.rgb = C_WHITE

    add_shape(s2, Inches(6.5), Inches(2.3), Inches(6.2), Inches(0.48), C_ROW_BG, rounded=True)
    t_desc_d = s2.shapes.add_textbox(Inches(6.6), Inches(2.32), Inches(6.0), Inches(0.44))
    t_desc_d.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_dd = t_desc_d.text_frame.paragraphs[0]
    p_dd.text = "Travel agencies & passengers (fraudulent bookings, stolen passport data & cancelled tickets)"
    p_dd.font.size = Pt(9.5)
    p_dd.font.color.rgb = C_TEXT_DARK

    # Row 2: INDIRECT
    add_shape(s2, Inches(5.2), Inches(2.88), Inches(1.2), Inches(0.48), C_SAGE_TEAL, rounded=True)
    t_tag_i = s2.shapes.add_textbox(Inches(5.2), Inches(2.9), Inches(1.2), Inches(0.44))
    t_tag_i.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    pt_i = t_tag_i.text_frame.paragraphs[0]
    pt_i.text = "INDIRECT"
    pt_i.alignment = PP_ALIGN.CENTER
    pt_i.font.size = Pt(9.5)
    pt_i.font.bold = True
    pt_i.font.color.rgb = C_WHITE

    add_shape(s2, Inches(6.5), Inches(2.88), Inches(6.2), Inches(0.48), C_ROW_BG, rounded=True)
    t_desc_i = s2.shapes.add_textbox(Inches(6.6), Inches(2.9), Inches(6.0), Inches(0.44))
    t_desc_i.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_di = t_desc_i.text_frame.paragraphs[0]
    p_di.text = "TBO operations & finance (margin loss, depleted refund pools, and manual ticket triage)"
    p_di.font.size = Pt(9.5)
    p_di.font.color.rgb = C_TEXT_DARK

    # Row 3: OTHERS
    add_shape(s2, Inches(5.2), Inches(3.46), Inches(1.2), Inches(0.48), C_TEAL_DARK, rounded=True)
    t_tag_o = s2.shapes.add_textbox(Inches(5.2), Inches(3.48), Inches(1.2), Inches(0.44))
    t_tag_o.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    pt_o = t_tag_o.text_frame.paragraphs[0]
    pt_o.text = "OTHERS"
    pt_o.alignment = PP_ALIGN.CENTER
    pt_o.font.size = Pt(9.5)
    pt_o.font.bold = True
    pt_o.font.color.rgb = C_WHITE

    add_shape(s2, Inches(6.5), Inches(3.46), Inches(6.2), Inches(0.48), C_ROW_BG, rounded=True)
    t_desc_o = s2.shapes.add_textbox(Inches(6.6), Inches(3.48), Inches(6.0), Inches(0.44))
    t_desc_o.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_do = t_desc_o.text_frame.paragraphs[0]
    p_do.text = "Platform engineers & compliance teams (India DPDP Act penalties & shadow API sprawl)"
    p_do.font.size = Pt(9.5)
    p_do.font.color.rgb = C_TEXT_DARK

    # SECTION 3: EVIDENCE
    t_ev_hdr = s2.shapes.add_textbox(Inches(5.2), Inches(4.08), Inches(7.5), Inches(0.3))
    pevh = t_ev_hdr.text_frame.paragraphs[0]
    pevh.text = "E V I D E N C E"
    pevh.font.size = Pt(10.5)
    pevh.font.bold = True
    pevh.font.color.rgb = C_SAGE_TEAL

    t_ev_txt = s2.shapes.add_textbox(Inches(5.2), Inches(4.35), Inches(7.5), Inches(0.75))
    pev_tf = t_ev_txt.text_frame
    pev_tf.word_wrap = True
    pevp = pev_tf.paragraphs[0]
    pevp.text = "Tested live on production-like travel staging: caught $1 flight fare tampering, cross-agency IDOR passport leak, deprecated 50% discount voucher leak, and internal DB telemetry disclosure. Found through: automated live multi-role API security simulation."
    pevp.font.size = Pt(10)
    pevp.font.color.rgb = C_TEXT_DARK

    # SECTION 4: NEED & PIPELINE (Peach Box with 3 connected white cards matching Image 2)
    add_shape(s2, Inches(5.2), Inches(5.25), Inches(7.5), Inches(1.65), C_PEACH_BOX, rounded=True)
    t_need_lbl = s2.shapes.add_textbox(Inches(5.4), Inches(5.33), Inches(7.1), Inches(0.3))
    pnd = t_need_lbl.text_frame.paragraphs[0]
    pnd.text = "NEED: An early-warning system for travel API business-logic and shadow risks"
    pnd.font.size = Pt(10.5)
    pnd.font.bold = True
    pnd.font.color.rgb = C_CORAL

    # Exactly 3 Horizontal Step Cards with Arrows (DETECT > ASSESS > ALERT style)
    pipeline_3steps = [
        ("DETECT", "temperature, humidity, body temp -> travel traffic, endpoints, shadow APIs"),
        ("ASSESS", "heat-stress risk -> business-logic exploit feasibility"),
        ("ALERT", "supervisors before severe -> dev teams with curl PoC & code fix")
    ]
    
    # Let's write clear, punchy 3 steps:
    pipeline_steps = [
        ("DISCOVER", "Observe live HTTP traffic & map shadow/zombie routes"),
        ("EXPLOIT", "Execute safe multi-step travel logic attacks"),
        ("REMEDIATE", "Deliver verified curl proof & patch code to devs")
    ]

    card_w = Inches(2.15)
    card_h = Inches(1.0)
    card_gap = Inches(0.35)
    start_x = Inches(5.45)
    card_y = Inches(5.72)

    for st_i, (step_t, step_sub) in enumerate(pipeline_steps):
        bx = start_x + st_i * (card_w + card_gap)
        add_shape(s2, bx, card_y, card_w, card_h, C_WHITE, rounded=True)
        
        stx = s2.shapes.add_textbox(bx + Inches(0.08), card_y + Inches(0.08), card_w - Inches(0.16), card_h - Inches(0.16))
        stf = stx.text_frame
        stf.word_wrap = True
        stp0 = stf.paragraphs[0]
        stp0.text = step_t
        stp0.alignment = PP_ALIGN.CENTER
        stp0.font.size = Pt(11)
        stp0.font.bold = True
        stp0.font.color.rgb = C_CORAL
        stp0.space_after = Pt(2)

        stp1 = stf.add_paragraph()
        stp1.text = step_sub
        stp1.alignment = PP_ALIGN.CENTER
        stp1.font.size = Pt(8.5)
        stp1.font.color.rgb = C_TEXT_MUTED

        if st_i < 2:
            # Sleek Right Arrow between cards
            arr = s2.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW, 
                bx + card_w + Inches(0.08), 
                card_y + Inches(0.4), 
                Inches(0.18), 
                Inches(0.2)
            )
            arr.fill.solid()
            arr.fill.fore_color.rgb = C_CORAL
            arr.line.fill.background()

    add_footer(s2)

    # ========================================================
    # SLIDE 3: EXACT IMAGE 1 TEMPLATE (5 Whys Root Cause Analysis)
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s3)

    # Left Edge Vertical Accent Strip (Exact Image 1: Teal line on far left with orange tab)
    add_shape(s3, Inches(0.0), Inches(0.0), Inches(0.25), Inches(7.5), C_TEAL_DARK, rounded=False)
    add_shape(s3, Inches(0.0), Inches(1.0), Inches(0.25), Inches(1.1), C_CORAL, rounded=False)

    # Title: 5 Whys (Exact Image 1)
    t_5w = s3.shapes.add_textbox(Inches(0.7), Inches(0.55), Inches(4.0), Inches(0.75))
    p_5w = t_5w.text_frame.paragraphs[0]
    p_5w.text = "5 Whys"
    p_5w.font.size = Pt(34)
    p_5w.font.bold = True
    p_5w.font.color.rgb = C_TEAL_DARK

    # Orange underline bar (Exact Image 1)
    add_shape(s3, Inches(0.7), Inches(1.4), Inches(0.85), Inches(0.06), C_CORAL, rounded=False)

    # Main Problem Dark Teal Card
    add_shape(s3, Inches(0.7), Inches(1.7), Inches(11.8), Inches(0.55), C_TEAL_DARK, rounded=True)
    t_mp = s3.shapes.add_textbox(Inches(0.9), Inches(1.75), Inches(11.4), Inches(0.45))
    t_mp.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    pmp = t_mp.text_frame.paragraphs[0]
    pmp.text = "Problem: TBO B2B travel APIs suffer undetected business-logic flaws and shadow route leaks"
    pmp.font.size = Pt(11)
    pmp.font.bold = True
    pmp.font.color.rgb = C_WHITE

    # 5 Whys Pairs (Exact Image 1: Teal on Left, Vector Arrow -> Soft Blue on Right)
    whys_data = [
        ("Why 1? Why do business-logic flaws go undetected?",
         "Because traditional DAST scanners only spray generic SQLi/XSS payloads and miss travel workflows."),
        ("Why 2? Why can't legacy scanners catch logic bugs?",
         "Because they do not understand application context like booking pricing, refunds, and multi-tenant agency roles."),
        ("Why 3? Why are APIs not tested against business context?",
         "Because manual pentesting takes weeks while TBO microservices deploy updates multiple times a day."),
        ("Why 4? Why do zombie and shadow APIs remain exposed?",
         "Because deprecated /v1 routes and debug endpoints remain live in production without traffic tracking."),
        ("Why 5? Why is continuous protection missing?",
         "Because no autonomous agent observes traffic, infers schemas, and executes targeted business exploits.")
    ]

    for w_i, (left_q, right_a) in enumerate(whys_data):
        y_pos = Inches(2.45 + w_i * 0.72)
        
        # Left Teal Box
        add_shape(s3, Inches(0.7), y_pos, Inches(4.3), Inches(0.56), C_TEAL_DARK, rounded=True)
        tx_l = s3.shapes.add_textbox(Inches(0.8), y_pos + Inches(0.05), Inches(4.1), Inches(0.46))
        tx_l.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        tx_l.text_frame.word_wrap = True
        pl = tx_l.text_frame.paragraphs[0]
        pl.text = left_q
        pl.font.size = Pt(10)
        pl.font.bold = True
        pl.font.color.rgb = C_WHITE

        # Vector Arrow connector (Exact clean look like Image 1)
        arr_5w = s3.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW, 
            Inches(5.08), 
            y_pos + Inches(0.2), 
            Inches(0.24), 
            Inches(0.16)
        )
        arr_5w.fill.solid()
        arr_5w.fill.fore_color.rgb = C_SAGE_TEAL
        arr_5w.line.fill.background()

        # Right Soft Blue Box
        add_shape(s3, Inches(5.4), y_pos, Inches(7.1), Inches(0.56), C_ROW_BG, rounded=True)
        tx_r = s3.shapes.add_textbox(Inches(5.55), y_pos + Inches(0.05), Inches(6.8), Inches(0.46))
        tx_r.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        tx_r.text_frame.word_wrap = True
        pr = tx_r.text_frame.paragraphs[0]
        pr.text = right_a
        pr.font.size = Pt(10)
        pr.font.color.rgb = C_TEXT_DARK

    # Bottom Orange Highlight Box: ROOT CAUSE (Exact Image 1)
    add_shape(s3, Inches(0.7), Inches(6.2), Inches(11.8), Inches(0.65), C_CORAL, rounded=True)
    t_rc_box = s3.shapes.add_textbox(Inches(0.9), Inches(6.25), Inches(11.4), Inches(0.55))
    t_rc_box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    prc = t_rc_box.text_frame.paragraphs[0]
    prc.text = "Root cause: The missing link between real-time traffic discovery and autonomous logic exploit testing"
    prc.font.size = Pt(11.5)
    prc.font.bold = True
    prc.font.color.rgb = C_WHITE

    add_footer(s3)

    # ========================================================
    # SLIDE 4: THANK YOU SLIDE (Full-bleed Left Sidebar)
    # ========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s4)

    # Full Bleed Left Dark Teal Column
    add_shape(s4, Inches(0.0), Inches(0.0), Inches(4.5), Inches(7.5), C_TEAL_DARK, rounded=False)

    t_ty_tag = s4.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(3.4), Inches(0.4))
    pty0 = t_ty_tag.text_frame.paragraphs[0]
    pty0.text = "ROUTEZERO // TBO VOYAGEHACK 4.0"
    pty0.font.size = Pt(11)
    pty0.font.bold = True
    pty0.font.color.rgb = C_CORAL

    t_ty_title = s4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(3.4), Inches(2.2))
    tf_ty = t_ty_title.text_frame
    tf_ty.word_wrap = True
    pty1 = tf_ty.paragraphs[0]
    pty1.text = "Thank You."
    pty1.font.size = Pt(46)
    pty1.font.bold = True
    pty1.font.color.rgb = C_WHITE

    add_shape(s4, Inches(0.8), Inches(4.1), Inches(0.8), Inches(0.06), C_CORAL, rounded=False)

    t_ty_desc = s4.shapes.add_textbox(Inches(0.8), Inches(4.4), Inches(3.4), Inches(2.2))
    tf_td = t_ty_desc.text_frame
    tf_td.word_wrap = True
    ptyd0 = tf_td.paragraphs[0]
    ptyd0.text = "RouteZero is ready for evaluation."
    ptyd0.font.size = Pt(14)
    ptyd0.font.bold = True
    ptyd0.font.color.rgb = C_WHITE
    ptyd0.space_after = Pt(4)

    ptyd1 = tf_td.add_paragraph()
    ptyd1.text = "Full working prototype, live interactive dashboard, reproducible curl proofs, and automated OpenAPI spec generator."
    ptyd1.font.size = Pt(10.5)
    ptyd1.font.color.rgb = C_ROW_BG

    # Right Content Area: Team Members & Links
    t_tm_hdr = s4.shapes.add_textbox(Inches(5.2), Inches(0.7), Inches(7.5), Inches(0.35))
    ptmh = t_tm_hdr.text_frame.paragraphs[0]
    ptmh.text = "TEAM MEMBERS & CONTRIBUTIONS"
    ptmh.font.size = Pt(11.5)
    ptmh.font.bold = True
    ptmh.font.color.rgb = C_SAGE_TEAL

    team = [
        ("Sai Santhosh", "Lead Backend & AI Engine", "Built LLM attack planner, safe exploit executor, verifier proof engine & core APIs."),
        ("Dharani", "Backend & Recon Engine", "Built traffic sniffer, HAR parser, zombie & shadow API detector, and SQLite models."),
        ("Arun Hitesh", "Frontend Command Center", "Built security operations dashboard, live activity stream, and emergency kill switch."),
        ("Mythreyan", "Frontend API Topology & PoC", "Built visual endpoint topology graph, vulnerability inspector, and retest trigger."),
        ("Ravi Kiran", "Test Data & Traffic Simulation", "Built synthetic flight booking datasets, HAR traffic interaction flows & demo fixtures.")
    ]

    for m_i, (name, role, contrib) in enumerate(team):
        card_y = Inches(1.08 + m_i * 0.95)
        # Left Tag Pill
        add_shape(s4, Inches(5.2), card_y, Inches(1.85), Inches(0.85), C_TEAL_DARK, rounded=True)
        tx_name = s4.shapes.add_textbox(Inches(5.25), card_y + Inches(0.08), Inches(1.75), Inches(0.7))
        tx_name.text_frame.word_wrap = True
        pn0 = tx_name.text_frame.paragraphs[0]
        pn0.text = name
        pn0.font.size = Pt(10.5)
        pn0.font.bold = True
        pn0.font.color.rgb = C_WHITE
        pn1 = tx_name.text_frame.add_paragraph()
        pn1.text = role
        pn1.font.size = Pt(8.0)
        pn1.font.color.rgb = C_CORAL

        # Right Content Container
        add_shape(s4, Inches(7.15), card_y, Inches(5.55), Inches(0.85), C_ROW_BG, rounded=True)
        tx_cont = s4.shapes.add_textbox(Inches(7.25), card_y + Inches(0.08), Inches(5.35), Inches(0.7))
        tx_cont.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        tx_cont.text_frame.word_wrap = True
        pc0 = tx_cont.text_frame.paragraphs[0]
        pc0.text = contrib
        pc0.font.size = Pt(9.5)
        pc0.font.color.rgb = C_TEXT_DARK

    # Bottom Links Box
    add_shape(s4, Inches(5.2), Inches(5.95), Inches(7.5), Inches(0.85), C_PEACH_BOX, rounded=True)
    t_sub_links = s4.shapes.add_textbox(Inches(5.4), Inches(6.05), Inches(7.1), Inches(0.65))
    tl_tf = t_sub_links.text_frame
    tl_p0 = tl_tf.paragraphs[0]
    tl_p0.text = "LIVE PLATFORM:  https://saisanthosh31.github.io/routezero/"
    tl_p0.font.size = Pt(10.5)
    tl_p0.font.bold = True
    tl_p0.font.color.rgb = C_CORAL

    tl_p1 = tl_tf.add_paragraph()
    tl_p1.text = "SOURCE CODE:    https://github.com/SaiSanthosh31/routezero"
    tl_p1.font.size = Pt(10.5)
    tl_p1.font.bold = True
    tl_p1.font.color.rgb = C_TEAL_DARK

    add_footer(s4)

    prs.save("RouteZero_VoyageHack_Submission.pptx")
    print("Exact screenshot matching presentation generated successfully!")

if __name__ == "__main__":
    build_exact_template_deck()
