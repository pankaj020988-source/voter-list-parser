import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Balaji Cyber Point - Voter Smart System", layout="wide")

# मुख्य हेडिंग आणि ब्रँडिंग
st.title("🗳️ बालजी सायबर पॉईंट - प्रगत मतदार स्लिप क्रॉपर")
st.markdown("#### 📍 माणगाव (Mangaon) स्पेशल निवडणूक सॉफ्टवेअर (Manual Page Mode)")
st.write("---")

# डाव्या बाजूला इनपुट्सचा विभाग
st.sidebar.header("📁 १. मतदार पीडीएफ लोड करा")
uploaded_pdf = st.sidebar.file_uploader("डिपार्टमेंटची मूळ मतदार यादी (PDF)", type=["pdf"])

st.sidebar.header("🎨 २. सायबर पॉईंट ब्रँडिंग")
branding_text = st.sidebar.text_input("स्लिपवरील जाहिरात मजकूर:", "शुभेच्छुक: बालजी सायबर पॉईंट, माणगाव")
uploaded_logo = st.sidebar.file_uploader("उमेदवाराचा किंवा सायबर पॉईंटचा लोगो (पर्यायी)", type=["png", "jpg", "jpeg"])

if uploaded_pdf is not None:
    try:
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        
        st.success(f"✅ पीडीएफ यशस्वीरित्या लोड झाली! एकूण पाने: {total_pages}")
        
        # पान निवडण्यासाठी इनपुट बॉक्स
        st.header("📸 प्रभाग यादीचे पान निवडा")
        page_num = st.number_input(f"कोणते पान क्रॉप करायचे आहे? (१ ते {total_pages})", min_value=1, max_value=total_pages, value=3)
        
        if st.button("🚀 या पानावरील सर्व ३० स्लिप्स क्रॉप करा"):
            page = doc[page_num - 1]
            
            # हाय-क्वालिटी क्रॉपसाठी रिझोल्यूशन २ पट वाढवणे
            zoom = 2  
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            main_image = Image.open(io.BytesIO(img_data))
            width, height = main_image.size
            
            st.write("---")
            st.subheader(f"🎯 पान क्र. {page_num} मधील सर्व मतदार स्लिप्स:")
            
            # --- सुधारित अचूक गुणोत्तर आणि मापे ---
            # पानावरील हेडिंग (Header) आणि तळ (Footer) अचूकपणे वजा करणे
            header_offset = height * 0.088  # पहिल्या ओळीच्या वरचे हेडिंग पूर्णपणे सोडण्यासाठी (८.८%)
            footer_offset = height * 0.025  # खालचा प्रभाग मजकूर सोडण्यासाठी
            
            usable_height = height - header_offset - footer_offset
            row_height = usable_height / 10  # प्रत्येक बॉक्सची परफेक्ट उंची
            col_width = width / 3
            
            count = 1
            # ३ कॉलम्सचा ग्रिड लेआउट
            grid_cols = st.columns(3)
            
            for r in range(10):
                for c in range(3):
                    # प्रत्येक बॉक्सचे अचूक डावे, उजवे, वरचे आणि खालचे माप
                    left = c * col_width
                    top = header_offset + (r * row_height)
                    right = left + col_width
                    bottom = top + row_height
                    
                    # मूळ मतदार चौकट अचूकपणे क्रॉप करणे
                    base_slip = main_image.crop((left + 8, top + 2, right - 8, bottom - 2))
                    
                    # --- सुंदर स्लिप कार्ड डिझाईन (ब्रँडिंग स्पेस) ---
                    logo_space = 75 if uploaded_logo else 0
                    footer_space = 35
                    
                    new_w = base_slip.width + 16
                    new_h = base_slip.height + logo_space + footer_space + 15
                    
                    # नवीन पांढरी स्लिप बॅकग्राउंड तयार करणे
                    branded_slip = Image.new("RGB", (new_w, new_h), "#ffffff")
                    # मूळ क्रॉप केलेला मतदार बॉक्स मध्यभागी पेस्ट करणे
                    branded_slip.paste(base_slip, (8, logo_space + 8))
                    
                    draw = ImageDraw.Draw(branded_slip)
                    
                    # कार्डची बाहेरील आकर्षक काळी बॉर्डर
                    draw.rectangle([(2, 2), (new_w - 2, new_h - 2)], outline="#000000", width=3)
                    
                    # तळाशी जाहिरातीसाठी सुंदर पट्टी
                    draw.rectangle([(4, new_h - footer_space - 4), (new_w - 4, new_h - 4)], fill="#f1f3f6")
                    
                    # लोगो असल्यास डाव्या कोपऱ्यात वर पेस्ट करणे
                    if uploaded_logo:
                        logo_img = Image.open(uploaded_logo).resize((65, 65))
                        branded_slip.paste(logo_img, (12, 8))
                    
                    # ग्रिडमध्ये स्लिप दाखवणे
                    col_index = c
                    with grid_cols[col_index]:
                        st.image(branded_slip, caption=f"मतदार स्लिप क्र. {count}", use_container_width=True)
                        
                        # इमेज डाऊनलोड करण्यासाठी मेमरी तयार करणे
                        buf = io.BytesIO()
                        branded_slip.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label=f"🖨️ स्लिप {count} प्रिंट",
                            data=byte_im,
                            file_name=f"Voter_Slip_Page{page_num}_No{count}.png",
                            mime="image/png",
                            key=f"btn_{page_num}_{r}_{c}"
                        )
                        st.write("---")
                    count += 1
                    
    except Exception as e:
        st.error(f"❌ त्रुटी आली: {e}")
else:
    st.info("👋 **बालजी सायबर पॉईंट:** सुरू करण्यासाठी डाव्या बाजूला डिपार्टमेंटची मूळ पीडीएफ फाईल अपलोड करा.")
