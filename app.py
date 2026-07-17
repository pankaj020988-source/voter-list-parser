import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
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
    
    # ३. कॅनव्हास आधारित सुरक्षित पीडीएफ जनरेशन लॉजिक (A5 Portrait)
    def generate_a5_portrait_slips_canvas(data_frame, banner_bytes, polling_station):
        buffer = io.BytesIO()
        # A5 Portrait चे डायमेन्शन्स निश्चित करणे
        width, height = A5
        c = canvas.Canvas(buffer, pagesize=A5)
        
        for index, row in data_frame.iterrows():
            # बाहेरील आऊटलाईन बॉक्स (पूर्ण A5 वर सुंदर फिटिंग)
            c.setStrokeColor(colors.black)
            c.setLineWidth(2)
            c.rect(15, 15, width - 30, height - 30)
            
            # १. पॅनेल बॅनर ड्रॉ करणे
            if banner_bytes:
                try:
                    banner_img = io.BytesIO(banner_bytes)
                    c.drawImage(banner_img, 20, height - 110, width=width - 40, height=85)
                except:
                    c.setFont(font_name, 14)
                    c.drawCentredString(width / 2, height - 70, "[ पॅनेल बॅनर इमेज ]")
            else:
                c.setFont(font_name, 16)
                c.drawCentredString(width / 2, height - 70, "[ इथे तुमचा पॅनेल बॅनर दिसेल ]")
                
            # कापावे रेष
            c.setStrokeColor(colors.dimgrey)
            c.setLineWidth(0.5)
            c.setDash(4, 4)
            c.line(20, height - 130, width - 20, height - 130)
            c.setDash() # रिसेट डॅश
            
            c.setFont(font_name, 11)
            c.setFillColor(colors.dimgrey)
            c.drawCentredString(width / 2, height - 125, "----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------")
            
            # डेटा क्लिनिंग आणि मॅपिंग
            voter_no = row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिांका', 'प्रियांका').replace('आदत्यि', 'आद्या').replace('मुजाहदि', 'मुजाहिद').replace('मनषिा', 'मनिषा').replace('वलिलास', 'विलास').replace('सारकिा', 'सारिका').replace('सुरेद्र', 'सुरेंद्र').replace('मंजरीि', 'मंजिरी').replace('भाटयिा', 'भाटिया').replace('गंगासगि', 'गंगासिंग').replace('सुरेद्रसगि', 'सुरेंद्रसिंग').replace('मांजशिी', 'मांजिरी').replace('गुरवदिर', 'गुरविंदर').replace('जतिंद्र', 'जितेन्द्र').replace('जतिद्र', 'जितेंद्र').replace('शशकिल', 'शशिकला').replace('शविचरण', 'शिवचरण').replace('माधूरी', 'माधुरी').replace('रनिा', 'रिना').replace('मयििांचद', 'मियाचंद').replace('अमति', 'अमित').replace('सलिराज', 'शिलेराज').replace('वदिद्या', 'विद्या').replace('रामसगि', 'रामसिंग').replace('कसिनसगि', 'किसनसिंग').replace('राजूसगि', 'राजूसिंग').replace('प्रवणि', 'प्रवीण').replace('शदि', 'शिंदे').replace('शर्मलिर्ता', 'शर्मिला').replace('वरािज', 'विराज').replace('शरीिष', 'शिरीष').replace('चरािग', 'चिراق').replace('रूचतिा', 'रुचिता').replace('नरिजन', 'निरंजन').replace('दपिक', 'दीपक')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = row.get('वय', '')
            epic_no = row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', ''))
            house_no = row.get('घर क्रमांक', '-')
            part_no = row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', ''))
            
            # २. मजकूर पूर्ण पानावर मोठा आणि ठळक टाईप करणे (Font Size 18)
            c.setFillColor(colors.black)
            c.setFont(font_name, 18)
            
            start_y = height - 170
            line_gap = 35
            
            c.drawString(35, start_y, f"मतदार नं. :  {voter_no}")
            c.drawString(35, start_y - line_gap, f"नाव :  {clean_name}")
            c.drawString(35, start_y - (line_gap * 2), f"लिंग / वय :  {clean_gender} / {age}")
            c.drawString(35, start_y - (line_gap * 3), f"ओळखपत्र क्र. :  {epic_no}")
            c.drawString(35, start_y - (line_gap * 4), f"घर क्रमांक :  {house_no}")
            c.drawString(35, start_y - (line_gap * 5), f"भाग क्रमांक :  {part_no}")
            c.drawString(35, start_y - (line_gap * 6), f"मतदान केंद्र :  {polling_station}")
            
            # नवीन पानावर जाणे
            c.showPage()
            
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    # डाऊनलोड बटन
    st.markdown("---")
    if st.button("🚀 नवीन A5 Portrait मतदार स्लिप्स पीडीएफ जनरेट करा"):
        banner_data = uploaded_banner.read() if uploaded_banner else None
        
        with st.spinner("तुमच्या फुल पेज उभ्या स्लिप्स तयार होत आहेत..."):
            pdf_out = generate_a5_portrait_slips_canvas(df, banner_data, polling_station_input)
            
            st.success("🎉 सर्व स्लिप्स A5 Portrait फॉरमॅटमध्ये पूर्ण पानावर फिट बसल्या आहेत!")
            st.download_button(
                label="📥 A5 Portrait मतदार स्लिप्स (PDF) डाऊनलोड करा",
                data=pdf_out,
                file_name="A5_Portrait_Voter_Slips.pdf",
                mime="application/pdf"
            )
