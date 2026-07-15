import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Balaji Cyber Point - A5 Voter System", layout="wide")

# मुख्य हेडिंग आणि ब्रँडिंग
st.title("🗳️ बालजी सायबर पॉईंट - A5 स्पेशल मतदार स्लिप क्रॉपर")
st.markdown("#### 📍 माणगाव (Mangaon) - थेट A5 पेजवर परफेक्ट प्रिंटिंग सिस्टीम")
st.write("---")

# डाव्या बाजूला इनपुट्सचा विभाग
st.sidebar.header("📁 १. मतदार पीडीएफ लोड करा")
uploaded_pdf = st.sidebar.file_uploader("डिपार्टमेंटची मूळ मतदार यादी (PDF)", type=["pdf"])

st.sidebar.header("🎨 २. सायबर पॉईंट ब्रँडिंग")
branding_text = st.sidebar.text_input("स्लिपवरील जाहिरात मजकूर:", "शुभेच्छुक: बालजी सायबर पॉईंट, माणगाव")
uploaded_logo = st.sidebar.file_uploader("उमेदवाराचा किंवा सायबर पॉईंटचा लोगो/बॅनर (A5 साठी)", type=["png", "jpg", "jpeg"])

if uploaded_pdf is not None:
    try:
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        
        st.success(f"✅ पीडीएफ यशस्वीरित्या लोड झाली! एकूण पाने: {total_pages}")
        
        # पान निवडण्यासाठी इनपुट बॉक्स
        st.header("📸 प्रभाग यादीचे पान निवडा")
        page_num = st.number_input(f"कोणते पान क्रॉप करायचे आहे? (१ ते {total_pages})", min_value=1, max_value=total_pages, value=3)
        
        if st.button("🚀 या पानावरील सर्व ३० स्लिप्स A5 साईझमध्ये क्रॉप करा"):
            page = doc[page_num - 1]
            
            # हाय-क्वालिटी क्रॉपसाठी रिझोल्यूशन ३ पट वाढवणे
            zoom = 3  
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            main_image = Image.open(io.BytesIO(img_data))
            width, height = main_image.size
            
            st.write("---")
            st.subheader(f"🎯 पान क्र. {page_num} मधील सर्व मतदार स्लिप्स (कॉलम-वाईज परफेक्ट फिक्स):")
            
            # पानावरील हेडिंग आणि तळ अचूकपणे वजा करणे
            header_offset = height * 0.088  
            footer_offset = height * 0.025  
            
            usable_height = height - header_offset - footer_offset
            row_height = usable_height / 10  
            
            count = 1
            # ३ कॉलम्सचा ग्रिड लेआउट
            grid_cols = st.columns(3)
            
            for r in range(10):
                for c in range(3):
                    top = header_offset + (r * row_height)
                    bottom = top + row_height
                    
                    # 💡 बदल: दुसऱ्या कॉलमला उजवीकडून २% मागे सरकवले (0.660 वरून 0.654 केले) जेणेकरून ३ऱ्या स्लिपचा कचरा २ऱ्यात येणार नाही!
                    if c == 0:    # पहिली स्लिप (कॉलम १)
                        crop_left = width * 0.018
                        crop_right = width * 0.336
                    elif c == 1:  # दुसरी स्लिप (कॉलम २)
                        crop_left = width * 0.336
                        crop_right = width * 0.654
                    else:         # तिसरी स्लिप (कॉलम ३)
                        crop_left = width * 0.656
                        crop_right = width * 0.980
                        
                    # मूळ मतदार चौकट अचूकपणे क्रॉप करणे
                    base_slip = main_image.crop((crop_left, top + 6, crop_right, bottom - 6))
                    
                    # --- A5 पेज गुणोत्तरानुसार रचना ---
                    target_width = 800
                    
                    # मूळ क्रॉप केलेल्या माहितीचा आकार वाढवणे
                    scale_percent = target_width / base_slip.width
                    new_box_h = int(base_slip.height * scale_percent)
                    resized_base = base_slip.resize((target_width - 40, new_box_h), Image.Resampling.LANCZOS)
                    
                    # लोगो आणि जाहिरातीसाठी जागा देणे
                    logo_space = 200 if uploaded_logo else 40
                    footer_space = 100
                    
                    a5_h = resized_base.height + logo_space + footer_space + 60
                    
                    # नवीन A5 आकाराचे पांढरे कार्ड बनवणे
                    a5_slip = Image.new("RGB", (target_width, a5_h), "#ffffff")
                    
                    # १. लोगो/बॅनर वरती पेस्ट करणे
                    if uploaded_logo:
                        logo_img = Image.open(uploaded_logo)
                        logo_w_percent = (target_width - 40) / logo_img.width
                        logo_h = int(logo_img.height * logo_w_percent)
                        if logo_h > 180:
                            logo_h = 180
                        resized_logo = logo_img.resize((target_width - 40, logo_h), Image.Resampling.LANCZOS)
                        a5_slip.paste(resized_logo, (20, 20))
                    
                    # २. आतील पांढरा मतदार माहितीचा बॉक्स मध्यभागी पेस्ट करणे
                    a5_slip.paste(resized_base, (20, logo_space + 20))
                    
                    # ३. नवीन सुंदर काळी चौकट आखणे
                    draw = ImageDraw.Draw(a5_slip)
                    draw.rectangle([(4, 4), (target_width - 4, a5_h - 4)], outline="#000000", width=5)
                    
                    # मतदार बॉक्सच्या वर आणि खाली स्पष्ट रेषा
                    draw.line([(20, logo_space + 10), (target_width - 20, logo_space + 10)], fill="#000000", width=3)
                    draw.line([(20, logo_space + 30 + resized_base.height), (target_width - 20, logo_space + 30 + resized_base.height)], fill="#000000", width=3)
                    
                    # जाहिरातीसाठी तळाशी पट्टी
                    draw.rectangle([(10, a5_h - footer_space - 10), (target_width - 10, a5_h - 10)], fill="#f8f9fa")
                    
                    # ग्रिडमध्ये स्लिप दाखवणे
                    col_index = c
                    with grid_cols[col_index]:
                        st.markdown(f"📊 **मतदार क्र. {count} (Perfect Margin)**")
                        st.image(a5_slip, use_container_width=True)
                        st.info(f"📣 {branding_text}")
                        
                        buf = io.BytesIO()
                        a5_slip.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label=f"🖨️ A5 स्लिप {count} प्रिंट",
                            data=byte_im,
                            file_name=f"A5_Perfect_Slip_{count}.png",
                            mime="image/png",
                            key=f"btn_a5_{page_num}_{r}_{c}"
                        )
                        st.write("---")
                    count += 1
                    
    except Exception as e:
        st.error(f"❌ त्रुटी आली: {e}")
else:
    st.info("👋 **बालाजी सायबर पॉईंट:** सुरू करण्यासाठी डाव्या बाजूला प्रभाग पीडीएफ अपलोड करा.")
