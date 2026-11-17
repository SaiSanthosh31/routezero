import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_template_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 Widescreen
    blank_layout = prs.slide_layouts[6]

    # Exact Palette from Iterate_DT_Stage0_Stage1_new.pptx:
    COLOR_TEAL_DARK = RGBColor(18, 52, 59)      # #12343B Deep Slate/Teal
    COLOR_CORAL     = RGBColor(240, 138, 75)   # #F08A4B Warm Coral/Orange
    COLOR_SAGE_TEAL = RGBColor(42, 157, 143)   # #2A9D8F Sage Teal
    COLOR_BG_LIGHT  = RGBColor(248, 250, 251)  # #F8FAFB Crisp Clean Canvas
    COLOR_PILL_GRAY = RGBColor(238, 243, 244)  # #EEF3F4 Soft Card Surface
    COLOR_PILL_PEACH= RGBColor(253, 235, 221)  # #FDEBDD Warm Accent Surface
    COLOR_WHITE     = RGBColor(255, 255, 255)
    COLOR_TEXT_DARK = RGBColor(20, 30, 35)
    COLOR_TEXT_MUTED= RGBColor(90, 105, 115)

    def draw_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG_LIGHT
        bg.line.fill.background()

    def add_rect(slide, x, y, w, h, fill_rgb, border_rgb=None, line_w=1, rounded=True):
        shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
        s = slide.shapes.add_shape(shape_type, x, y, w, h)
        s.fill.solid()
        s.fill.fore_color.rgb = fill_rgb
        if border_rgb:
            s.line.color.rgb = border_rgb
            s.line.width = Pt(line_w)
        else:
            s.line.fill.background()
        return s

    # ========================================================
    # SLIDE 1: COVER SLIDE (Exact Iterate_DT Style)
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    draw_bg(s1)

    # Top Teal Bar Header Card
    add_rect(s1, Inches(1.0), Inches(1.5), Inches(11.333), Inches(4.5), COLOR_WHITE, border_rgb=COLOR_PILL_GRAY, rounded=True)
    add_rect(s1, Inches(1.0), Inches(1.5), Inches(11.333), Inches(1.1), COLOR_TEAL_DARK, rounded=False)

    # Header text
    t_hdr = s1.shapes.add_textbox(Inches(1.3), Inches(1.65), Inches(10.7), Inches(0.8))
    tf_h = t_hdr.text_frame
    p_h0 = tf_h.paragraphs[0]
    p_h0.text = "VOYAGEHACK 4.0  *  TRACK 4: AGENTIC REAL-TIME DAST"
    p_h0.font.size = Pt(13)
    p_h0.font.bold = True
    p_h0.font.color.rgb = COLOR_CORAL
    p_h0.space_after = Pt(2)

    p_h1 = tf_h.add_paragraph()
    p_h1.text = "TBO.COM INNOVATION CHALLENGE"
    p_h1.font.size = Pt(18)
    p_h1.font.bold = True
    p_h1.font.color.rgb = COLOR_WHITE

    # Main Body on Cover
    t_body = s1.shapes.add_textbox(Inches(1.4), Inches(2.85), Inches(10.5), Inches(2.9))
    tf_b = t_body.text_frame
    tf_b.word_wrap = True

    pb0 = tf_b.paragraphs[0]
    pb0.text = "RouteZero"
    pb0.font.size = Pt(46)
    pb0.font.bold = True
    pb0.font.color.rgb = COLOR_TEAL_DARK
    pb0.space_after = Pt(6)

    pb1 = tf_b.add_paragraph()
    pb1.text = "Autonomous Real-Time Application Security Agent for B2B Travel APIs"
    pb1.font.size = Pt(18)
    pb1.font.bold = True
    pb1.font.color.rgb = COLOR_CORAL
    pb1.space_after = Pt(14)

    pb2 = tf_b.add_paragraph()
    pb2.text = "Chosen Problem: Hunting zero-day business-logic flaws, unmapped shadow APIs, and deprecated zombie routes across high-frequency B2B travel deployments."
    pb2.font.size = Pt(13)
    pb2.font.color.rgb = COLOR_TEXT_MUTED
    pb2.space_after = Pt(18)

    pb3 = tf_b.add_paragraph()
    pb3.text = "Team: RouteZero  |  Live Demo: saisanthosh31.github.io/routezero  |  GitHub: github.com/SaiSanthosh31/routezero"
    pb3.font.size = Pt(11.5)
    pb3.font.bold = True
    pb3.font.color.rgb = COLOR_TEAL_DARK

    # ========================================================
    # SLIDE 2: THE PROBLEM & PROPOSED SOLUTION (Exact Slide 3 of Template)
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    draw_bg(s2)

    # Top Title Bar in Deep Teal
    add_rect(s2, Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.75), COLOR_TEAL_DARK, rounded=True)
    t_s2_hdr = s2.shapes.add_textbox(Inches(1.0), Inches(0.45), Inches(10.0), Inches(0.6))
    p_s2_h = t_s2_hdr.text_frame.paragraphs[0]
    p_s2_h.text = "Autonomous Real-Time DAST for B2B Travel Platforms"
    p_s2_h.font.size = Pt(18)
    p_s2_h.font.bold = True
    p_s2_h.font.color.rgb = COLOR_WHITE

    # Big Coral Stat Box (Top Right)
    add_rect(s2, Inches(9.2), Inches(1.3), Inches(3.333), Inches(1.4), COLOR_CORAL, rounded=True)
    t_stat = s2.shapes.add_textbox(Inches(9.3), Inches(1.35), Inches(3.1), Inches(1.3))
    t_stf = t_stat.text_frame
    t_stf.word_wrap = True
    p_st0 = t_stf.paragraphs[0]
    p_st0.text = "<50ms"
    p_st0.font.size = Pt(32)
    p_st0.font.bold = True
    p_st0.font.color.rgb = COLOR_WHITE
    p_st1 = t_stf.add_paragraph()
    p_st1.text = "Deploy-to-attack reaction time vs 7+ days for traditional scans"
    p_st1.font.size = Pt(10.5)
    p_st1.font.color.rgb = COLOR_WHITE

    # Left Column: THE PROBLEM
    add_rect(s2, Inches(0.8), Inches(1.3), Inches(8.2), Inches(1.4), COLOR_WHITE, border_rgb=COLOR_PILL_GRAY, rounded=True)
    t_prob = s2.shapes.add_textbox(Inches(1.0), Inches(1.35), Inches(7.8), Inches(1.3))
    tptf = t_prob.text_frame
    tptf.word_wrap = True
    pt0 = tptf.paragraphs[0]
    pt0.text = "THE PROBLEM"
    pt0.font.size = Pt(12)
    pt0.font.bold = True
    pt0.font.color.rgb = COLOR_CORAL
    pt0.space_after = Pt(2)
    pt1 = tptf.add_paragraph()
    pt1.text = "TBO updates booking and inventory APIs daily. Conventional security scanners run on weekly schedules and spray generic payloads, missing critical business-logic abuse: $1 flight fare tampering, cross-agency IDOR passport leaks, and unmonitored zombie/shadow APIs."
    pt1.font.size = Pt(11)
    pt1.font.color.rgb = COLOR_TEXT_DARK

    # Middle Section: WHO IS AFFECTED (3 Rounded Cards: Direct, Indirect, Others)
    t_who_lbl = s2.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.733), Inches(0.35))
    p_who = t_who_lbl.text_frame.paragraphs[0]
    p_who.text = "WHO IS AFFECTED"
    p_who.font.size = Pt(12)
    p_who.font.bold = True
    p_who.font.color.rgb = COLOR_TEAL_DARK

    affected_groups = [
        ("DIRECT", COLOR_CORAL, "Travel Agencies & End Travelers", "Suffer financial loss from fraudulent bookings, leaked passenger passport PII, and unauthorized fare cancellations."),
        ("INDIRECT", COLOR_SAGE_TEAL, "TBO Operations & Finance", "Face revenue leakage, margin theft via coupon replay, manual ticket triage fatigue, and supplier escrow depletion."),
        ("OTHERS", COLOR_TEAL_DARK, "Compliance & Platform Infrastructure", "Risk severe penalties under India's DPDP Act 2023 for cross-agency data exposure and unmapped API sprawl.")
    ]

    for idx, (label, color_bar, title, desc) in enumerate(affected_groups):
        card_x = Inches(0.8 + idx * 3.95)
        add_rect(s2, card_x, Inches(3.2), Inches(3.8), Inches(1.4), COLOR_PILL_GRAY, rounded=True)
        add_rect(s2, card_x, Inches(3.2), Inches(3.8), Inches(0.3), color_bar, rounded=True)
        
        # Label in top strip
        tx_tag = s2.shapes.add_textbox(card_x + Inches(0.15), Inches(3.2), Inches(3.5), Inches(0.28))
        ptag = tx_tag.text_frame.paragraphs[0]
        ptag.text = label
        ptag.font.size = Pt(9.5)
        ptag.font.bold = True
        ptag.font.color.rgb = COLOR_WHITE

        # Card text
        tx_c = s2.shapes.add_textbox(card_x + Inches(0.15), Inches(3.55), Inches(3.5), Inches(1.0))
        ctf = tx_c.text_frame
        ctf.word_wrap = True
        cp0 = ctf.paragraphs[0]
        cp0.text = title
        cp0.font.size = Pt(11)
        cp0.font.bold = True
        cp0.font.color.rgb = COLOR_TEXT_DARK
        cp1 = ctf.add_paragraph()
        cp1.text = desc
        cp1.font.size = Pt(9.5)
        cp1.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Section: IDEA IN MIND (Workflow Pipeline)
    add_rect(s2, Inches(0.8), Inches(4.8), Inches(11.733), Inches(2.2), COLOR_PILL_PEACH, rounded=True)
    t_idea_lbl = s2.shapes.add_textbox(Inches(1.0), Inches(4.85), Inches(11.3), Inches(0.35))
    p_idea = t_idea_lbl.text_frame.paragraphs[0]
    p_idea.text = "IDEA IN MIND: ROUTEZERO 5-STAGE AUTONOMOUS PIPELINE"
    p_idea.font.size = Pt(11.5)
    p_idea.font.bold = True
    p_idea.font.color.rgb = COLOR_CORAL

    stages = [
        ("DETECT", "Parses live traffic & HAR logs to infer routes & schemas."),
        ("MAP", "Categorizes Active, Zombie (/v1), and Shadow APIs."),
        ("PLAN", "LLM designs targeted travel business-logic exploits."),
        ("EXPLOIT", "Safely executes attacks with allowlisting & rate limits."),
        ("VERIFY", "Delivers 1-click curl proofs & developer code fixes.")
    ]

    for s_idx, (st_name, st_desc) in enumerate(stages):
        box_x = Inches(1.0 + s_idx * 2.3)
        add_rect(s2, box_x, Inches(5.25), Inches(2.1), Inches(1.5), COLOR_WHITE, border_rgb=COLOR_CORAL, rounded=True)
        
        stx = s2.shapes.add_textbox(box_x + Inches(0.1), Inches(5.35), Inches(1.9), Inches(1.3))
        stf = stx.text_frame
        stf.word_wrap = True
        
        sp0 = stf.paragraphs[0]
        sp0.text = st_name
        sp0.font.size = Pt(12)
        sp0.font.bold = True
        sp0.font.color.rgb = COLOR_TEAL_DARK
        sp0.space_after = Pt(4)

        sp1 = stf.add_paragraph()
        sp1.text = st_desc
        sp1.font.size = Pt(9.5)
        sp1.font.color.rgb = COLOR_TEXT_MUTED

        if s_idx < 4:
            arr = s2.shapes.add_textbox(box_x + Inches(2.05), Inches(5.7), Inches(0.3), Inches(0.4))
            ap = arr.text_frame.paragraphs[0]
            ap.text = ">"
            ap.font.size = Pt(14)
            ap.font.bold = True
            ap.font.color.rgb = COLOR_CORAL

    # ========================================================
    # SLIDE 3: VALIDATED RESULTS & ENTERPRISE ROI (Content 2)
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    draw_bg(s3)

    # Top Teal Bar Header Card
    add_rect(s3, Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.75), COLOR_TEAL_DARK, rounded=True)
    t_s3_hdr = s3.shapes.add_textbox(Inches(1.0), Inches(0.45), Inches(10.0), Inches(0.6))
    p_s3_h = t_s3_hdr.text_frame.paragraphs[0]
    p_s3_h.text = "Validated Results, Target Exploits & Value for TBO.com"
    p_s3_h.font.size = Pt(18)
    p_s3_h.font.bold = True
    p_s3_h.font.color.rgb = COLOR_WHITE

    # Big Teal Stat Box (Top Right)
    add_rect(s3, Inches(9.2), Inches(1.3), Inches(3.333), Inches(1.4), COLOR_SAGE_TEAL, rounded=True)
    t_stat3 = s3.shapes.add_textbox(Inches(9.3), Inches(1.35), Inches(3.1), Inches(1.3))
    t_stf3 = t_stat3.text_frame
    t_stf3.word_wrap = True
    p_st3_0 = t_stf3.paragraphs[0]
    p_st3_0.text = "0% False Positives"
    p_st3_0.font.size = Pt(24)
    p_st3_0.font.bold = True
    p_st3_0.font.color.rgb = COLOR_WHITE
    p_st3_1 = t_stf3.add_paragraph()
    p_st3_1.text = "Every finding backed by raw HTTP reproduction curl proof"
    p_st3_1.font.size = Pt(10.5)
    p_st3_1.font.color.rgb = COLOR_WHITE

    # Top Left Summary Box
    add_rect(s3, Inches(0.8), Inches(1.3), Inches(8.2), Inches(1.4), COLOR_WHITE, border_rgb=COLOR_PILL_GRAY, rounded=True)
    t_sum3 = s3.shapes.add_textbox(Inches(1.0), Inches(1.35), Inches(7.8), Inches(1.3))
    tsf3 = t_sum3.text_frame
    tsf3.word_wrap = True
    ps3_0 = tsf3.paragraphs[0]
    ps3_0.text = "VALIDATION ON LIVE TARGET"
    ps3_0.font.size = Pt(12)
    ps3_0.font.bold = True
    ps3_0.font.color.rgb = COLOR_CORAL
    ps3_0.space_after = Pt(2)
    ps3_1 = tsf3.add_paragraph()
    ps3_1.text = "RouteZero was evaluated against a live, production-like mock B2B travel portal with seeded vulnerabilities. It successfully discovered 6 API endpoints and proved 5 high-severity vulnerabilities without any OpenAPI specification provided."
    ps3_1.font.size = Pt(11)
    ps3_1.font.color.rgb = COLOR_TEXT_DARK

    # Middle Row: 5 Confirmed Vulnerabilities (White Cards)
    t_vuln_lbl = s3.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.733), Inches(0.35))
    p_vlbl = t_vuln_lbl.text_frame.paragraphs[0]
    p_vlbl.text = "5 PROVEN EXPLOITS ON LIVE TARGET PLATFORM"
    p_vlbl.font.size = Pt(12)
    p_vlbl.font.bold = True
    p_vlbl.font.color.rgb = COLOR_TEAL_DARK

    exploits_data = [
        ("Price Tampering (CRITICAL)", "Overrode $450 flight fare to $1.00 via client parameter tampering in /api/v2/bookings/create."),
        ("Tenant IDOR & PII Leak (CRITICAL)", "Agency-002 accessed Agency-001 booking records & exfiltrated passenger passport data."),
        ("Zombie Promo Code Leak (HIGH)", "Unauthenticated deprecated /v1/ legacy route leaked valid 50% internal staff discount code."),
        ("Shadow Telemetry Leak (HIGH)", "Publicly accessible /internal/ endpoint exposed database connection strings and environment info."),
        ("Double Refund State Flaw (HIGH)", "Executed infinite refund payouts without booking cancellation state verification.")
    ]

    for v_idx, (v_name, v_detail) in enumerate(exploits_data):
        vx = Inches(0.8 + v_idx * 2.37)
        add_rect(s3, vx, Inches(3.2), Inches(2.25), Inches(1.8), COLOR_PILL_GRAY, rounded=True)
        add_rect(s3, vx, Inches(3.2), Inches(2.25), Inches(0.28), COLOR_TEAL_DARK, rounded=True)

        v_tx = s3.shapes.add_textbox(vx + Inches(0.1), Inches(3.52), Inches(2.05), Inches(1.4))
        v_tf = v_tx.text_frame
        v_tf.word_wrap = True
        vp0 = v_tf.paragraphs[0]
        vp0.text = v_name
        vp0.font.size = Pt(10)
        vp0.font.bold = True
        vp0.font.color.rgb = COLOR_CORAL
        vp0.space_after = Pt(3)
        vp1 = v_tf.add_paragraph()
        vp1.text = v_detail
        vp1.font.size = Pt(9)
        vp1.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Section: TBO ENTERPRISE VALUE (Peach Box)
    add_rect(s3, Inches(0.8), Inches(5.15), Inches(11.733), Inches(1.9), COLOR_PILL_PEACH, rounded=True)
    t_roi_lbl = s3.shapes.add_textbox(Inches(1.0), Inches(5.2), Inches(11.3), Inches(0.35))
    p_roi_h = t_roi_lbl.text_frame.paragraphs[0]
    p_roi_h.text = "STRATEGIC ROI & COMPLIANCE IMPACT FOR TBO.COM"
    p_roi_h.font.size = Pt(11.5)
    p_roi_h.font.bold = True
    p_roi_h.font.color.rgb = COLOR_CORAL

    rois = [
        ("Revenue Shield", "Stops direct financial loss from client fare manipulation, coupon replay, and supplier escrow refund pool draining."),
        ("DPDP Act Compliance", "Enforces strict cross-agency tenant boundaries, preventing massive statutory fines for passenger passport leaks."),
        ("Sub-Minute MTTR", "Developers receive verified curl reproduction commands and ready-to-merge code fixes in seconds."),
        ("Automated Governance", "Auto-generates and maintains a live OpenAPI 3.0 catalog as a by-product, ending unmapped API sprawl.")
    ]

    for r_idx, (r_title, r_desc) in enumerate(rois):
        rx = Inches(1.0 + r_idx * 2.85)
        add_rect(s3, rx, Inches(5.6), Inches(2.7), Inches(1.3), COLOR_WHITE, border_rgb=COLOR_CORAL, rounded=True)
        rtx = s3.shapes.add_textbox(rx + Inches(0.12), Inches(5.68), Inches(2.45), Inches(1.15))
        rtf = rtx.text_frame
        rtf.word_wrap = True
        rp0 = rtf.paragraphs[0]
        rp0.text = r_title
        rp0.font.size = Pt(11)
        rp0.font.bold = True
        rp0.font.color.rgb = COLOR_TEAL_DARK
        rp0.space_after = Pt(2)
        rp1 = rtf.add_paragraph()
        rp1.text = r_desc
        rp1.font.size = Pt(9)
        rp1.font.color.rgb = COLOR_TEXT_MUTED

    # ========================================================
    # SLIDE 4: TEAM & THANK YOU SLIDE (Exact Slide 18 of Template)
    # ========================================================
    s4 = prs.slides.add_slide(blank_layout)
    draw_bg(s4)

    add_rect(s4, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), COLOR_WHITE, border_rgb=COLOR_PILL_GRAY, rounded=True)
    add_rect(s4, Inches(1.0), Inches(1.2), Inches(11.333), Inches(1.1), COLOR_TEAL_DARK, rounded=False)

    t_s4_hdr = s4.shapes.add_textbox(Inches(1.3), Inches(1.35), Inches(10.7), Inches(0.8))
    tf4 = t_s4_hdr.text_frame
    p_t4_0 = tf4.paragraphs[0]
    p_t4_0.text = "TEAM: ROUTEZERO  *  VOYAGEHACK 4.0"
    p_t4_0.font.size = Pt(13)
    p_t4_0.font.bold = True
    p_t4_0.font.color.rgb = COLOR_CORAL
    p_t4_0.space_after = Pt(2)
    p_t4_1 = tf4.add_paragraph()
    p_t4_1.text = "Thank You"
    p_t4_1.font.size = Pt(22)
    p_t4_1.font.bold = True
    p_t4_1.font.color.rgb = COLOR_WHITE

    # 4 Team Members & Roles (Matching Template Slide 18 Layout)
    team_members = [
        ("Sai Santhosh", "Lead Backend & AI Agent Engine", "Built the LLM attack planner, safe exploit executor, verifier proofs, and core APIs."),
        ("Dharani", "Backend & Recon Engine", "Built traffic parser, zombie & shadow API classifier, and database persistence."),
        ("Arun Hitesh", "Frontend Command Center", "Built security operations dashboard, live activity stream, and emergency kill switch."),
        ("Mythreyan", "Frontend API Topology & PoC", "Built visual endpoint topology, vulnerability modal inspector, and retest trigger.")
    ]

    for m_idx, (name, role, contrib) in enumerate(team_members):
        mx = Inches(1.3 + m_idx * 2.7)
        add_rect(s4, mx, Inches(2.6), Inches(2.55), Inches(2.4), COLOR_PILL_GRAY, rounded=True)
        mtx = s4.shapes.add_textbox(mx + Inches(0.12), Inches(2.7), Inches(2.3), Inches(2.2))
        mtf = mtx.text_frame
        mtf.word_wrap = True
        
        mp0 = mtf.paragraphs[0]
        mp0.text = f"Name: {name}"
        mp0.font.size = Pt(12)
        mp0.font.bold = True
        mp0.font.color.rgb = COLOR_TEAL_DARK
        mp0.space_after = Pt(2)

        mp1 = mtf.add_paragraph()
        mp1.text = f"Role: {role}"
        mp1.font.size = Pt(10)
        mp1.font.bold = True
        mp1.font.color.rgb = COLOR_CORAL
        mp1.space_after = Pt(4)

        mp2 = mtf.add_paragraph()
        mp2.text = f"Contribution: {contrib}"
        mp2.font.size = Pt(9)
        mp2.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Links
    add_rect(s4, Inches(1.3), Inches(5.2), Inches(10.7), Inches(0.8), COLOR_PILL_PEACH, rounded=True)
    t_links = s4.shapes.add_textbox(Inches(1.5), Inches(5.3), Inches(10.3), Inches(0.6))
    tl_tf = t_links.text_frame
    tl_p0 = tl_tf.paragraphs[0]
    tl_p0.text = "Live Interactive Platform: https://saisanthosh31.github.io/routezero/   |   Source Code: https://github.com/SaiSanthosh31/routezero"
    tl_p0.font.size = Pt(12)
    tl_p0.font.bold = True
    tl_p0.font.color.rgb = COLOR_TEAL_DARK

    prs.save("RouteZero_VoyageHack_Submission.pptx")
    print("Exact template presentation generated successfully!")

if __name__ == "__main__":
    build_template_deck()
