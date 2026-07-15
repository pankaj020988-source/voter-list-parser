import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="डिजिटल मतदार यादी कन्व्हर्टर", layout="wide")

# मुख्य हेडिंग
st.title("📊 डिजिटल मतदार यादी कन्व्हर्टर व शोध प्रणाली")
st.markdown("### 🗳️ Balaji Cyber Point - Mangaon स्पेशल")
st.write("---")

# लेआउटसाठी दोन भाग (Columns) करणे
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📁 डेटाबेस लोड करा")
    uploaded_file = st.file_uploader("प्रभागाची एक्सेल (XLSX) किंवा सीएव्ही (CSV) फाईल इथे अपलोड करा", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # फाईल वाचणे
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"✅ डेटाबेस यशस्वीरित्या लोड झाला! एकूण मतदार: {len(df)}")
        
        with col2:
            st.header("🔍 मतदार शोध प्रणाली")
            search_query = st.text_input("📝 मतदाराचे नाव किंवा मतदार आयडी (EPIC No.) टाईप करा:")
            
            if search_query:
                # सर्व कॉलममध्ये सर्च मारणे
                filtered_df = df[
                    df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)
                ]
                
                if not filtered_df.empty:
                    st.write(f"🎯 सापडलेले एकूण मतदार: {len(filtered_df)}")
                    
                    # टेबल स्वरूपात डेटा दाखवणे
                    st.dataframe(filtered_df, use_container_width=True)
                    
                    # पहिल्या सापडलेल्या मतदाराची स्लिप तयार करणे (सिंगल स्लिप प्रिंटसाठी)
                    st.markdown("---")
                    st.subheader("🖨️ मतदार माहिती पावती (Voter Slip)")
                    
                    row = filtered_df.iloc[0]
                    
                    # स्लिपचे सुंदर एचटीएमएल डिझाईन
                    html_slip = f"""
                    <div style="border: 2px dashed #000; padding: 15px; width: 350px; background-color: #fff; font-family: 'Arial'; color: #000;">
                        <h4 style="text-align: center; margin: 0; border-bottom: 1px solid #000; padding-bottom: 5px;">🗳️ मतदान माहिती पावती 🗳️</h4>
                        <p style="margin: 8px 0;"><b>नाव:</b> {row.get('नाव (मराठी)', row.get('नाव', 'N/A'))}</p>
                        <p style="margin: 8px 0;"><b>मतदार आयडी (EPIC):</b> {row.get('मतदार आयडी', row.get('EPIC ID', 'N/A'))}</p>
                        <p style="margin: 8px 0;"><b>वय:</b> {row.get('वय', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp; <b>लिंग:</b> {row.get('लिंग', 'N/A')}</p>
                        <p style="margin: 8px 0; font-size: 13px; color: #555;"><i>शुभेच्छुक: बालाजी सायबर पॉईंट, माणगाव</i></p>
                    </div>
                    <br>
                    <button onclick="window.print()" style="padding: 8px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">🖨️ स्लिप प्रिंट करा</button>
                    """
                    st.components.v1.html(html_slip, height=250)
                    
                else:
                    st.warning("❌ या नावाचा किंवा आयडीचा कोणताही मतदार सापडला नाही.")
                    
    except Exception as e:
        st.error(f"❌ फाईल लोड करताना त्रुटी आली: {e}")
else:
    with col2:
        st.info("👋 सायबर पॉईंट मतदार शोध सिस्टीममध्ये आपले स्वागत आहे! सुरू करण्यासाठी डाव्या बाजूला तुमची एक्सेल फाईल (उदा. 'प्रभाग_१३_मतदार_यादी.csv') अपलोड करा.")
