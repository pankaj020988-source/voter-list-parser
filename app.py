import streamlit as st
import fitz  # PyMuPDF लायब्ररी (पीडीएफ मधून इमेजेस क्रॉप करण्यासाठी)
from PIL import Image
import io

st.set_page_config(page_title="सायबर पॉईंट मतदार क्रॉप प्रणाली", layout="wide")

st.title("🗳️ डिजिटल मतदार यादी बॉक्स क्रॉपर (No Font Error)")
st.markdown("### 📊 Balaji Cyber Point - स्पेशल टूल")
st.write("---")

# डाव्या बाजूला फाईल अपलोडर
st.sidebar.header("📁 मतदार पीडीएफ लोड करा")
uploaded_pdf = st.sidebar.file_uploader("डिपार्टमेंटची मूळ पीडीएफ फाईल निवडा", type=["pdf"])

if uploaded_pdf is not None:
    try:
        # पीडीएफ फाईल वाचणे
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        
        st.success(f"✅ पीडीएफ लोड झाली! एकूण पाने: {total_pages}")
        
        # पान निवडण्यासाठी स्लायडर किंवा इनपुट
        page_num = st.number_input(f"कोणते पान क्रॉप करायचे आहे? (१ ते {total_pages})", min_value=1, max_value=total_pages, value=1)
        
        if st.button("🚀 मतदार स्लिप्स क्रॉप करा (Generate Crop)"):
            # पायथनचे इलेक्शन यादीतील पानाचे कोऑर्डिनेट्स (Coordinates)
            # एका पानावर साधारण ३० बॉक्स असतात (३ कॉलम्स आणि १० रोज)
            page = doc[page_num - 1]
            
            # पानावरील अक्षरे किंवा कचरा न पाहता थेट पूर्ण पानाचा मोठा हाय-क्वालिटी फोटो बनवणे
            zoom = 2  # रिझोल्यूशन वाढवण्यासाठी
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # पिक्समॅपचे पीआयएल इमेजमध्ये रूपांतर
            img_data = pix.tobytes("png")
            main_image = Image.open(io.BytesIO(img_data))
            width, height = main_image.size
            
            st.subheader(f"📸 पान क्र. {page_num} मधील मतदार स्लिप्स:")
            
            # अंदाजे ३ कॉलम्स आणि १० रोज नुसार पानावरील बॉक्स कट करण्याचे लॉजिक
            # (तुमच्या पीडीएफच्या रचनेनुसार हे आकडे आपण नंतर बारीक बदलू शकतो)
            col_width = width / 3
            row_height = height / 10
            
            count = 1
            # स्क्रीनवर दाखवण्यासाठी ३ कॉलम्सचा लेआउट
            grid_cols = st.columns(3)
            
            for r in range(10):
                for c in range(3):
                    # प्रत्येक मतदाराच्या बॉक्सची चौकट (Bounding Box) ठरवणे
                    left = c * col_width
                    top = r * row_height
                    right = left + col_width
                    bottom = top + row_height
                    
                    # इमेज क्रॉप करणे
                    cropped_box = main_image.crop((left, top, right, bottom))
                    
                    # ग्रिडमध्ये स्लिप दाखवणे आणि डाउनलोड बटण देणे
                    col_index = c
                    with grid_cols[col_index]:
                        st.image(cropped_box, caption=f"मतदार क्र. {count}", use_container_width=True)
                        
                        # प्रत्येक स्लिप स्वतंत्र डाउनलोड करण्यासाठी बटण
                        buf = io.BytesIO()
                        cropped_box.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label=f"📥 स्लिप {count} प्रिंट",
                            data=byte_im,
                            file_name=f"voter_slip_{page_num}_{count}.png",
                            mime="image/png",
                            key=f"btn_{r}_{c}"
                        )
                        st.write("---")
                    count += 1
                    
    except Exception as e:
        st.error(f"❌ पीडीएफ क्रॉप करताना त्रुटी आली: {e}")
        st.info("💡 टीप: या टूलसाठी 'PyMuPDF' (fitz) लायब्ररी आवश्यक आहे. ती तुमच्या requirements.txt मध्ये जोडलेली असावी.")
else:
    st.info("👋 सुरू करण्यासाठी डाव्या बाजूला डिपार्टमेंटची मूळ पीडीएफ फाईल अपलोड करा. फॉन्ट खराब असला तरी थेट फोटो कट होऊन मिळतील!")
