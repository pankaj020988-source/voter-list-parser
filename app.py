import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import urllib.request
import re

st.set_page_config(page_title="Balaji Cyber Point - Final Voter System", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (A5 Portrait - Perfect Layout)")

# १. पॅनेल बॅनर आणि सेटिंग्ज
st.sidebar.header("⚙️ पॅनेल कॉन्फिगरेशन")
uploaded_banner = st.sidebar.file_uploader("१. पॅनेलचा बॅनर इमेज अपलोड करा", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("२. मतदान केंद्राचे नाव", "ज. प. प्रा. शाळा")

# २. एक्सेल फाईल अपलोड
st.subheader("📊 मतदार एक्सेल फाईल अपलोड करा")
uploaded_file = st.file_uploader("तुमची एक्सेल फाईल (.xlsx) इथे अपलोड करा", type=["xlsx"])

# मराठी अक्षरे आणि जोडाक्षरे एकदम शुद्ध दाखवण्यासाठी गुगलचा 'Noto Serif Devanagari' फॉन्ट ऑनलाईन रजिस्टर करणे
@st.cache_resource
def register_marathi_font():
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
        font_data = urllib.request.urlopen(font_url).read()
        font_io = io.BytesIO(font_data)
        pdfmetrics.registerFont(TTFont('MarathiFont', font_io))
        return 'MarathiFont'
    except Exception as e:
        return 'Helvetica'

font_name = register_marathi_font()

# जेंडर मधील चुका शुद्ध मराठीत सुधारणारे फंक्शन
def clean_gender_and_text(text):
    text = str(text).strip()
    if re.search(r'(सतरी|त्री|जी|श्रीमती|स्त्री|सत्री|^str|^st|^q|^g)', text, re.IGNORECASE):
        return "स्त्री"
    elif re.search(r'(पु|पु.|पुरुष|^pur|^pu|^t)', text, re.IGNORECASE):
        return "पु"
    return text

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("✅ एक्सेल फाईल यशस्वीरित्या लोड झाली!")
    
    # ३. सुटसुटीत आणि अचूक पीडीएफ जनरेशन लॉजिक
    def generate_perfect_slips(data_frame, banner_bytes, polling_station):
        buffer = io.BytesIO()
        # A5 Portrait चे डायमेन्शन्स निश्चित करणे (Margins सेट केल्या आहेत)
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A5, 
            rightMargin=15, 
            leftMargin=15, 
            topMargin=15, 
            bottomMargin=15
        )
        story = []
        
        styles = getSampleStyleSheet()
        
        # फॉन्ट योग्य दिसण्यासाठी पॅराग्राफ स्टाईल (जोडाक्षरे फाटणार नाहीत)
        marathi_style = ParagraphStyle(
            'PerfectMarathi',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=15,
            leading=24,
            textColor=colors.black
        )
        
        cut_style = ParagraphStyle(
            'PerfectCut',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=14,
            alignment=1, # Center
            textColor=colors.dimgrey
        )
        
        for index, row in data_frame.iterrows():
            slip_elements = []
            
            # १. पॅनेल बॅनर - सर्वात वरती
            if banner_bytes:
                try:
                    banner_img = Image(io.BytesIO(banner_bytes), width=370, height=85)
                    slip_elements.append(banner_img)
                except:
                    slip_elements.append(Paragraph("<font size='14' color='red'><b>[ बॅनर इमेज फॉरमॅट एरर ]</b></font>", cut_style))
            else:
                slip_elements.append(Paragraph("<font size='16'><b>[ इथे तुमचा पॅनेल बॅनर दिसेल ]</b></font>", cut_style))
            
            # २. तुमच्या डिझाईननुसार बॅनर आणि रेषेच्या मध्ये मोठी मोकळी जागा (Big Space)
            slip_elements.append(Spacer(1, 240)) 
            
            # ३. कापावे रेष आणि मजकूर
            slip_elements.append(Paragraph("----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------", cut_style))
            slip_content_spacer = Spacer(1, 10)
            slip_elements.append(slip_content_spacer)
            
            # डेटा मॅपिंग
            voter_no = row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिาंका', 'प्रियांका').replace('आदत्यि', 'आद्या').replace('मुजाहदि', 'मुजाहिद').replace('मनषिा', 'मनिषा').replace('वलिलास', 'विलास').replace('सारकिा', 'सारिका').replace('सुरेद्र', 'सुरेंद्र').replace('मंजरीि', 'मंजिरी').replace('भाटयिा', 'भाटिया').replace('गंगासगि', 'गंगासिंग').replace('सुरेद्रसगि', 'सुरेंद्रसिंग').replace('मांजशिी', 'मांजिरी').replace('गुरवदिर', 'गुरविंदर').replace('जतिंद्र', 'जितेन्द्र').replace('जतिद्र', 'जितेंद्र').replace('शशकिल', 'शशिकला').replace('शविचरण', 'शिवचरण').replace('माधूरी', 'माधुरी').replace('रनिा', 'रिना').replace('मयििांचद', 'मियाचंद').replace('अमति', 'अमित').replace('सलिराज', 'शिलेराज').replace('वदिद्या', 'विद्या').replace('रामसगि', 'रामसिंग').replace('कसिनसगि', 'किसनसिंग').replace('राजूसगि', 'राजूसिंग').replace('प्रवणि', 'प्रवीण').replace('शदि', 'शिंदे').replace('शर्मलिर्ता', 'शर्मिला').replace('वरािज', 'विराज').replace('शरीिष', 'शिरीष').replace('चरािग', 'चिराग').replace('रूचतिा', 'रुचिता').replace('नरिजन', 'निरंजन').replace('दपिक', 'दीपक')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = row.get('वय', '')
            epic_no = row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', ''))
            house_no = row.get('घर क्रमांक', '-')
            part_no = row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', ''))
            
            # ४. तळाशी शुद्ध मराठी माहितीचा मजकूर (Paragraph फॉरमॅटमुळे जोडाक्षरे १००% शुद्ध येतील)
            info_html = f"""
            <b>मतदार नं. :</b> {voter_no} <br/>
            <b>नाव :</b> {clean_name} <br/>
            <b>लिंग / वय :</b> {clean_gender} / {age} <br/>
            <b>ओळखपत्र क्र. :</b> {epic_no} <br/>
            <b>घर क्रमांक :</b> {house_no} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>भाग क्रमांक :</b> {part_no} <br/>
            <b>मतदान केंद्र :</b> {polling_station}
            """
            slip_elements.append(Paragraph(info_html, marathi_style))
            
            # बॉक्स आऊटलाईन डिझाईन
            voter_table = Table([[slip_elements]], colWidths=[380], rowHeights=[535])
            voter_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            
            story.append(voter_table)
            story.append(PageBreak())
            
        if story and isinstance(story[-1], PageBreak):
            story.pop()
            
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # डाऊनलोड बटन
    st.markdown("---")
    if st.button("🚀 नवीन A5 Portrait मतदार स्लिप्स पीडीएफ जनरेट करा"):
        banner_data = uploaded_banner.read() if uploaded_banner else None
        
        with st.spinner("तुमच्या शुद्ध मराठी आणि क्यमाईज्ड लेआउटच्या स्लिप्स तयार होत आहेत..."):
            pdf_out = generate_perfect_slips(df, banner_data, polling_station_input)
            
            st.success("🎉 सर्व स्लिप्स अचूक डिझाईन आणि शुद्ध मराठीत तयार झाल्या आहेत!")
            st.download_button(
                label="📥 A5 Portrait मतदार स्लिप्स (PDF) डाऊनलोड करा",
                data=pdf_out,
                file_name="A5_Portrait_Voter_Slips_Final.pdf",
                mime="application/pdf"
            )
