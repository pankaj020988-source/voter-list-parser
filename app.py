import streamlit as st
import pandas as pd
from xhtml2pdf import pisa
import io
import base64
import re

st.set_page_config(page_title="Balaji Cyber Point - Final Voter System", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (A5 Portrait - Perfect Marathi)")

# १. पॅनेल बॅनर आणि सेटिंग्ज
st.sidebar.header("⚙️ पॅनेल कॉन्फिगरेशन")
uploaded_banner = st.sidebar.file_uploader("१. पॅनेलचा बॅनर इमेज अपलोड करा", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("२. मतदान केंद्राचे नाव", "ज. प. प्रा. शाळा")

# २. एक्सेल फाईल अपलोड
st.subheader("📊 मतदार एक्सेल फाईल अपलोड करा")
uploaded_file = st.file_uploader("तुमची एक्सेल फाईल (.xlsx) इथे अपलोड करा", type=["xlsx"])

def clean_gender_and_text(text):
    text = str(text).strip()
    if re.search(r'(सतरी|त्री|जी|श्रीमती|स्त्री|^str|^st|^q|^g)', text, re.IGNORECASE):
        return "स्त्री"
    elif re.search(r'(पु|पु.|पुरुष|^pur|^pu|^t)', text, re.IGNORECASE):
        return "पु"
    return text

def get_image_base64(uploaded_image):
    if uploaded_image is not None:
        bytes_data = uploaded_image.getvalue()
        base64_encoded = base64.b64encode(bytes_data).decode('utf-8')
        image_format = uploaded_image.type.split('/')[-1]
        return f"data:image/{image_format};base64,{base64_encoded}"
    return ""

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("✅ एक्सेल फाईल यशस्वीरित्या लोड झाली!")
    
    def generate_html_pdf(data_frame, banner_base64, polling_station):
        # A5 Size CSS with perfect Marathi font support (using system fonts like Mangal/Arial Unicode MS fallback)
        html_content = """
        <html>
        <head>
        <style>
            @page {
                size: A5 portrait;
                margin: 1.5cm;
            }
            body {
                font-family: 'Mangal', 'Arial Unicode MS', 'FreeSans', sans-serif;
                font-size: 16pt;
                line-height: 1.8;
                color: #000000;
            }
            .slip-container {
                border: 2px solid #000;
                padding: 15px;
                height: 95%; /* Make it fill almost the whole page */
                box-sizing: border-box;
            }
            .banner-img {
                width: 100%;
                height: 100px;
                object-fit: cover;
                margin-bottom: 20px;
            }
            .no-banner {
                text-align: center;
                font-size: 18pt;
                font-weight: bold;
                color: #555;
                padding: 30px 0;
                border: 1px dashed #ccc;
                margin-bottom: 20px;
            }
            .cut-line-container {
                text-align: center;
                margin-bottom: 20px;
            }
            .cut-text {
                font-size: 12pt;
                color: #666;
                margin-bottom: 5px;
            }
            .cut-line {
                border-top: 1px dashed #666;
                width: 100%;
            }
            .info-row {
                margin-bottom: 12px;
            }
            .label {
                font-weight: bold;
            }
            .page-break {
                page-break-after: always;
            }
        </style>
        </head>
        <body>
        """
        
        for index, row in data_frame.iterrows():
            # Data Mapping & Cleaning
            voter_no = row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिांका', 'प्रियांका').replace('आदत्यि', 'आदित्य').replace('मुजाहदि', 'मुजाहिद').replace('मनषिा', 'मनिषा').replace('वलिलास', 'विलास').replace('सारकिा', 'सारिका').replace('सुरेद्र', 'सुरेंद्र').replace('मंजरीि', 'मंजिरी').replace('भाटयिा', 'भाटिया').replace('गंगासगि', 'गंगासिंग').replace('सुरेद्रसगि', 'सुरेंद्रसिंग').replace('मांजशिी', 'मांजिरी').replace('गुरवदिर', 'गुरविंदर').replace('जतिंद्र', 'जितेन्द्र').replace('जतिद्र', 'जितेंद्र').replace('शशकिल', 'शशिकला').replace('शविचरण', 'शिवचरण').replace('माधूरी', 'माधुरी').replace('रनिा', 'रिना').replace('मयििांचद', 'मियाचंद').replace('अमति', 'अमित').replace('सलिराज', 'शिलेराज').replace('वदिद्या', 'विद्या').replace('रामसगि', 'रामसिंग').replace('कसिनसगि', 'किसनसिंग').replace('राजूसगि', 'राजूसिंग').replace('प्रवणि', 'प्रवीण').replace('शदि', 'शिंदे').replace('शर्मलिर्ता', 'शर्मिला').replace('वरािज', 'विराज').replace('शरीिष', 'शिरीष').replace('चरािग', 'चिराग').replace('रूचतिा', 'रुचिता').replace('नरिजन', 'निरंजन').replace('दपिक', 'दीपक')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = row.get('वय', '')
            epic_no = row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', ''))
            house_no = row.get('घर क्रमांक', '-')
            part_no = row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', ''))

            html_content += '<div class="slip-container">'
            
            # Banner
            if banner_base64:
                html_content += f'<img src="{banner_base64}" class="banner-img" />'
            else:
                html_content += '<div class="no-banner">[ इथे तुमचा पॅनेल बॅनर दिसेल ]</div>'
                
            # Cut Line
            html_content += """
            <div class="cut-line-container">
                <div class="cut-text">मतदान केंद्रात जाण्यापूर्वी येथून कापावे</div>
                <div class="cut-line"></div>
            </div>
            """
            
            # Voter Info
            html_content += f"""
            <div class="info-row"><span class="label">मतदार नं. :</span> {voter_no}</div>
            <div class="info-row"><span class="label">नाव :</span> {clean_name}</div>
            <div class="info-row"><span class="label">लिंग / वय :</span> {clean_gender} / {age}</div>
            <div class="info-row"><span class="label">ओळखपत्र क्र. :</span> {epic_no}</div>
            <div class="info-row"><span class="label">घर क्रमांक :</span> {house_no}</div>
            <div class="info-row"><span class="label">भाग क्रमांक :</span> {part_no}</div>
            <div class="info-row"><span class="label">मतदान केंद्र :</span> {polling_station}</div>
            """
            
            html_content += '</div>' # End slip-container
            
            # Add page break except for the last item
            if index < len(data_frame) - 1:
                html_content += '<div class="page-break"></div>'
                
        html_content += """
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=pdf_buffer,
            encoding='UTF-8'
        )
        
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    st.markdown("---")
    if st.button("🚀 नवीन A5 Portrait मतदार स्लिप्स जनरेट करा"):
        # Convert banner to base64 if uploaded
        banner_b64 = get_image_base64(uploaded_banner)
        
        with st.spinner("तुमच्या परफेक्ट मराठी फॉन्टसह स्लिप्स तयार होत आहेत..."):
            try:
                pdf_out = generate_html_pdf(df, banner_b64, polling_station_input)
                st.success("🎉 सर्व स्लिप्स तयार झाल्या आहेत! फॉन्ट एकदम क्लिअर असेल.")
                st.download_button(
                    label="📥 A5 Portrait मतदार स्लिप्स (PDF) डाऊनलोड करा",
                    data=pdf_out,
                    file_name="A5_Portrait_Voter_Slips_PerfectFont.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF बनवताना एरर आली: {e}")
