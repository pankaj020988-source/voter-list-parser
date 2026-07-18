import streamlit as st
import pandas as pd
import base64
import re

st.set_page_config(page_title="Balaji Cyber Point - Advanced Voter System", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (मल्टी-लेआउट सिस्टीम - कागद बचत मोड)")

# १. पॅनेल बॅनर आणि सेटिंग्ज
st.sidebar.header("⚙️ पॅनेल कॉन्फिगरेशन")
uploaded_banner = st.sidebar.file_uploader("१. पॅनेलचा बॅनर इमेज अपलोड करा", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("२. मतदान केंद्राचे नाव", "ज. प. प्रा. शाळा")

# २. लेआउट चॉईस (A5 वर 1, A4 वर 4, A4 वर 6)
st.sidebar.header("📐 प्रिंट लेआउट सेटिंग्ज")
layout_choice = st.sidebar.radio(
    "तुम्हाला एका पानावर किती स्लिप्स पाहिजेत?",
    ["A5 पाडलेले लेआउट (१ पानावर १ स्लिप)", "A4 पाडलेले लेआउट (१ पानावर ४ स्लिप्स)", "A4 पाडलेले लेआउट (१ पानावर ६ स्लिप्स)"]
)

# ३. एक्सेल फाईल अपलोड
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
    total_rows = len(df)
    st.success(f"✅ एक्सेल फाईल यशस्वीरित्या लोड झाली! एकूण मतदार: {total_rows}")
    
    # सर्व्हर हँग होऊ नये म्हणून १००-१०० मतदारांचे तुकडे (Safe Batching)
    batch_size = 100
    num_batches = (total_rows // batch_size) + (1 if total_rows % batch_size > 0 else 0)
    
    batch_options = []
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, total_rows)
        batch_options.append(f"मतदार क्र. {start_idx + 1} ते {end_idx}")
        
    selected_batch_str = st.selectbox("मजकूर लोड करण्यासाठी मतदारांची बॅच निवडा:", batch_options)
    selected_batch_idx = batch_options.index(selected_batch_str)
    
    start_pos = selected_batch_idx * batch_size
    end_pos = min(start_pos + batch_size, total_rows)
    df_batch = df.iloc[start_pos:end_pos]

    # ४. डायनॅमिक HTML ग्रिड जनरेशन लॉजिक
    def generate_advanced_layout(data_frame, banner_b64, polling_station, layout_type):
        # लेआउटनुसार सेटिंग्ज ठरवणे
        if "१ स्लिप" in layout_type:
            page_size = "A5 portrait"
            grid_css = ".grid-container { display: block; }"
            box_width, box_height, banner_h, font_s = "132mm", "194mm", "115mm", "15px"
            page_padding = "padding: 8mm;"
            items_per_page = 1
        elif "४ स्लिप्स" in layout_type:
            page_size = "A4 portrait"
            grid_css = ".grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }"
            box_width, box_height, banner_h, font_s = "92mm", "135mm", "75mm", "12px"
            page_padding = "padding: 6mm 4mm;"
            items_per_page = 4
        else: # ६ स्लिप्स
            page_size = "A4 portrait"
            grid_css = ".grid-container { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; gap: 3mm; }"
            box_width, box_height, banner_h, font_s = "94mm", "88mm", "42mm", "10.5px"
            page_padding = "padding: 4mm 3mm;"
            items_per_page = 6

        html_content = f"""
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Marathi:wght@400;700&display=swap');
            @media print {{
                body {{ background-color: #ffffff; }}
                .page-sheet {{ page-break-after: always; }}
            }}
            body {{
                font-family: 'Noto Sans Marathi', sans-serif;
                margin: 0;
                padding: 0;
            }}
            .page-sheet {{
                box-sizing: border-box;
                {page_padding}
                margin: 0 auto;
                page-break-inside: avoid;
            }}
            {grid_css}
            .outer-box {{
                width: {box_width};
                height: {box_height};
                border: 1.5mm solid #000000;
                box-sizing: border-box;
                padding: 0px;
                position: relative;
                overflow: hidden;
                background: #fff;
            }}
            .banner-container {{
                width: 100%;
                height: {banner_h};
                overflow: hidden;
                border-bottom: 1px solid #000;
            }}
            .banner-img {{
                width: 100%;
                height: 100%;
                object-fit: fill;
            }}
            .no-banner {{
                width: 100%;
                height: 100%;
                background-color: #f0f4f8;
                text-align: center;
                line-height: {banner_h};
                font-size: 14px;
                font-weight: bold;
                color: #555555;
            }}
            .cut-line-text {{
                text-align: center;
                font-size: 9px;
                color: #444444;
                margin-top: 2px;
                font-weight: bold;
            }}
            .cut-line {{
                border-top: 1.5px dashed #555555;
                margin: 2px 6px 0 6px;
            }}
            .content-container {{
                padding: 6px 12px;
                font-size: {font_s};
                line-height: 1.6;
                color: #000000;
            }}
            .info-row {{
                margin-bottom: 1px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .bold-label {{
                font-weight: 700;
            }}
            .flex-row {{
                width: 100%;
                display: flex;
            }}
            .left-col {{
                width: 52%;
            }}
            .right-col {{
                width: 48%;
            }}
        </style>
        </head>
        <body>
        """
        
        # मतदारांना पानांच्या सेटमध्ये विभागणे
        voter_list = list(data_frame.iterrows())
        for p in range(0, len(voter_list), items_per_page):
            page_voters = voter_list[p:p+items_per_page]
            
            html_content += '<div class="page-sheet"><div class="grid-container">'
            
            for _, row in page_voters:
                voter_no = str(row.get('अनुक्रमांक', row.get('मतदार नं.', row.get('अनु. क्र.', _ + 1))))
                raw_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
                
                clean_name = str(raw_name).replace('सचनि', 'सचिन').replace('दलिीप', 'दिलीप').replace('अभजिीत', 'अभिजीत').replace('गोवदि', 'गोविंद').replace('करिण', 'किरण').replace('अश्वनिी', 'अश्विनी').replace('संदपि', 'संदीप').replace('योगतिा', 'योगिता')
                
                raw_gender = row.get('लिंग', '')
                clean_gender = clean_gender_and_text(raw_gender)
                age = str(row.get('वय', ''))
                
                epic_no = str(row.get('मतदार ओळखपत्र क्र', row.get('मतदार ओळखपत्र क्र.', row.get('मतदार ओळखपत्र क्र. (Voter ID)', ''))))
                house_no = str(row.get('घर क्रमांक', '-'))
                part_no = str(row.get('भाग / सिरीयल क्र.', row.get('भाग / सिरीयल क्र', row.get('यादी भाग क्र.', ''))))
                
                html_content += f"""
                <div class="outer-box">
                    <div class="banner-container">
                """
                if banner_b64:
                    html_content += f'<img src="data:image/jpeg;base64,{banner_b64}" class="banner-img">'
                else:
                    html_content += '<div class="no-banner">[ पॅनेल बॅनर ]</div>'
                    
                html_content += f"""
                    </div>
                    
                    <div class="cut-line-text">--- मतदान केंद्रात जाण्यापूर्वी येथून कापावे ---</div>
                    <div class="cut-line"></div>
                    
                    <div class="content-container">
                        <div class="info-row"><span class="bold-label">मतदार नं. :</span> {voter_no}</div>
                        <div class="info-row"><span class="bold-label">नाव :</span> {clean_name}</div>
                        <div class="info-row"><span class="bold-label">लिंग / वय :</span> {clean_gender} / {age}</div>
                        <div class="info-row"><span class="bold-label">ओळखपत्र क्र. :</span> {epic_no}</div>
                        
                        <div class="flex-row">
                            <div class="left-col"><span class="bold-label">घर नं. :</span> {house_no}</div>
                            <div class="right-col"><span class="bold-label">भाग क्र. :</span> {part_no}</div>
                        </div>
                        
                        <div class="info-row"><span class="bold-label">केंद्र :</span> {polling_station}</div>
                    </div>
                </div>
                """
            
            html_content += '</div></div>' # grid-container & page-sheet शेवट
            
        html_content += "</body></html>"
        return html_content

    banner_base64 = get_image_base64(uploaded_banner)
    final_html = generate_advanced_layout(df_batch, banner_base64, polling_station_input, layout_choice)
    
    st.markdown("---")
    st.subheader("🚀 पायरी ३: निवडलेल्या लेआउटनुसार फाईल डाऊनलोड करा")
    
    printable_html = final_html.replace("<body>", '<body onload="window.print()">')
    
    st.download_button(
        label=f"📥 {layout_choice.split(' ')[0]} लेआउटची फाईल डाऊनलोड करा",
        data=printable_html,
        file_name=f"Balaji_Cyber_Point_MultiLayout_{selected_batch_idx+1}.html",
        mime="text/html",
    )
    
    st.info("💡 **प्रिंटिंग सोपी स्टेप:** डाऊनलोड केलेल्या फाईलवर डबल क्लिक करा, ब्राउझरमध्ये पेज ओपन होताच प्रिंट कमांड सुरू होईल. जर **४ किंवा ६ स्लिप्स** निवडल्या असतील तर प्रिंट सेटिंग्जमध्ये **A4** साईझ निवडा आणि **१ स्लिप** साठी **A5** निवडा!")
