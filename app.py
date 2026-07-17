import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import urllib.request

st.set_page_config(page_title="Voter Slip Generator", layout="wide")

st.title("🖨️ पॅनेल मतदार स्लिप जनरेटर (A4 - 2 Column Layout)")

# १. पॅनेल बॅनर आणि सेटिंग्ज
st.sidebar.header("⚙️ पॅनेल कॉन्फिगरेशन")
uploaded_banner = st.sidebar.file_uploader("१. पॅनेलचा बॅनर इमेज अपलोड करा", type=["jpg", "jpeg", "png"])
polling_station_input = st.sidebar.text_input("२. मतदान केंद्राचे नाव (सर्व स्लिप्ससाठी समान असल्यास)", "ज. प. प्रा. शाळा")

# २. एक्सेल फाईल अपलोड
st.subheader("📊 मतदार एक्सेल फाईल अपलोड करा")
uploaded_file = st.file_uploader("तुमची पार्स केलेली एक्सेल फाईल (.xlsx) इथे अपलोड करा", type=["xlsx"])

# मराठी फॉन्ट डाउनलोड आणि रजिस्टर करण्याचे फंक्शन (जेणेकरून पीडीएफ मध्ये मराठी नावे व्यवस्थित दिसतील)
@st.cache_resource
def register_marathi_font():
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
        font_data = urllib.request.urlopen(font_url).read()
        font_io = io.BytesIO(font_data)
        pdfmetrics.registerFont(TTFont('NotoSans', font_io))
        return 'NotoSans'
    except Exception as e:
        # काही अडचण आल्यास डीफॉल्ट फॉन्ट वापरेल
        return 'Helvetica'

font_name = register_marathi_font()

if uploaded_file is not None:
    # एक्सेल डेटा लोड करणे
    df = pd.read_excel(uploaded_file)
    st.success("✅ एक्सेल फाईल यशस्वीरित्या लोड झाली!")
    st.write("### मतदार डेटा प्रीव्ह्यू (पहिले ५ रेकॉर्ड्स)", df.head())

    # PDF जनरेशन लॉजिक
    def generate_slips_pdf(data_frame, banner_bytes, polling_station):
        buffer = io.BytesIO()
        # A4/Letter साईझ आणि गॅप्स मॅनेजमेंट
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        story = []
        
        styles = getSampleStyleSheet()
        
        # मराठी मजकुरासाठी स्टाईल
        marathi_style = ParagraphStyle(
            'MarathiStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.black
        )
        
        # कापावे रेषेसाठी स्टाईल
        cut_style = ParagraphStyle(
            'CutStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            leading=10,
            alignment=1, # Center
            textColor=colors.dimgrey
        )
        
        slips_list = []
        current_row = []
        
        for index, row in data_frame.iterrows():
            slip_content = []
            
            # १. पॅनेल बॅनर ॲड करणे
            if banner_bytes:
                banner_img = Image(io.BytesIO(banner_bytes), width=250, height=65)
                slip_content.append(banner_img)
            else:
                slip_content.append(Paragraph("<b><font color='red'>[इथे तुमचा पॅनेल बॅनर दिसेल]</font></b>", marathi_style))
            
            slip_content.append(Spacer(1, 3))
            slip_content.append(Paragraph("----------------- मतदान केंद्रात जाण्यापूर्वी येथून कापावे -----------------", cut_style))
            slip_content.append(Spacer(1, 5))
            
            # २. एक्सेल मधील कॉलमची नावे मॅप करणे
            voter_no = row.get('अनुक्रमांक', row.get('मतदार नं.', index + 1))
            voter_name = row.get('मतदाराचे पूर्ण नांव', row.get('नाव', row.get('मतदाराचे पूर्ण नाव', '')))
            gender = row.get('लिंग', '')
            age = row.get('वय', '')
            epic_no = row.get('मतदार ओळखपत्र क्र. (Voter ID)', row.get('मतदार ओळखपत्र क्र.', ''))
            house_no = row.get('घर क्रमांक', '-')
            part_no = row.get('भाग / सिरीयल क्र.', row.get('यादी भाग क्र.', ''))
            
            # ३. स्लिपचा मजकूर फॉरमॅटिंग (तुमच्या प्रतिमेप्रमाणे)
            info_html = f"""
            <b>मतदार नं. :</b> {voter_no} <br/>
            <b>नाव :</b> {voter_name} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{gender}/{age}</b><br/>
            <b>ओळखपत्र क्र. :</b> {epic_no} <br/>
            <b>घर क्रमांक :</b> {house_no} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>भाग नं:</b> {part_no}<br/>
            <b>मतदान केंद्र :</b> {polling_station}
            """
            
            slip_content.append(Paragraph(info_html, marathi_style))
            
            # २ Column ग्रीड मॅनेजमेंट
            current_row.append(slip_content)
            if len(current_row) == 2:
                slips_list.append(current_row)
                current_row = []
                
        # शिल्लक राहिलेला शेवटचा बॉक्स हाताळणे
        if current_row:
            current_row.append([])
            slips_list.append(current_row)
            
        # टेबल लेआउट आणि बॉर्डर्स (कापण्यासाठी आउटलाईन)
        slip_table = Table(slips_list, colWidths=[275, 275])
        slip_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.grey),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        
        story.append(slip_table)
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # ३. पीडीएफ जनरेट आणि डाऊनलोड बटन
    st.markdown("---")
    if st.button("🚀 सर्व ५९० मतदारांच्या स्लिप्स तयार करा"):
        banner_data = uploaded_banner.read() if uploaded_banner else None
        
        with st.spinner("तुमच्या पॅनेलच्या स्लिप्स पीडीएफ मध्ये तयार होत आहेत..."):
            pdf_out = generate_slips_pdf(df, banner_data, polling_station_input)
            
            st.success("🎉 स्लिप्स तयार झाल्या आहेत! खालील बटनावर क्लिक करून डाऊनलोड करा.")
            st.download_button(
                label="📥 मतदार स्लिप्स (PDF) डाऊनलोड करा",
                data=pdf_out,
                file_name="Panel_Voter_Slips.pdf",
                mime="application/pdf"
            )
