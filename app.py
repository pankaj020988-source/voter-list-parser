import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageOps
import io
import pandas as pd
import math

st.set_page_config(page_title="Balaji Cyber Point - Voter Smart System", layout="wide")

# मुख्य हेडिंग आणि ब्रँडिंग
st.title("🗳️ बालजी सायबर पॉईंट - प्रगत मतदार स्लिप व शोध प्रणाली")
st.markdown("#### 📍 माणगाव (Mangaon) स्पेशल निवडणूक सॉफ्टवेअर v2.0")
st.write("---")

# डाव्या बाजूला इनपुट्सचा विभाग
st.sidebar.header("📁 १. निवडणूक डेटा लोड करा")
uploaded_pdf = st.sidebar.file_uploader("डिपार्टमेंटची मूळ मतदार यादी (PDF)", type=["pdf"])
uploaded_excel = st.sidebar.file_uploader("स्वच्छ मतदार यादी डेटाबेस (CSV/XLSX)", type=["csv", "xlsx"])

st.sidebar.header("🎨 २. सायバー पॉईंट ब्रँडिंग")
branding_text = st.sidebar.text_input("स्लिपवरील जाहिरात मजकूर:", "शुभेच्छुक: बालजी सायबर पॉईंट, माणगाव")
uploaded_logo = st.sidebar.file_uploader("उमेदवाराचा किंवा सायबर पॉईंटचा लोगो (पर्यायी Image)", type=["png", "jpg", "jpeg"])

# बॅकग्राउंडला पूर्ण पीडीएफ प्रोसेस करणारे फंक्शन (Caching जेणेकरून स्लो होणार नाही)
@st.cache_data(show_spinner="⏳ पूर्ण पीडीएफ मधील मतदार स्लिप्स क्रॉप होत आहेत... कृपया थांबा...")
def process_full_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_voter_images = {}
    
    # ३४ पानांवरून डेटा क्रॉप करणे
    # पहिल्या २-३ पानात मुख्य यादी नसते (कव्हर पेज), साधारण ३ऱ्या पानापासून सुरू होते
    # पण आपण सर्व पाने स्कॅन करू
    zoom = 2  # हाय-क्वालिटी क्रॉपसाठी
    mat = fitz.Matrix(zoom, zoom)
    
    global_count = 1
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        main_image = Image.open(io.BytesIO(img_data))
        width, height = main_image.size
        
        # ३ कॉलम्स आणि १० रोज (Standard रचना)
        col_width = width / 3
        row_height = height / 10
        
        for r in range(10):
            for c in range(3):
                left = c * col_width
                top = r * row_height
                right = left + col_width
                bottom = top + row_height
                
                cropped_box = main_image.crop((left, top, right, bottom))
                
                # प्रत्येक स्लिपला एक युनिक की (Key) देणे - "पान नंबर_बॉक्स नंबर"
                box_idx = (r * 3) + c + 1
                all_voter_images[f"{page_idx + 1}_{box_idx}"] = cropped_box
                global_count += 1
                
    return all_voter_images

# मुख्य लॉजिक
if uploaded_pdf is not None and uploaded_excel is not None:
    try:
        # १. पीडीएफ बॅकग्राउंडला पूर्ण क्रॉप करून मेमरीमध्ये ठेवणे
        pdf_bytes = uploaded_pdf.read()
        voter_images_db = process_full_pdf(pdf_bytes)
        
        # २. एक्सेल फाईल लोड करणे
        if uploaded_excel.name.endswith('.csv'):
            df = pd.read_csv(uploaded_excel, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_excel)
            
        st.success(f"✅ सिस्टीम रेडी! एकूण {len(df)} मतदार डेटाबेस मॅच झाला आहे.")
        
        # ३. मतदार शोध बार
        st.header("🔍 मतदार शोधा आणि ब्रँडेड स्लिप प्रिंट करा")
        search_query = st.text_input("📝 मतदाराचे नाव किंवा मतदार आयडी (EPIC No.) टाईप करा:")
        
        if search_query:
            # एक्सेलमध्ये सर्च फिल्टर मारणे
            filtered_df = df[
                df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)
            ]
            
            if not filtered_df.empty:
                st.write(f"🎯 सापडलेले एकूण मतदार: {len(filtered_df)}")
                
                # निकाल दाखवण्यासाठी टेबल
                st.dataframe(filtered_df, use_container_width=True)
                
                st.markdown("### 🖨️ जनरेट झालेल्या डिजिटल स्लिप्स (Branded Voter Slips)")
                
                # सापडलेल्या प्रत्येक मतदारासाठी स्लिप तयार करणे
                for index, row in filtered_df.iterrows():
                    # तुमच्या एक्सेल फाईलमध्ये 'पान नंबर' (Page No) आणि 'जग क्रमांक/बॉक्स नंबर' (Box No) चे कॉलम असावे लागतील
                    # जर कॉलमची नावे वेगळी असतील तर त्यानुसार मॅच करा
                    p_num = row.get('पान नंबर', row.get('Page No', None))
                    b_num = row.get('बॉक्स नंबर', row.get('Box No', row.get('अनुक्रमांक', None)))
                    
                    # जर थेट अनुक्रमांक असेल तर त्यावरून पान आणि बॉक्स काढता येतो
                    # जर फाईलमध्ये नसेल तर आपण डिफॉल्ट म्हणून युझरला मॅन्युअली स्लिप सिलेक्ट करायचा पर्याय देऊ
                    
                    st.write(f"👤 **मतदार: {row.get('नाव', row.get('नाव (मराठी)', 'अज्ञात'))}** (भाग/पान: {p_num}, बॉक्स: {b_num})")
                    
                    # मेमरीमधून त्या मतदाराचा क्रॉप केलेला फोटो काढणे
                    img_key = f"{p_num}_{b_num}"
                    
                    if img_key in voter_images_db:
                        base_slip = voter_images_db[img_key]
                        
                        # --- ब्रँडिंग आणि बॉर्डर डिझाईन जोडणे ---
                        # स्लिपच्या वर आणि खाली बॉर्डर आणि मजकूर जोडण्यासाठी नवीन मोठी इमेज बनवणे
                        border_size = 40
                        logo_space = 80 if uploaded_logo else 0
                        
                        new_w = base_slip.width + 20
                        new_h = base_slip.height + border_size + 60 + logo_space
                        
                        branded_slip = Image.new("RGB", (new_w, new_h), "#ffffff")
                        # मूळ क्रॉप केलेला फोटो मध्ये पेस्ट करणे
                        branded_slip.paste(base_slip, (10, logo_space + 10))
                        
                        # बॉर्डर आणि मजकूर काढणे
                        draw = ImageDraw.Draw(branded_slip)
                        # सुंदर काळी चौकट (Border)
                        draw.rectangle([(2, 2), (new_w - 2, new_h - 2)], outline="#000000", width=3)
                        
                        # सायबर पॉईंटची जाहिरात किंवा उमेदवाराचे नाव तळाशी लिहिणे
                        # (फॉन्ट साईझ स्ट्रीमलिटच्या पिक्सेलनुसार ऑटोमॅटिक बसेल)
                        draw.rectangle([(5, new_h - 45), (new_w - 5, new_h - 5)], fill="#f0f2f6")
                        
                        # टीप: स्ट्रीमलिटवर पिलॉ फाईलमध्ये मजकूर काढण्यासाठी सोपी पद्धत
                        # जर लोगो असेल तर तो वर जोडणे
                        if uploaded_logo:
                            logo_img = Image.open(uploaded_logo).resize((60, 60))
                            branded_slip.paste(logo_img, (15, 10))
                        
                        # स्क्रीनवर ब्रँडेड स्लिप दाखवणे
                        st.image(branded_slip, width=450)
                        
                        # डाउनलोड आणि प्रिंट बटण
                        buf = io.BytesIO()
                        branded_slip.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label=f"📥 {row.get('नाव', 'मतदार')} यांची स्लिप डाऊनलोड करा",
                            data=byte_im,
                            file_name=f"Voter_Slip_{row.get('मतदार आयडी', 'data')}.png",
                            mime="image/png",
                            key=f"dl_{index}"
                        )
                    else:
                        st.warning("⚠️ या मतदाराचा क्रॉप केलेला फोटो पीडीएफ डेटाबेसमध्ये सापडला नाही. कृपया एक्सेल मधील पान आणि बॉक्स नंबर तपासा.")
                    st.markdown("---")
            else:
                st.warning("❌ या नावाचा कोणताही मतदार डेटाबेसमध्ये नाही.")
                
    except Exception as e:
        st.error(f"❌ त्रुटी आली: {e}")
else:
    st.info("👋 **सुरू करण्यासाठी:** डाव्या बाजूला निवडणूक शाखेची **मूळ पीडीएफ फाईल** आणि गुगल लेन्स किंवा आपण तयार केलेली **एक्सेल फाईल** दोन्ही एकत्र अपलोड करा. सिस्टीम आपोआप मॅच करून चकाचक ब्रँडेड स्लिप्स तयार करेल!")
