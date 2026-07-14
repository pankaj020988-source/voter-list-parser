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
    cleaned = re.sub(r'[A-Za-z0-9\s§\|•\*■\+\[\]\(\)\-\./_\\\?€>;:ः]+', ' ', name)
    cleaned = re.sub(r'^(मतदाराचे पूर्ण नाव|मतदाराचे पूर्ण|पुर्ण नाव|नाव|नांव|तदाराचे पूर्ण)[:\s]*', '', cleaned).strip()
    
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
            
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # वेग आणि अचूकतेसाठी २३० DPI परफेक्ट आहे
            pages = convert_from_path("temp.pdf", dpi=230)
            voters_list = []
            
            # पेज ३ पासून संपूर्ण पानाचा लेआउट ब्लॉक स्वयंचलितपणे स्कॅन करणे
            for page_num, page_img in enumerate(pages[2:], start=3):
                # PSM 3 ऑटोमॅटिक लेआउट पॅटर्न क्लाउडवर सर्वात अचूक काम करतो
                custom_config = r'--oem 3 --psm 3'
                text = pytesseract.image_to_string(page_img, lang='mar+script/Devanagari', config=custom_config)
                
                # मतदार आयडीनुसार (EPIC ID) डेटाचे ब्लॉक्स पाडणे
                voter_blocks = re.split(r'([A-Z]{3}\s*\d{7})', text)
                
                if len(voter_blocks) < 2:
                    continue
                    
                i = 1
                while i < len(voter_blocks):
                    epic_id = re.sub(r'\s+', '', voter_blocks[i])
                    block_content = voter_blocks[i+1] if i+1 < len(voter_blocks) else ""
                    
                    if block_content:
                        lines = [l.strip() for l in block_content.split('\n') if l.strip()]
                        full_name = ""
                        
                        for idx, line in enumerate(lines):
                            if 'मतदाराचे' in line or 'पूर्ण' in line or 'नाव' in line:
                                name_part = line.split(':')[-1].split('नांव')[-1].strip()
                                full_name = clean_name(name_part)
                                if len(full_name) < 2 and idx + 1 < len(lines):
                                    full_name = clean_name(lines[idx+1])
                                break
                        
                        if full_name and len(full_name) > 2 and 'DELETED' not in block_content and 'वगळलेले' not in block_content:
                            voters_list.append({
                                "मतदार आयडी": epic_id,
                                "नाव (मराठी)": full_name,
                                "भाग / वॉर्ड": "प्रभाग क्र. १३ (उतेखोल)"
                            })
                    i += 2
            
            if os.path.exists("temp.pdf"):
                os.remove("temp.pdf")
                
            if voters_list:
                df = pd.DataFrame(voters_list)
                st.success(f"🎉 यशस्वी! एकूण {len(df)} मतदार अचूक सापडले!")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 संपूर्ण यादी Excel (CSV) मध्ये डाउनलोड करा", csv, "voter_list.csv", "text/csv")
            else:
                st.warning("या PDF मधून मतदार डेटा गोषा करता आला नाही. कृपया गिटहबवरील packages.txt फाईल तपासा की ती सेव्ह झाली आहे का.")
