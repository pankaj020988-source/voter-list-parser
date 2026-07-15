import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="डिजिटल मतदार यादी कन्व्हर्टर", layout="wide")

st.title("📊 डिजिटल मतदार यादी कन्व्हर्टर व शोध प्रणाली")
st.markdown("### 🗳️ Balaji Cyber Point - Mangaon स्पेशल")
st.write("---")

# दोन वेगळे टॅब बनवू - १. पीडीएफ मधून एक्सेल बनवणे, २. नाव शोधणे
tab1, tab2 = st.tabs(["⚙️ १. पीडीएफ मजकूर टू एक्सेल कन्व्हर्टर", "🔍 २. मतदार यादी शोध प्रणाली"])

with tab1:
    st.header("📝 गुगल डॉक्सचा मजकूर इथे पेस्ट करा")
    st.info("💡 डिपार्टमेंटच्या पीडीएफ मधील मजकूर गुगल ड्राईव्ह/डॉक्स द्वारे शुद्ध मराठीत करून तो खालील बॉक्समध्ये पेस्ट करा.")
    
    # मोठा टेक्स्ट बॉक्स मजकूर पेस्ट करण्यासाठी
    raw_text = st.text_area("मजकूर (Text) इथे पेस्ट करा:", height=300)
    
    if st.button("🚀 एक्सेल यादी तयार करा"):
        if raw_text:
            # मतदार आयडीनुसार (AZS / BYY) तुकडे पाडणे
            voter_blocks = re.split(r'([A-Z]{3}\s*\d{7})', raw_text)
            final_voters = []
            
            idx = 1
            while idx < len(voter_blocks):
                epic_id = re.sub(r'\s+', '', voter_blocks[idx])
                block_content = voter_blocks[idx+1] if idx+1 < len(voter_blocks) else ""
                
                if block_content:
                    block_content = re.sub(r'\s+', ' ', block_content).strip()
                    
                    # वय आणि लिंग शोधणे
                    age = 18
                    age_match = re.search(r'वय\s*[:\-]?\s*(\d+)', block_content)
                    if age_match:
                        age = int(age_match.group(1))
                    
                    gender = "पुरुष"
                    if any(x in block_content for x in ['स्त्री', 'महिला', 'जी', 'त्री']):
                        gender = "female" # किंवा 'महिला'
                        
                    # नाव शोधणे
                    full_name = ""
                    name_match = re.search(r'(?:मतदाराचे नाव|नाव|नांव|पूर्ण नाव)\s*[:\-]?\s*([^A-Za-z0-9\:]+)', block_content)
                    
                    if name_match:
                        name_part = name_match.group(1).strip()
                        name_part = re.split(r'(?:वडिलांचे|पतीचे|आईचे|वय|लिंग|घर क्रमांक)', name_part)[0].strip()
                        full_name = re.sub(r'[^\u0900-\u097F\s]+', '', name_part).strip()
                    
                    if not full_name or len(full_name) < 3:
                        words = [w for w in block_content.split() if re.match(r'^[\u0900-\u097F]+$', w)]
                        if len(words) >= 2:
                            full_name = " ".join(words[:3])
                    
                    if full_name and not any(k in full_name for k in ['DELETED', 'वगळलेले']):
                        final_voters.append({
                            "मतदार आयडी": epic_id,
                            "नाव": full_name,
                            "वय": age,
                            "लिंग": "महिला" if gender == "female" else "पुरुष"
                        })
                idx += 2
            
            if final_voters:
                df_output = pd.DataFrame(final_voters).drop_duplicates(subset=['मतदार आयडी'])
                st.success(f"🎉 विजय झाला पंकज भाऊ! एकूण {len(df_output)} मतदार यशस्वीरित्या फिल्टर केले!")
                
                # स्क्रीनवर डेटा दाखवणे
                st.dataframe(df_output, use_container_width=True)
                
                # थेट एक्सेल/CSV डाउनलोड बटण
                csv = df_output.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 शुद्ध मराठी एक्सेल (CSV) फाईल डाउनलोड करा",
                    data=csv,
                    file_name="शुद्ध_मतदार_यादी.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ मजकुरातून डेटा ओळखता आला नाही. फॉरमॅट तपासा.")
        else:
            st.warning("⚠️ आधी वरील बॉक्समध्ये मजकूर पेस्ट करा.")

with tab2:
    st.header("🔍 मतदार शोध प्रणाली")
    uploaded_file = st.file_uploader("तुमची तयार झालेली एक्सेल/CSV फाईल इथे अपलोड करा", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"✅ डेटाबेस लोड झाला! एकूण मतदार: {len(df)}")
        
        search_query = st.text_input("📝 मतदाराचे नाव किंवा आयडी टाईप करा:")
        if search_query:
            filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)]
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.warning("❌ मतदार सापडला नाही.")
