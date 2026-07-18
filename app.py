import streamlit as st
import pandas as pd
import base64
import re

# Professional Corporate Page Setup
st.set_page_config(page_title="Balaji Cyber Point | Voter Slip System Pro", layout="wide")

st.markdown("<h2 style='text-align: center; color: #1E3A8A; font-family: sans-serif; margin-bottom: 25px;'>VOTER SLIP SYSTEM PRO</h2>", unsafe_allow_html=True)

# 1. Professional Control Panel (Sidebar)
st.sidebar.markdown("<h3 style='color: #1E3A8A; font-family: sans-serif;'>CONFIGURATION</h3>", unsafe_allow_html=True)
uploaded_banner = st.sidebar.file_uploader("Upload Panel Banner (JPG/PNG)", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("Polling Station Name", "ज. प. प्रा. शाळा")

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: #1E3A8A; font-family: sans-serif;'>PRINT LAYOUT</h3>", unsafe_allow_html=True)
layout_choice = st.sidebar.radio(
    "Select Sheets Configuration:",
    [
        "A5 Paper Layout (1 Slip per Page)", 
        "A5 Paper Layout (2 Slips per Page)", 
        "A4 Paper Layout (4 Slips per Page)", 
        "A4 Paper Layout (6 Slips per Page)"
    ]
)

# 2. Clean Data Upload Area
st.markdown("<h4 style='color: #374151; font-family: sans-serif;'>1. Import Voter Database</h4>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose Excel File (.xlsx)", type=["xlsx"], label_visibility="collapsed")

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
    st.success(f"Database Synchronized successfully. Total Records Indexed: {total_rows}")
    
    # 3. Dynamic HTML Layout Engine (Retains 100% Pure Marathi Data Internally)
    def generate_advanced_layout(data_frame, banner_b64, polling_station, layout_type):
        if "1 Slip" in layout_type:
            grid_css = ".grid-container { display: block; }"
            box_width, box_height, banner_h, font_s = "132mm", "194mm", "115mm", "15px"
            page_padding = "padding: 8mm;"
            items_per_page = 1
            wrapper_style = ""
        elif "2 Slips" in layout_type:
            grid_css = ".grid-container { display: grid; grid-template-columns: 1fr; gap: 6mm; background-image: linear-gradient(to right, #000 33%, rgba(255,255,255,0) 0%); background-position: center 103mm; background-size: 8px 1.5px; background-repeat: repeat-x; }"
            box_width, box_height, banner_h, font_s = "134mm", "94mm", "48mm", "11px"
            page_padding = "padding: 5mm 7mm;"
            items_per_page = 2
            wrapper_style = ""
        elif "4 Slips" in layout_type:
            grid_css = """
                .grid-container { 
                    display: grid; 
                    grid-template-columns: 1fr 1fr; 
                    gap: 8mm; 
                    position: relative;
                }
                .grid-container::before {
                    content: "";
                    position: absolute;
                    left: 50%;
                    top: 0;
                    bottom: 0;
                    border-left: 1.5px dashed #000000;
                    transform: translateX(-50%);
                }
                .grid-container::after {
                    content: "";
                    position: absolute;
                    top: 50%;
                    left: 0;
                    right: 0;
                    border-top: 1.5px dashed #000000;
                    transform: translateY(-50%);
                }
            """
            box_width, box_height, banner_h, font_s = "92mm", "135mm", "75mm", "12px"
            page_padding = "padding: 6mm 4mm;"
            items_per_page = 4
            wrapper_style = ""
        else: 
            grid_css = """
                .grid-container { 
                    display: grid; 
                    grid-template-columns: 1fr 1fr; 
                    grid-template-rows: 1fr 1fr 1fr; 
                    gap: 6mm;
                    position: relative;
                }
                .grid-container::before {
                    content: "";
                    position: absolute;
                    left: 50%;
                    top: 0;
                    bottom: 0;
                    border-left: 1.5px dashed #000000;
                    transform: translateX(-50%);
                }
                .grid-container::after {
                    content: "";
                    position: absolute;
                    top: 33.33%;
                    left: 0;
                    right: 0;
                    border-top: 1.5px dashed #000000;
                }
                .grid-container-horizontal-2 {
                    position: absolute;
                    top: 66.66%;
                    left: 0;
                    right: 0;
                    border-top: 1.5px dashed #000000;
                }
            """
            box_width, box_height, banner_h, font_s = "94mm", "88mm", "42mm", "10.5px"
            page_padding = "padding: 4mm 3mm;"
            items_per_page = 6
            wrapper_style = ""

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
                border: 1.5mm solid #000000 !important;
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
            {wrapper_style}
        </style>
        </head>
        <body>
        """
        
        voter_list = list(data_frame.iterrows())
        for p in range(0, len(voter_list), items_per_page):
            page_voters = voter_list[p:p+items_per_page]
            
            html_content += '<div class="page-sheet"><div class="grid-container">'
            
            if "6 Slips" in layout_type:
                html_content += '<div class="grid-container-horizontal-2"></div>'
            
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
                    html_content += '<div class="no-banner">[ PANEL BANNER ]</div>'
                    
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
            
            html_content += '</div></div>'
            
        html_content += "</body></html>"
        return html_content

    banner_base64 = get_image_base64(uploaded_banner)
    final_html = generate_advanced_layout(df, banner_base64, polling_station_input, layout_choice)
    
    # 4. English Corporate Output Actions
    st.markdown("---")
    st.markdown("<h4 style='color: #374151; font-family: sans-serif;'>2. Export Compilation</h4>", unsafe_allow_html=True)
    
    printable_html = final_html.replace("<body>", '<body onload="window.print()">')
    
    st.download_button(
        label=f"📥 DOWNLOAD ALL {total_rows} VOTER SLIPS (PDF/HTML)",
        data=printable_html,
        file_name=f"Voter_Slips_Master_Compilation.html",
        mime="text/html",
        use_container_width=True
    )
    
    st.info("System Instruction: Clicking the download button saves the production build. Opening the downloaded asset instantly initializes the default system print dialog box. Ensure appropriate margins and targets are configured before printing.")
