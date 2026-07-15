# पानावरील हेडिंग आणि बाजूच्या समासाची अचूक मापे (Padding Adjustments)
            # पानावरील मुख्य मतदार यादी कुठून सुरू होते आणि कुठे संपते ते अचूक ठरवणे
            header_offset = height * 0.07  # पानावरील वरचे हेडिंग सोडण्यासाठी (7%)
            footer_offset = height * 0.03  # पानावरील खालचा भाग सोडण्यासाठी (3%)
            
            usable_height = height - header_offset - footer_offset
            row_height = usable_height / 10
            col_width = width / 3
            
            count = 1
            grid_cols = st.columns(3)
            
            for r in range(10):
                for c in range(3):
                    # प्रत्येक बॉक्सचे अचूक डावे, उजवे, वरचे आणि खालचे माप
                    left = c * col_width
                    top = header_offset + (r * row_height)
                    right = left + col_width
                    bottom = top + row_height
                    
                    # अचूक मापाने बॉक्स क्रॉप करणे (आता वरचे नाव मिक्स होणार नाही)
                    base_slip = main_image.crop((left + 5, top + 2, right - 5, bottom - 2))
                    
                    # --- ब्रँडिंग स्पेस जोडणे ---
                    border_size = 40
                    logo_space = 60 if uploaded_logo else 0
                    
                    new_w = base_slip.width + 20
                    new_h = base_slip.height + border_size + 40 + logo_space
                    
                    branded_slip = Image.new("RGB", (new_w, new_h), "#ffffff")
                    branded_slip.paste(base_slip, (10, logo_space + 10))
                    
                    draw = ImageDraw.Draw(branded_slip)
                    draw.rectangle([(2, 2), (new_w - 2, new_h - 2)], outline="#000000", width=3)
                    draw.rectangle([(5, new_h - 35), (new_w - 5, new_h - 5)], fill="#f0f2f6")
                    
                    if uploaded_logo:
                        logo_img = Image.open(uploaded_logo).resize((50, 50))
                        branded_slip.paste(logo_img, (15, 10))
                    
                    col_index = c
                    with grid_cols[col_index]:
                        st.image(branded_slip, caption=f"स्लिप क्र. {count} (पान {page_num})", use_container_width=True)
                        
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
