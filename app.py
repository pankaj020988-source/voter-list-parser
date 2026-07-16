import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Balaji Cyber Point - Smart Voter Crop", layout="wide")

# मुख्य हेडिंग आणि ब्रँडिंग
st.title("🗳️ बालजी सायबर पॉईंट - प्रगत मतदार स्लिप क्रॉपर (Manual Fix)")
st.markdown("#### 📍 माणगाव (Mangaon) - थेट A5 पेजवर परफेक्ट प्रिंटिंग सिस्टीम")
st.write("---")

# डाव्या बाजूला इनपुट्सचा विभाग
st.sidebar.header("📁 १. मतदार पीडीएफ लोड करा")
uploaded_pdf = st.sidebar.file_uploader("डिपार्टमेंटची मूळ मतदार यादी (PDF)", type=["pdf"])

st.sidebar.header("🎨 २. सायबर पॉईंट ब्रँडिंग")
branding_text = st.sidebar.text_input("स्लिपवरील जाहिरात मजकूर:", "शुभेच्छुक: बालजी सायबर पॉईंट, माणगाव")
uploaded_logo = st.sidebar.file_uploader("logo", type=["png", "jpg", "jpeg"])

# 💡 ३. नवीन मॅन्युअल कंट्रोल पॅनेल (स्लिप्स मॅन्युअली वर-खाली सरकवण्यासाठी)
st.sidebar.header("🛠️ ३. क्रॉपिंग ॲडजस्टमेंट (मॅन्युअल)")
st.sidebar.info("खालील कंट्रोल्स वापरून स्लिप्स वर-खाली किंवा डावीकडे सरकवा, स्क्रीनवर लाईव्ह बदल दिसेल.")

fine_top = st.sidebar.slider("वरचा भाग कापा (Top Trim):", min_value=-30, max_value=30, value=2)
fine_bottom = st.sidebar.slider("खालचा भाग कापा (Bottom Trim):", min_value=-30, max_value=30, value=5)
fine_left = st.sidebar.slider("डावा भाग कापा (Left Trim):", min_value=-20, max_value=20, value=0)
fine_right = st.sidebar.slider("उजवा भाग कापा (Right Trim):", min_value=-20, max_value=20, value=0)

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
            st.subheader(f"🎯 पान क्र. {page_num} मधील सर्व मतदार स्लिप्स (कंट्रोल मोड चालू):")
            
            # पानावरील हेडिंग आणि तळ वजा करणे
            header_offset = height * 0.088  
            footer_offset = height * 0.025  
            usable_height = height - header_offset - footer_offset
            
            row_height = (usable_height / 10) + 8  
            
            count = 1
            grid_cols = st.columns(3)
            
            for r in range(10):
                top = header_offset + (r * (row_height - 8))
                bottom = top + row_height
                
                for c in range(3):
                    # कॉलम वाईज मूळ फिक्स विड्थ मोजणे
                    if c == 0:
                        crop_left = (width * 0.018) + fine_left
                        crop_right = (width * 0.336) + fine_right
                    elif c == 1:
                        crop_left = (width * 0.336) + fine_left
                        crop_right = (width * 0.654) + fine_right
                    else:
                        crop_left = (width * 0.656) + fine_left
                        crop_right = (width * 0.980) + fine_right
                        
                    # 💡 मॅन्युअल कंट्रोल्स (fine_top आणि fine_bottom) मूळ मापात लागू करणे
                    base_slip = main_image.crop((crop_left, top - fine_top, crop_right, bottom + fine_bottom))
                    
                    # --- A5 पेज गुणोत्तरानुसार रचना ---
                    target_width = 800
                    scale_percent = target_width / base_slip.width
                    new_box_h = int(base_slip.height * scale_percent)
                    resized_base = base_slip.resize((target_width - 40, new_box_h), Image.Resampling.LANCZOS)
                    
                    logo_space = 200 if uploaded_logo else 40
                    footer_space = 100
                    
                    a5_h = resized_base.height + logo_space + footer_space + 60
                    a5_slip = Image.new("RGB", (target_width, a5_h), "#ffffff")
                    
                    # लोगो पेस्ट करणे
                    if uploaded_logo:
                        logo_img = Image.open(uploaded_logo)
                        logo_w_percent = (target_width - 40) / logo_img.width
                        logo_h = int(logo_img.height * logo_w_percent)
                        if logo_h > 180:
                            logo_h = 180
                        resized_logo = logo_img.resize((target_width - 40, logo_h), Image.Resampling.LANCZOS)
                        a5_slip.paste(resized_logo, (20, 20))
                    
                    # मतदार माहिती पेस्ट करणे
                    a5_slip.paste(resized_base, (20, logo_space + 20))
                    
                    # चौकट आखणे
                    draw = ImageDraw.Draw(a5_slip)
                    draw.rectangle([(4, 4), (target_width - 4, a5_h - 4)], outline="#000000", width=5)
                    draw.line([(20, logo_space + 10), (target_width - 20, logo_space + 10)], fill="#000000", width=3)
                    draw.line([(20, logo_space + 30 + resized_base.height), (target_width - 20, logo_space + 30 + resized_base.height)], fill="#000000", width=3)
                    
                    draw.rectangle([(10, a5_h - footer_space - 10), (target_width - 10, a5_h - 10)], fill="#f8f9fa")
                    
                    col_index = c
                    with grid_cols[col_index]:
                        st.markdown(f"📊 **मतदार क्र. {count}**")
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
