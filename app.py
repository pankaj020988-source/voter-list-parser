import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Balaji Cyber Point - Fast Voter System", layout="wide")

st.title("🗳️ बालजी सायबर पॉईंट - सुपर-फास्ट मतदार स्लिप क्रॉपर")
st.markdown("#### 📍 माणगाव (Mangaon) - वेळ वाचवणारी ऑटोमॅटिक सिस्टीम")
st.write("---")

st.sidebar.header("📁 १. मतदार पीडीएफ लोड करा")
uploaded_pdf = st.sidebar.file_uploader("डिपार्टमेंटची मूळ मतदार यादी (PDF)", type=["pdf"])

st.sidebar.header("🎨 २. सायबर पॉईंट ब्रँडिंग")
branding_text = st.sidebar.text_input("स्लिपवरील जाहिरात मजकूर:", "शुभेच्छुक: बालजी सायबर पॉईंट, माणगाव")
uploaded_logo = st.sidebar.file_uploader("उमेदवाराचा लोगो / बॅनर (A5 साठी)", type=["png", "jpg", "jpeg"])

if uploaded_pdf is not None:
    try:
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        
        st.success(f"✅ पीडीएफ लोड झाली! एकूण पाने: {total_pages}")
        
        st.header("📸 प्रभाग यादीचे पान निवडा")
        page_num = st.number_input(f"कोणते पान क्रॉप करायचे आहे? (१ ते {total_pages})", min_value=1, max_value=total_pages, value=3)
        
        if st.button("⚡ झटपट सर्व ३० स्लिप्स A5 मध्ये तयार करा"):
            page = doc[page_num - 1]
            
            # स्पष्ट प्रिंटसाठी ३ पट रिझोल्यूशन
            zoom = 3  
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            main_image = Image.open(io.BytesIO(img_data))
            width, height = main_image.size
            
            st.write("---")
            
            # अचूकता आणि सुरक्षेसाठी गुणोत्तर
            header_offset = height * 0.088  
            footer_offset = height * 0.025  
            usable_height = height - header_offset - footer_offset
            row_height = usable_height / 10  
            col_width = width / 3
            
            count = 1
            grid_cols = st.columns(3)
            
            for r in range(10):
                for c in range(3):
                    # 💡 मूळ भाग: डावीकडे आणि उजवीकडे ५ पिक्सेलची एक्स्ट्रा सेफ जागा ठेवली आहे
                    # जेणेकरून कोणत्याही पानावर काहीही डेटा कट होणार नाही!
                    left = (c * col_width) + 5
                    top = header_offset + (r * row_height) - 4
                    right = (left + col_width) - 10
                    bottom = top + row_height + 12
                    
                    base_slip = main_image.crop((left, top, right, bottom))
                    
                    # A5 आकाराची परफेक्ट रुंदी (Target Width)
                    target_width = 800
                    scale_percent = target_width / base_slip.width
                    new_box_h = int(base_slip.height * scale_percent)
                    resized_base = base_slip.resize((target_width - 40, new_box_h), Image.Resampling.LANCZOS)
                    
                    logo_space = 200 if uploaded_logo else 40
                    footer_space = 100
                    
                    a5_h = resized_base.height + logo_space + footer_space + 60
                    a5_slip = Image.new("RGB", (target_width, a5_h), "#ffffff")
                    
                    # १. वर उमेदवाराचा मोठा लोगो बसवणे
                    if uploaded_logo:
                        logo_img = Image.open(uploaded_logo)
                        logo_w_percent = (target_width - 40) / logo_img.width
                        logo_h = int(logo_img.height * logo_w_percent)
                        if logo_h > 180:
                            logo_h = 180
                        resized_logo = logo_img.resize((target_width - 40, logo_h), Image.Resampling.LANCZOS)
                        a5_slip.paste(resized_logo, (20, 20))
                    
                    # २. क्रॉप केलेला डेटा मध्यभागी सुरक्षित पेस्ट करणे
                    a5_slip.paste(resized_base, (20, logo_space + 20))
                    
                    # ३. कडक आणि प्रोफेशनल आऊटर बॉर्डर
                    draw = ImageDraw.Draw(a5_slip)
                    draw.rectangle([(4, 4), (target_width - 4, a5_h - 4)], outline="#000000", width=5)
                    draw.line([(20, logo_space + 10), (target_width - 20, logo_space + 10)], fill="#000000", width=3)
                    draw.line([(20, logo_space + 30 + resized_base.height), (target_width - 20, logo_space + 30 + resized_base.height)], fill="#000000", width=3)
                    
                    # तळाशी जाहिरात बॅकग्राउंड
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
                            label=f"🖨️ प्रिंट स्लिप {count}",
                            data=byte_im,
                            file_name=f"Voter_Slip_{count}.png",
                            mime="image/png",
                            key=f"btn_{page_num}_{r}_{c}"
                        )
                    count += 1
                    
    except Exception as e:
        st.error(f"❌ त्रुटी आली: {e}")
else:
    st.info("👋 **बालाजी सायबर पॉईंट:** सुरू करण्यासाठी डाव्या बाजूला प्रभाग पीडीएफ अपलोड करा.")
