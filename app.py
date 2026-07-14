import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import re
import pandas as pd
import os

st.set_page_config(page_title="सुपर-फास्ट मतदार यादी स्कॅनर", layout="wide")
st.title("📊 डिजिटल मतदार यादी कन्व्हर्टर (Ultra Fast Cloud OCR)")

uploaded_file = st.file_uploader("प्रभागाची PDF फाईल इथे अपलोड करा", type=["pdf"])

def clean_name(name):
    if not name: 
        return ""
    # कचरा शब्द आणि चिन्हे साफ करणे
    cleaned = re.sub(r'[A-Za-z0-9\s§\|•\*■\+\[\]\(\)\-\./_\\\?€>;:ः]+', ' ', name)
    cleaned = re.sub(r'^(मतदाराचे पूर्ण नाव|मतदाराचे पूर्ण|पुर्ण नाव|नाव|नांव|तदाराचे पूर्ण)[:\s]*', '', cleaned).strip()
    
    # नावापुढचा 'म' किंवा कचरा काढणे
    junk_suffixes = [r'\s+मः$', r'\s+मत्‌$', r'\s+मत्$', r'\s+मत$', r'\s+म$', r'\s+मर्‌$']
    for suffix in junk_suffixes:
        cleaned = re.sub(suffix, '', cleaned).strip()
        
    font_fixes = {'अंबुलें': 'अंबुर्ले', 'अशवीन': 'अश्वीन', 'अर्विनी': 'अश्विनी', 'झार्लस': 'चार्ल्स'}
    for wrong, right in font_fixes.items():
        cleaned = cleaned.replace(wrong, right)
    return cleaned

if uploaded_file is not None:
    if st.button("⚡ स्कॅनिंग सुरू करा (फक्त काही सेकंद)"):
        with st.spinner("क्लाउड सर्व्हरवर यादी स्कॅन होत आहे... कृपया थांबा..."):
            
            # तात्पुरती PDF सेव्ह करणे (दुरुस्त केलेली ओळ)
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # PDF इमेजेस मध्ये बदलणे
            pages = convert_from_path("temp.pdf", dpi=230)
            voters_list = []
            
            # प्रत्येक पानाचे ग्रिड स्कॅनिंग
            for page_num, page_img in enumerate(pages[2:], start=3):
                width, height = page_img.size
                top_margin = int(height * 0.10)
                bottom_margin = int(height * 0.95)
                grid_height = bottom_margin - top_margin
                
                col_width = width // 3
                row_height = grid_height // 5
                
                for row in range(5):
                    for col in range(3):
                        x1 = col * col_width
                        y1 = top_margin + (row * row_height)
                        x2 = x1 + col_width
                        y2 = y1 + row_height
                        
                        box = page_img.crop((x1, y1, x2, y2))
                        text = pytesseract.image_to_string(box, lang='mar+script/Devanagari', config='--oem 3 --psm 6')
                        
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        
                        epic_id = None
                        full_name = ""
                        
                        for line in lines:
                            epic_match = re.search(r'([A-Z]{3})\s*(\d{7})', line)
                            if epic_match:
                                epic_id = f"{epic_match.group(1)}{epic_match.group(2)}"
                                break
                        
                        if epic_id:
                            for idx, line in enumerate(lines):
                                if 'मतदाराचे' in line or 'पूर्ण' in line or 'नाव' in line:
                                    n = line.split(':')[-1].strip()
                                    full_name = clean_name(n)
                                    break
                            
                            if full_name and len(full_name) > 2:
                                voters_list.append({
                                    "मतदार आयडी": epic_id,
                                    "नाव (मराठी)": full_name,
                                    "भाग / वॉर्ड": "प्रभाग क्र. १३ (उतेखोल)"
                                })
            
            # तात्पुरती फाईल डिलीट करणे
            if os.path.exists("temp.pdf"):
                os.remove("temp.pdf")
                
            # डेटा टेबल दाखवणे
            if voters_list:
                df = pd.DataFrame(voters_list)
                st.success(f"🎉 यशस्वी! एकूण {len(df)} मतदार अचूक सापडले!")
                st.dataframe(df, use_container_width=True)
                
                # Excel/CSV डाउनलोड बटण
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 संपूर्ण यादी Excel (CSV) मध्ये डाउनलोड करा", csv, "voter_list.csv", "text/csv")
            else:
                st.warning("या PDF मधून मतदार डेटा गोळा करता आला नाही. कृपया ग्रिड लेआउट तपासा.")
