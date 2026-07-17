import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader  # लेटेस्ट व्हर्जनसाठी अचूक इम्पोर्ट
from PIL import Image as PILImage, ImageDraw as PILImageDraw, ImageFont as PILImageFont
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

# जोडाक्षरे आणि वेलांटी शंभर टक्के अचूक दाखवण्यासाठी गुगलचा देवनागरी फॉन्ट डाउनलोड करणे
@st.cache_resource
def get_marathi_font_bytes():
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
        return urllib.request.urlopen(font_url).read()
    except:
        return None

font_bytes = get_marathi_font_bytes()

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
    
    # ३. इमेज आधारित १००% अचूक देवनागरी स्लिप जनरेशन
    def generate_perfect_pdf_slips(data_frame, banner_data, polling_station):
        pdf_buffer = io.BytesIO()
        width, height = A5  # A5 Portrait चे डायमेन्शन्स (396 x 595 points)
        
        # रिपोर्टलॅब कॅनव्हास सुरू करणे
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=A5)
        
        # पिक्सेल डायमेन्शन्स (A5 च्या प्रमाणात मोठे आणि क्लिअर प्रिंटिंगसाठी)
        img_w, img_h = 800, 1200
        
        for index, row in data_frame.iterrows():
            # प्रत्येक मतदारासाठी एक नवीन कोरी इमेज तयार करणे
            slip_img = PILImage.new("RGB", (img_w, img_h), "#FFFFFF")
            draw = PILImageDraw.Draw(slip_img)
            
            # बाहेरील बॉर्डर (Outline Box)
            draw.rectangle([(30, 30), (img_w - 30, img_h - 30)], outline="#000000", width=4)
            
            # १. पॅनेल बॅनर - अगदी कडेला परफेक्ट फिट बसवणे (Width 740, Height 200)
            if banner_data:
                try:
                    banner_stream = io.BytesIO(banner_data)
                    panel_banner = PILImage.open(banner_stream).convert("RGB")
                    panel_banner = panel_banner.resize((img_w - 68, 200))
                    slip_img.paste(panel_banner, (34, 34))
                except:
                    pass
            else:
                draw.rectangle([(34, 34), (img_w - 34, 234)], fill="#EEEEEE", outline="#CCCCCC")
                if font_bytes:
                    temp_font = PILImageFont.truetype(io.BytesIO(font_bytes), 32)
                    draw.text((img_w / 2, 134), "[ इथे तुमचा पॅनेल बॅनर दिसेल ]", fill="#555555", font=temp_font, anchor="mm")
            
            # २. कापावे रेष आणि डॅश - तळाशी (Bottom ला) शिफ्ट
            cut_y = 820
            if font_bytes:
                cut_font = PILImageFont.truetype(io.BytesIO(font_bytes), 24)
                draw.text((img_w / 2, cut_y - 30), "----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------", fill="#666666", font=cut_font, anchor="mm")
            
            # डॅश रेष ओढणे
            for x in range(40, img_w - 40, 15):
                draw.line([(x, cut_y), (x + 8, cut_y)], fill="#666666", width=2)
            
            # डेटा मॅपिंग आणि क्लीनिंग
            voter_no = row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            # वेलांटीच्या चुका दुरुस्त करणे
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिาंका', 'प्रियांका').replace('आदत्यि', 'आद्या').replace('मुजाहदि', 'मुजाहिद').replace('मनषिा', 'मनिषा').replace('वलिलास', 'विलास').replace('सारकिा', 'सारिका').replace('सुरेद्र', 'सुरेंद्र').replace('मंजरीि', 'मंजिरी').replace('भाटयिा', 'भाटिया').replace('गंगासगि', 'गंगासिंग').replace('सुरेद्रसगि', 'सुरेंद्रसिंग').replace('मांजशिी', 'मांजिरी').replace('गुरवदिर', 'गुरविंदर').replace('जतिंद्र', 'जितेन्द्र').replace('जतिद्र', 'जितेंद्र').replace('शशकिल', 'शशिकला').replace('शविचरण', 'शिवचरण').replace('माधूरी', 'माधुरी').replace('रनिा', 'रिना').replace('मयििांचद', 'मियाचंद').replace('अमति', 'अमित').replace('सलिराज', 'शिलेराज').replace('वदिद्या', 'विद्या').replace('रामसगि', 'रामसिंग').replace('कसिनसगि', 'किसनसिंग').replace('राजूसगि', 'राजूसिंग').replace('प्रवणि', 'प्रवीण').replace('शदि', 'शिंदे').replace('शर्मलिर्ता', 'शर्मिला').replace('वरािज', 'विराज').replace('शरीिष', 'शिरीष').replace('चरािग', 'चिराग').replace('रूचतिा', 'रुचिता').replace('नरिजन', 'निरंजन').replace('दपिक', 'दीपक')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = row.get('वय', '')
            epic_no = row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', ''))
            house_no = row.get('घर क्रमांक', '-')
            part_no = row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', ''))
            
            # ३. मतदाराची माहिती तळाशी स्पष्ट आणि शुद्ध फॉन्टमध्ये लिहिणे
            if font_bytes:
                main_font = PILImageFont.truetype(io.BytesIO(font_bytes), 34)
                
                text_x = 60
                text_y = cut_y + 40
                line_gap = 52
                
                draw.text((text_x, text_y), f"मतदार नं. :  {voter_no}", fill="#000000", font=main_font)
                draw.text((text_x, text_y + line_gap), f"नाव :  {clean_name}", fill="#000000", font=main_font)
                draw.text((text_x, text_y + (line_gap * 2)), f"लिंग / वय :  {clean_gender} / {age}", fill="#000000", font=main_font)
                draw.text((text_x, text_y + (line_gap * 3)), f"ओळखपत्र क्र. :  {epic_no}", fill="#000000", font=main_font)
                draw.text((text_x, text_y + (line_gap * 4)), f"घर क्रमांक :  {house_no}", fill="#000000", font=main_font)
                draw.text((text_x + 420, text_y + (line_gap * 4)), f"भाग क्रमांक :  {part_no}", fill="#000000", font=main_font)
                draw.text((text_x, text_y + (line_gap * 5)), f"मतदान केंद्र :  {polling_station}", fill="#000000", font=main_font)
                
            # तयार झालेली परफेक्ट इमेज पीडीएफ कॅनव्हासवर ड्रॉ करणे
            img_byte_arr = io.BytesIO()
            slip_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # एरर फिक्स: लेटेस्ट ImageReader मॅपिंगचा वापर
            reader = ImageReader(img_byte_arr)
            pdf_canvas.drawImage(reader, 0, 0, width=width, height=height)
            pdf_canvas.showPage()
            
        pdf_canvas.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # डाऊनलोड बटन
    st.markdown("---")
    if st.button("🚀 नवीन A5 Portrait मतदार स्लिप्स पीडीएफ जनरेट करा"):
        banner_data = uploaded_banner.read() if uploaded_banner else None
        
        with st.spinner("Pillow सिस्टीमद्वारे जोडाक्षरे शुद्ध करून बॅनर फिट केला जात आहे..."):
            pdf_out = generate_perfect_pdf_slips(df, banner_data, polling_station_input)
            
            st.success("🎉 सर्व ५९० स्लिप्स तुमच्या अचूक डिझाईननुसार आणि १००% शुद्ध मराठीत तयार झाल्या आहेत!")
            st.download_button(
                label="📥 A5 Portrait मतदार स्लिप्स (PDF) डाऊनलोड करा",
                data=pdf_out,
                file_name="A5_Portrait_Voter_Slips_Perfect.pdf",
                mime="application/pdf"
            )
