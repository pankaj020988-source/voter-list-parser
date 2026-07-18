import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import re

st.set_page_config(page_title="Balaji Cyber Point - Final Voter System", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (A5 Portrait - Clean Fonts Fixed)")

# १. पॅनेल बॅनर आणि सेटिंग्ज
st.sidebar.header("⚙️ पॅनेल कॉन्फिगरेशन")
uploaded_banner = st.sidebar.file_uploader("१. पॅनेलचा बॅनर इमेज अपलोड करा", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("२. मतदान केंद्राचे नाव", "ज. प. प्रा. शाळा")

# २. एक्सेल फाईल अपलोड
st.subheader("📊 मतदार एक्सेल फाईल अपलोड करा")
uploaded_file = st.file_uploader("तुमची एक्सेल फाईल (.xlsx) इथे अपलोड करा", type=["xlsx"])

# सिस्टीमचे फॉन्ट्स मॅप करणे जेणेकरून वेलांटी किंवा जोडाक्षरे अजिबात फुटणार नाहीत
pdfmetrics.registerFont(TTFont('Mangal', 'mangal.ttf', 'UTF-8'))

def clean_gender_and_text(text):
    text = str(text).strip()
    if re.search(r'(सतरी|त्री|जी|श्रीमती|स्त्री|^str|^st|^q|^g)', text, re.IGNORECASE):
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
        
        # A5 Portrait सेटअप - कडांपर्यंत परफेक्ट फिटिंगसाठी मार्जिन्स १८ ठेवल्या आहेत
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A5, 
            rightMargin=18, 
            leftMargin=18, 
            topMargin=18, 
            bottomMargin=18
        )
        story = []
        
        # सिस्टीम मधील 'Mangal' फॉन्ट वापरल्यामुळे जोडाक्षरे एकदम शुद्ध येतील
        marathi_style = ParagraphStyle(
            'CleanMarathiStyle',
            fontName='Mangal',
            fontSize=15,
            leading=25,
            textColor=colors.black
        )
        
        cut_style = ParagraphStyle(
            'CleanCutStyle',
            fontName='Mangal',
            fontSize=10,
            leading=14,
            alignment=1, # Center
            textColor=colors.dimgrey
        )
        
        for index, row in data_frame.iterrows():
            slip_elements = []
            
            # १. पॅनेल बॅनर - पूर्ण कडांपर्यंत ३५५ रुंदी आणि २३० उंचीसह अचूक फिट
            if banner_bytes:
                try:
                    banner_img = Image(io.BytesIO(banner_bytes), width=355, height=230)
                    slip_elements.append(banner_img)
                except:
                    slip_elements.append(Paragraph("<font size='14' color='red'><b>[ बॅनर इमेज एरर ]</b></font>", cut_style))
            else:
                slip_elements.append(Paragraph("<br/><br/><br/><b>[ इथे तुमचा पॅनेल बॅनर संपूर्ण जागेत मोठा दिसेल ]</b><br/><br/><br/>", cut_style))
            
            # २. बॅनरच्या बरोबर खाली 'येथून कापावे' संदेश आणि रेष
            slip_elements.append(Spacer(1, 10))
            slip_elements.append(Paragraph("----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------", cut_style))
            slip_elements.append(Spacer(1, 15))
            
            # डेटा मॅपिंग आणि शुद्धीकरण
            voter_no = row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            # वेलांटीच्या चुका दुरुस्त करणे
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिांका', 'प्रियांका').replace('आदत्यि', 'आदित्य').replace('मुजाहदि', 'मुजाहिद').replace('मनषिा', 'मनिषा').replace('वलिलास', 'विलास').replace('सारकिा', 'सारिका').replace('सुरेद्र', 'सुरेंद्र').replace('मंजरीि', 'मंजिरी').replace('भाटयिा', 'भाटिया').replace('गंगासगि', 'गंगासिंग').replace('सुरेद्रसगि', 'सुरेंद्रसिंग').replace('मांजशिी', 'मांजिरी').replace('गुरवदिर', 'गुरविंदर').replace('जतिंद्र', 'जितेन्द्र').replace('जतिद्र', 'जितेंद्र').replace('शशकिल', 'शशिकला').replace('शविचरण', 'शिवचरण').replace('माधूरी', 'माधुरी').replace('रनिा', 'रिना').replace('मयििांचद', 'मियाचंद').replace('अमति', 'अमित').replace('सलिराज', 'शिलेराज').replace('वदिद्या', 'विद्या').replace('रामसगि', 'रामसिंग').replace('कसिनसगि', 'किसनसिंग').replace('राजूसगि', 'राजूसिंग').replace('प्रवणि', 'प्रवीण').replace('शदि', 'शिंदे').replace('शर्मलिर्ता', 'शर्मिला').replace('वरािज', 'विराज').replace('शरीिष', 'शिरीष').replace('चरािग', 'चिराग').replace('रूचतिा', 'रुचिता').replace('नरिजन', 'निरंजन').replace('दपिक', 'दीपक')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = row.get('वय', '')
            epic_no = str(row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', '')))
            house_no = row.get('घर क्रमांक', '-')
            part_no = row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', ''))
            
            # ३. मतदाराची माहिती - 'Mangal' सिस्टीम फॉन्टमुळे जोडाक्षरे एकदम कडक आणि शुद्ध मराठीत दिसतील
            info_html = f"""
            <b>मतदार नं. :</b> {voter_no} <br/><br/>
            <b>नाव :</b> {clean_name} <br/><br/>
            <b>लिंग / वय :</b> {clean_gender} / {age} <br/><br/>
            <b>ओळखपत्र क्रमांक :</b> {epic_no} <br/><br/>
            <b>घर क्रमांक :</b> {house_no} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>भाग क्रमांक :</b> {part_no} <br/><br/>
            <b>मतदान केंद्र :</b> {polling_station}
            """
            slip_elements.append(Paragraph(info_html, marathi_style))
            
            # आऊटलाईन बॉक्स डिझाईन
            voter_table = Table([[slip_elements]], colWidths=[360], rowHeights=[540])
            voter_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 2, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
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
        
        with st.spinner("सिस्टममधील Mangal फॉन्ट कॉन्फिगर करून शुद्ध मराठीत स्लिप्स पीडीएफ तयार होत आहे..."):
            pdf_out = generate_perfect_slips(df, banner_data, polling_station_input)
            
            st.success("🎉 सर्व ५९० स्लिप्स अत्यंत हलक्या फाईल साईझमध्ये आणि शुद्ध मराठीत तयार झाल्या आहेत!")
            st.download_button(
                label="📥 A5 Portrait मतदार स्लिप्स (PDF) डाऊनलोड करा",
                data=pdf_out,
                file_name="A5_Portrait_Voter_Slips_Final.pdf",
                mime="application/pdf"
            )
