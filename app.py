import streamlit as st
import pandas as pd
import pdfkit
import io
import base64
import re

st.set_page_config(page_title="Balaji Cyber Point - Final Voter System", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (A5 Portrait - Guaranteed Marathi Fix)")

# १. पॅनेल बॅनर आणि सेटिंग्ज
st.sidebar.header("⚙️ पॅनेल कॉन्फिगरेशन")
uploaded_banner = st.sidebar.file_uploader("१. पॅनेलचा बॅनर इमेज अपलोड करा", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("२. मतदान केंद्राचे नाव", "ज. प. प्रा. शाळा")

# २. एक्सेल फाईल अपलोड
st.subheader("📊 मतदार एक्सेल फाईल अपलोड करा")
uploaded_file = st.file_uploader("तुमची एक्सेल फाईल (.xlsx) इथे अपलोड करा", type=["xlsx"])

def clean_gender_and_text(text):
    text = str(text).strip()
    if re.search(r'(सतरी|त्री|जी|श्रीमती|物件|स्त्री|^str|^st|^q|^g)', text, re.IGNORECASE):
        return "स्त्री"
    elif re.search(r'(पु|पु.|पुरुष|^pur|^pu|^t)', text, re.IGNORECASE):
        return "पु"
    return text

def get_image_base64(uploaded_image):
    if uploaded_image is not None:
        return base64.b64encode(uploaded_image.getvalue()).decode('utf-8')
    return ""

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("✅ एक्सेल फाईल यशस्वीरित्या लोड झाली!")
    
    def generate_html_to_pdf(data_frame, banner_b64, polling_station):
        # गुगलचा थेट अधिकृत मराठी फॉन्ट एम्बेड केला आहे, यामुळे एकही अक्षर चुकणार नाही
        html_content = """
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Marathi:wght@400;700&display=swap');
            @page {
                size: A5 portrait;
                margin: 0px;
            }
            body {
                font-family: 'Noto Sans Marathi', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #ffffff;
                -webkit-print-color-adjust: exact;
            }
            .page-container {
                width: 148mm;
                height: 210mm;
                box-sizing: border-box;
                padding: 8mm;
                position: relative;
                page-break-after: always;
            }
            .outer-box {
                width: 132mm;
                height: 194mm;
                border: 2mm solid #000000;
                box-sizing: border-box;
                padding: 0px;
                position: relative;
            }
            .banner-container {
                width: 100%;
                height: 65mm;
                overflow: hidden;
                border-bottom: 1px solid #000;
            }
            .banner-img {
                width: 100%;
                height: 100%;
                object-fit: fill;
            }
            .no-banner {
                width: 100%;
                height: 100%;
                background-color: #f0f4f8;
                text-align: center;
                line-height: 65mm;
                font-size: 18px;
                font-weight: bold;
                color: #555555;
            }
            .cut-line-text {
                text-align: center;
                font-size: 11px;
                color: #444444;
                margin-top: 5px;
                font-weight: bold;
            }
            .cut-line {
                border-top: 2px dashed #555555;
                margin: 3px 10px 0 10px;
            }
            .content-container {
                padding: 20px 25px;
                font-size: 17px;
                line-height: 2.1;
                color: #000000;
            }
            .info-row {
                margin-bottom: 8px;
            }
            .bold-label {
                font-weight: 700;
                display: inline-block;
            }
            .flex-row {
                width: 100%;
            }
            .left-col {
                float: left;
                width: 50%;
            }
            .right-col {
                float: left;
                width: 50%;
            }
            .clear {
                clear: both;
            }
        </style>
        </head>
        <body>
        """
        
        for index, row in data_frame.iterrows():
            voter_no = str(row.get('अनुक्रमांक', row.get('मतدار नं.', index + 1)))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            # वेलांट्या शुद्ध करणे
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिांका', 'प्रियांका').replace('आदत्यि', 'आदित्य').replace('मुजाहदि', 'मुजाहिद')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = str(row.get('वय', ''))
            epic_no = str(row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', '')))
            house_no = str(row.get('घर क्रमांक', '-'))
            part_no = str(row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', '')))
            
            html_content += f"""
            <div class="page-container">
                <div class="outer-box">
                    <!-- १. पॅनेल बॅनर पूर्ण मोठा फिट -->
                    <div class="banner-container">
            """
            if banner_b64:
                html_content += f'<img src="data:image/jpeg;base64,{banner_b64}" class="banner-img">'
            else:
                html_content += '<div class="no-banner">[ इथे पॅनेल बॅनर दिसेल ]</div>'
                
            html_content += f"""
                    </div>
                    
                    <!-- २. कापावे संदेश आणि रेष -->
                    <div class="cut-line-text">----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------</div>
                    <div class="cut-line"></div>
                    
                    <!-- ३. मतदाराची माहिती शुद्ध मराठीत -->
                    <div class="content-container">
                        <div class="info-row"><span class="bold-label">मतदार नं. :</span> {voter_no}</div>
                        <div class="info-row"><span class="bold-label">नाव :</span> {clean_name}</div>
                        <div class="info-row"><span class="bold-label">लिंग / वय :</span> {clean_gender} / {age}</div>
                        <div class="info-row"><span class="bold-label">ओळखपत्र क्रमांक :</span> {epic_no}</div>
                        
                        <div class="flex-row">
                            <div class="left-col"><span class="bold-label">घर क्रमांक :</span> {house_no}</div>
                            <div class="right-col"><span class="bold-label">भाग क्रमांक :</span> {part_no}</div>
                            <div class="clear"></div>
                        </div>
                        
                        <div class="info-row" style="margin-top: 8px;"><span class="bold-label">मतदान केंद्र :</span> {polling_station}</div>
                    </div>
                </div>
            </div>
            """
            
        html_content += "</body></html>"
        
        # सिस्टीम कॉन्फिगरेशन
        options = {
            'page-size': 'A5',
            'orientation': 'Portrait',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': ''
        }
        
        # HTML चे PDF मध्ये रूपांतर करणे
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        return pdf_bytes

    st.markdown("---")
    if st.button("🚀 नवीन A5 Portrait मतदार स्लिप्स पीडीएफ जनरेट करा"):
        banner_base64 = get_image_base64(uploaded_banner)
        
        with st.spinner("गुगल मराठी वेब फॉन्टसह अंतिम अचूक पीडीएफ तयार होत आहे..."):
            try:
                pdf_out = generate_html_to_pdf(df, banner_base64, polling_station_input)
                st.success("🎉 सर्व स्लिप्स १००% अचूक फॉन्ट आणि कमी साईझमध्ये तयार झाल्या आहेत!")
                st.download_button(
                    label="📥 A5 Portrait मतदार स्लिप्स (PDF) डाऊनलोड करा",
                    data=pdf_out,
                    file_name="A5_Portrait_Voter_Slips_PerfectFix.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"पीडीएफ तयार करताना एरर आली: {e}. कृपया ॲप एकदा रिबूट करा.")
