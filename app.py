import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import urllib.request
import re

st.set_page_config(page_title="A5 Portrait Voter Slip Generator", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (A5 Portrait - Full Page Layout)")

# १. पॅनेल बॅनर आणि सेटिंग्ज
st.sidebar.header("⚙️ पॅनेल कॉन्फिगरेशन")
uploaded_banner = st.sidebar.file_uploader("१. पॅनेलचा बॅनर इमेज अपलोड करा", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("२. मतदान केंद्राचे नाव", "ज. प. प्रा. शाळा")

# २. एक्सेल फाईल अपलोड
st.subheader("📊 मतदार एक्सेल फाईल अपलोड करा")
uploaded_file = st.file_uploader("तुमची एक्सेल फाईल (.xlsx) इथे अपलोड करा", type=["xlsx"])

# गुगलचा नोतो सॅन्स देवनागरी फॉन्ट ऑनलाईन रजिस्टर करणे
@st.cache_resource
def register_marathi_font():
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
        font_data = urllib.request.urlopen(font_url).read()
        font_io = io.BytesIO(font_data)
        pdfmetrics.registerFont(TTFont('NotoSans', font_io))
        return 'NotoSans'
    except Exception as e:
        return 'Helvetica'

font_name = register_marathi_font()

# जेंडर आणि स्पेलिंग मधील चुका शुद्ध मराठीत सुधारणारे फंक्शन
def clean_gender_and_text(text):
    text = str(text).strip()
    if re.search(r'(सतरी|त्री|जी|श्रीमती|^str|^st|^q|^g)', text, re.IGNORECASE):
        return "स्त्री"
    elif re.search(r'(पु|पु.|पुरुष|^pur|^pu|^t)', text, re.IGNORECASE):
        return "पु"
    return text

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("✅ एक्सेल फाईल यशस्वीरित्या लोड झाली!")
    
    # ३. पीडीएफ जनरेशन लॉजिक (A5 Portrait - Full Page Per Voter)
    def generate_a5_portrait_slips(data_frame, banner_bytes, polling_station):
        buffer = io.BytesIO()
        # A5 Portrait सेटअप (Margins कमी केल्या आहेत जेणेकरून पूर्ण पानावर डिझाईन बसेल)
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
        
        # पूर्ण पानावर फिट बसण्यासाठी मोठा फॉन्ट (Size 18) आणि स्पेसिंग (Leading 28)
        marathi_main_style = ParagraphStyle(
            'MarathiMainPortrait',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=18,
            leading=28,
            textColor=colors.black
        )
        
        # कापावे रेषेसाठी स्टाईल
        cut_line_style = ParagraphStyle(
            'CutLineStylePortrait',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            leading=16,
            alignment=1, # Center
            textColor=colors.dimgrey
        )
        
        for index, row in data_frame.iterrows():
            slip_content = []
            
            # १. पॅनेल बॅनर (A5 Portrait नुसार रुंदी ३८० केली आहे)
            if banner_bytes:
                banner_img = Image(io.BytesIO(banner_bytes), width=380, height=95)
                slip_content.append(banner_img)
            else:
                slip_content.append(Paragraph("<b><font color='blue' size='16'>[इथे तुमचा पॅनेल बॅनर दिसेल]</font></b>", cut_line_style))
            
            slip_content.append(Spacer(1, 15))
            slip_content.append(Paragraph("----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------", cut_line_style))
            slip_content.append(Spacer(1, 20))
            
            # डेटा क्लिनिंग आणि मॅपिंग
            voter_no = row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            # वेलांटीच्या चुका दुरुस्त करणे
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिांका', 'प्रियांका').replace('आदत्यि', 'आद्या').replace('मुजाहदि', 'मुजाहिद').replace('मनषिा', 'मनिषा').replace('वलिलास', 'विलास').replace('सारकिा', 'सारिका').replace('सुरेद्र', 'सुरेंद्र').replace('मंजरीि', 'मंजिरी').replace('भाटयिा', 'भाटिया').replace('गंगासगि', 'गंगासिंग').replace('सुरेद्रसगि', 'सुरेंद्रसिंग').replace('मांजशिी', 'मांजिरी').replace('गुरवदिर', 'गुरविंदर').replace('जतिंद्र', 'जितेन्द्र').replace('जतिद्र', 'जितेंद्र').replace('शशकिल', 'शशिकला').replace('शविचरण', 'शिवचरण').replace('माधूरी', 'माधुरी').replace('रनिा', 'रिना').replace('मयििांचद', 'मियाचंद').replace('अमति', 'अमित').replace('सलिराज', 'शिलेराज').replace('वदिद्या', 'विद्या').replace('रामसगि', 'रामसिंग').replace('कसिनसगि', 'किसनसिंग').replace('राजूसगि', 'राजूसिंग').replace('प्रवणि', 'प्रवीण').replace('शदि', 'शिंदे').replace('शर्मलिर्ता', 'शर्मिला').replace('वरािज', 'विराज').replace('शरीिष', 'शिरीष').replace('चरािग', 'चिराग').replace('रूचतिा', 'रुचिता').replace('नरिजन', 'निरंजन').replace('दपिक', 'दीपक')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = row.get('वय', '')
            epic_no = row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', ''))
            house_no = row.get('घर क्रमांक', '-')
            part_no = row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', ''))
            
            # २. मुख्य माहितीचा मजकूर (A5 Portrait Full Screen Layout)
            info_html = f"""
            <b>मतदार नं. :</b> {voter_no} <br/><br/>
            <b>नाव :</b> {clean_name} <br/><br/>
            <b>लिंग / वय :</b> {clean_gender} / {age} <br/><br/>
            <b>ओळखपत्र क्र. :</b> {epic_no} <br/><br/>
            <b>घर क्रमांक :</b> {house_no} <br/><br/>
            <b>भाग क्रमांक :</b> {part_no} <br/><br/>
            <b>मतदान केंद्र :</b> {polling_station}
            """
            
            slip_content.append(Paragraph(info_html, marathi_main_style))
            slip_content.append(Spacer(1, 15))
            
            # पूर्ण A5 पेज कव्हर करणारा सुंदर आऊटलाईन बॉक्स (Width 390, Height 530)
            voter_table = Table([[slip_content]], colWidths=[390], rowHeights=[530])
            voter_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 2, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 20),
                ('BOTTOMPADDING', (0,0), (-1,-1), 20),
                ('LEFTPADDING', (0,0), (-1,-1), 20),
                ('RIGHTPADDING', (0,0), (-1,-1), 20),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BACKGROUND', (0,0), (-1,-1), colors.white)
            ]))
            
            story.append(voter_table)
            
            # प्रत्येक मतदारानंतर कंपल्सरी पेज ब्रेक
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
        
        with st.spinner("तुमच्या फुल पेज उभ्या स्लिप्स तयार होत आहेत..."):
            pdf_out = generate_a5_portrait_slips(df, banner_data, polling_station_input)
            
            st.success("🎉 सर्व स्लिप्स A5 Portrait फॉरमॅटमध्ये पूर्ण पानावर फिट बसल्या आहेत!")
            st.download_button(
                label="📥 A5 Portrait मतदार स्लिप्स (PDF) डाऊनलोड करा",
                data=pdf_out,
                file_name="A5_Portrait_Voter_Slips.pdf",
                mime="application/pdf"
            )
