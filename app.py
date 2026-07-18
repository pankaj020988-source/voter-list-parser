import streamlit as st
import pandas as pd
import base64
import re

st.set_page_config(page_title="Balaji Cyber Point - Final Voter System", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (A5 Portrait - Safe Marathi Version)")

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
        return base64.b64encode(uploaded_image.getvalue()).decode('utf-8')
    return ""

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("✅ एक्सेल फाईल यशस्वीरित्या लोड झाली!")
    
    # ३. HTML जनरेशन लॉजिक जे थेट ब्राउझरवरून PDF बनवेल
    def generate_html_layout(data_frame, banner_b64, polling_station):
        html_content = """
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Marathi:wght@400;700&display=swap');
            @media print {
                body { background-color: #ffffff; }
                .page-container { page-break-after: always; }
            }
            body {
                font-family: 'Noto Sans Marathi', sans-serif;
                margin: 0;
                padding: 0;
            }
            .page-container {
                width: 148mm;
                height: 210mm;
                box-sizing: border-box;
                padding: 8mm;
                margin: 0 auto;
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
                font-size: 18px;
                line-height: 2.2;
                color: #000000;
            }
            .info-row {
                margin-bottom: 6px;
            }
            .bold-label {
                font-weight: 700;
            }
            .flex-row {
                width: 100%;
                display: flex;
            }
            .left-col {
                width: 50%;
            }
            .right-col {
                width: 50%;
            }
        </style>
        </head>
        <body>
        """
        
        for index, row in data_frame.iterrows():
            voter_no = str(row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1)))
            raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            
            # वेलांट्या आणि चुकीचे शब्द अचूक साफ करणे
            clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता').replace('प्रयिांका', 'प्रियांका').replace('आदत्यि', 'आदित्य').replace('मुजाहदि', 'मुजाहिद').replace('मनषिा', 'मनिषा')
            
            raw_gender = row.get('लिंग', '')
            clean_gender = clean_gender_and_text(raw_gender)
            age = str(row.get('वय', ''))
            epic_no = str(row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', '')))
            house_no = str(row.get('घर क्रमांक', '-'))
            part_no = str(row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', '')))
            
            html_content += f"""
            <div class="page-container">
                <div class="outer-box">
                    <div class="banner-container">
            """
            if banner_b64:
                html_content += f'<img src="data:image/jpeg;base64,{banner_b64}" class="banner-img">'
            else:
                html_content += '<div class="no-banner">[ इथे पॅनेल बॅनर दिसेल ]</div>'
                
            html_content += f"""
                    </div>
                    
                    <div class="cut-line-text">----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------</div>
                    <div class="cut-line"></div>
                    
                    <div class="content-container">
                        <div class="info-row"><span class="bold-label">मतदार नं. :</span> {voter_no}</div>
                        <div class="info-row"><span class="bold-label">नाव :</span> {clean_name}</div>
                        <div class="info-row"><span class="bold-label">लिंग / वय :</span> {clean_gender} / {age}</div>
                        <div class="info-row"><span class="bold-label">ओळखपत्र क्रमांक :</span> {epic_no}</div>
                        
                        <div class="flex-row">
                            <div class="left-col"><span class="bold-label">घर क्रमांक :</span> {house_no}</div>
                            <div class="right-col"><span class="bold-label">भाग क्रमांक :</span> {part_no}</div>
                        </div>
                        
                        <div class="info-row" style="margin-top: 4px;"><span class="bold-label">मतदान केंद्र :</span> {polling_station}</div>
                    </div>
                </div>
            </div>
            """
            
        html_content += "</body></html>"
        return html_content

    # प्रिंट प्रिव्ह्यू आणि प्रिंट बटन
    banner_base64 = get_image_base64(uploaded_banner)
    final_html = generate_html_layout(df, banner_base64, polling_station_input)
    
    st.markdown("---")
    st.subheader("🚀 पायरी ३: मतदार स्लिप्स प्रिंट / PDF म्हणून सेव्ह करा")
    
    # थेट ब्राउझर प्रिंटर ओपन करण्यासाठी छोटी स्क्रिप्ट
    components_html = f"""
        <div style="text-align: center; margin: 20px 0;">
            <button onclick="var printWindow = window.open('', '_blank'); printWindow.document.write({repr(final_html)}); printWindow.document.close(); printWindow.focus(); setTimeout(function() {{ printWindow.print(); }}, 1000);" 
                style="background-color: #4CAF50; color: white; padding: 14px 28px; font-size: 18px; border: none; cursor: pointer; border-radius: 8px; font-weight: bold;">
                📥 सर्व ५९० स्लिप्स (PDF) डाऊनलोड / प्रिंट करा
            </button>
        </div>
    """
    st.components.v1.html(components_html, height=100)
    
    # लाइव्ह प्रिव्ह्यू पाहण्यासाठी
    with st.expander("👀 पहिल्या काही स्लिप्सचा नमुना पाहण्यासाठी इथे क्लिक करा"):
        st.components.v1.html(final_html, height=600, scrolling=True)
