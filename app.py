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
            st.subheader(f"🎯 पान क्र. {page_num} मधील सर्व मतदार स्लिप्स (अचूक मापांसह):")
            
            # पानावरील हेडिंग सोडण्यासाठी अचूक गॅप (६% वरून आणि १% खालून)
            header_offset = height * 0.06  
            footer_offset = height * 0.01  
            
            # स्लिपची उंची खाली वाढवण्यासाठी usable_height मध्ये बदल करून +८ पिक्सेल वाढवले आहेत
            usable_height = height - header_offset - footer_offset
            row_height = (usable_height / 10) + 8  
            col_width = width / 3
            
            count = 1
            # ३ कॉलम्सचा ग्रिड लेआउट
            grid_cols = st.columns(3)
            
            for r in range(10):
                for c in range(3):
                    # प्रत्येक बॉक्सचे अचूक डावे, उजवे, वरचे आणि खालचे माप
                    left = c * col_width
                    top = header_offset + (r * (row_height - 8)) # मूळ रो स्पेसिंग मेंटेन करण्यासाठी
                    right = left + col_width
                    bottom = top + row_height
                    
                    # अचूक मापाने बॉक्स क्रॉप करणे (आता वय, लिंग आणि घर क्रमांक कट होणार नाही)
                    base_slip = main_image.crop((left + 5, top + 2, right - 5, bottom - 2))
                    
                    # --- ब्रँडिंग स्पेस जोडणे ---
                    border_size = 40
                    logo_space = 60 if uploaded_logo else 0
                    
                    new_w = base_slip.width + 20
                    new_h = base_slip.height + border_size + 40 + logo_space
                    
                    # नवीन पांढरी स्लिप बॅकग्राउंड तयार करणे
                    branded_slip = Image.new("RGB", (new_w, new_h), "#ffffff")
                    branded_slip.paste(base_slip, (10, logo_space + 10))
                    
                    draw = ImageDraw.Draw(branded_slip)
                    # काळी बॉर्डर
                    draw.rectangle([(2, 2), (new_w - 2, new_h - 2)], outline="#000000", width=3)
                    
                    # तळाशी फिक्कट पट्टी (जाहिरातीसाठी)
                    draw.rectangle([(5, new_h - 35), (new_w - 5, new_h - 5)], fill="#f0f2f6")
                    
                    # लोगो असल्यास वर पेस्ट करणे
                    if uploaded_logo:
                        logo_img = Image.open(uploaded_logo).resize((50, 50))
                        branded_slip.paste(logo_img, (15, 10))
                    
                    # ग्रिडमध्ये स्लिप दाखवणे
                    col_index = c
                    with grid_cols[col_index]:
                        st.image(branded_slip, caption=f"स्लिप क्र. {count} (पान {page_num})", use_container_width=True)
                        
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
