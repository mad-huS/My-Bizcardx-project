import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import pandas as pd
import numpy as np
from PIL import Image
import re
import io
import mysql.connector

def img_to_text(path):

    input_img  = Image.open(path)
    
    #converting image into array format
    
    img_array = np.array(input_img)
    
    reader = easyocr.Reader(['en'])
    text = reader.readtext(img_array, detail = 0) # detail = 0 ---> excludes all the array part extracts only the text part

    return text, input_img

def extracted_texts(texts):
    extrd_dict = {"Name":[],"Designation":[],"Company_name":[],"Contact":[],"Email":[],
                  "Website":[],"Address":[],"Pincode":[]}
    extrd_dict['Name'].append(texts[0])
    extrd_dict['Designation'].append(texts[1])

    for i in range(2,len(texts)):

        if texts[i].startswith('+') or (texts[i].replace('-','').isdigit() and '-' in texts[i]) :
            extrd_dict['Contact'].append(texts[i])
            
        elif '@' in texts[i] and '.com' in texts[i]:
            extrd_dict['Email'].append(texts[i])
            
        elif (texts[i].startswith('WWW') or texts[i].startswith('www') or texts[i].startswith('wwW') or texts[i].startswith('Www')) or (texts[i].endswith('.com')):
            lowerC = texts[i].lower()
            extrd_dict['Website'].append(lowerC)

        elif 'TamilNadu' in texts[i] or 'Tamil Nadu' in texts[i] or 'Tamil nadu' in texts[i] or 'Tamilnadu' in texts[i] or (texts[i].isdigit() and len(texts[i])==6):
            pincode_pattern = re.compile(r'\b\d{6}\b|\b\d{7}\b')
            pincodes = []
            for item in range(len(texts[i])):
                matches = pincode_pattern.findall(texts[i])
                
                extrd_dict['Pincode'].extend(matches)
                if len(extrd_dict['Pincode'])>0:
                    break

        elif (texts[i] not in districts_tamilnadu) and (re.match(r'^[a-zA-Z]', texts[i])) and not (texts[i].endswith('.com')) :
            extrd_dict['Company_name'].append(texts[i]) 

        else:
            remove_colon = re.sub(r'^[,;]','',texts[i])
            extrd_dict['Address'].append(remove_colon)
            
    for key,value in extrd_dict.items():

        if isinstance(value, list) and len(value) > 0:  # Check if value is a list
            if value:  # Check if the list is not empty
                concate_str = ' '.join(value)  # Join list elements into a single string
                extrd_dict[key] = [concate_str]

        else:
            value = 'NA'
            extrd_dict[key] = [value]
            
    return extrd_dict


#Streamlit part

st.set_page_config(layout = 'wide')
st.title("Extracting Business Card Data with OCR")
with st.sidebar:
    select = option_menu("Main menu",["Home","Upload & Modify", "Delete"])

if select == 'Home':
    st.markdown(
        """
        <div style='background-color: #f0f0f0; padding: 20px; border-radius: 10px;'>
            <h2 style='color: #333333;'>Welcome to Bizcard!</h2>
            <p style='color: #555555; font-size: 16px; line-height: 1.5;'>
                Bizcard is an application designed to streamline the process of capturing and organizing information from business cards. With its advanced optical character recognition (OCR) technology, Bizcard can effortlessly extract key details such as names, phone numbers, email addresses, and company names from any business card image.
            </p>
            <h3 style='color: #333333;'>Here there are two options available</h2>
             <ul style='list-style-type: none; padding-left: 0;'>
            <li style='margin-bottom: 10px;'>
                <span style='font-weight: bold; color: #007bff;'>1. Upload and Modify:</span>  
                <span style='color: #555555;'> Here you can preview, modify and upload the extracted information.</span>
            </li>
            <li style='margin-bottom: 10px;'>
                <span style='font-weight: bold; color: #007bff;'>2. Delete:</span> 
                <span style='color: #555555;'> In this, you can delete business card information that is no longer required.</span>
            </li>
        </ul>   
        </div>
        """,
        unsafe_allow_html=True
    )
    
elif select == 'Upload & Modify':
    img = st.file_uploader("Upload the Image here", type = ['png','jpg','jpeg'])

    if img is not None:
        st.image(img, width = 300)
        text_img, input_img = img_to_text(img)
        
        text_dict = extracted_texts(text_img)
        if text_dict:
            st.success("Text is extracted successfully")
        text_df = pd.DataFrame(text_dict)

        #converting image to bytes

        Imagebytes = io.BytesIO()
        input_img.save(Imagebytes, format = 'PNG')
        
        image_data = Imagebytes.getvalue()

        #creating dictionary
        
        data = {"Image":[image_data]}
        
        df1 = pd.DataFrame(data)

        concat_df = pd.concat([text_df, df1],axis = 1)
        
        st.dataframe(concat_df)

        button_1 = st.button("Save", use_container_width = True)

        if button_1:
            mydb = mysql.connector.connect(
                                host="127.0.0.1",
                                user="root",
                                password="madhu123",
                                database="bizcardx",
                                port = "3306"
                              )
                        
            cursor = mydb.cursor()
            
            query1 = '''create table if not exists bizcard_detail(Name varchar(100),
                                                                   Designation varchar(100),
                                                                   Company_name varchar(100),
                                                                   Contact varchar(100),
                                                                   Email varchar(100),
                                                                   Website text,
                                                                   Address text,
                                                                   Pincode int,
                                                                   Image longblob);'''
            
            cursor.execute(query1)
            mydb.commit()

            # Modify the insert query to use parameterized placeholders

            insert1 = '''insert into bizcard_detail(
                Name, Designation, Company_name,
                Contact, Email, Website, Address, Pincode, Image
            ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            
            # Convert DataFrame to list of tuples
            datas = [tuple(row) for row in concat_df.values]
            
            # Execute the insert query with parameters
            cursor.executemany(insert1, datas)
            
            # Commit the changes
            mydb.commit()

            st.success("Saved and uploaded into Database successfully")

    method = st.radio("Select the method", ["None","Preview","Modify"])

    if method == "None":
        st.write("")

    if method == "Preview":
        
        mydb = mysql.connector.connect(
                                host="127.0.0.1",
                                user="root",
                                password="madhu123",
                                database="bizcardx",
                                port = "3306"
                              )
                        
        cursor = mydb.cursor()
        
        select_query  = '''select * from bizcard_detail'''
        cursor.execute(select_query)
        
        table = cursor.fetchall()
        mydb.commit()
        
        table_df = pd.DataFrame(table,columns = ["Name","Designation","Company_name","Contact","Email","Website","Address","Pincode","Image"])

        st.dataframe(table_df)

    if method == 'Modify':

        mydb = mysql.connector.connect(
                                host="127.0.0.1",
                                user="root",
                                password="madhu123",
                                database="bizcardx",
                                port = "3306"
                              )
                        
        cursor = mydb.cursor()
        
        select_query  = '''select * from bizcard_detail'''
        cursor.execute(select_query)
        
        table = cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table,columns = ["Name","Designation","Company_name","Contact","Email","Website","Address","Pincode","Image"])

        col1,col2 = st.columns(2)

        with col1:

            selected_name = st.selectbox("Select the name",table_df['Name'])

        df2 = table_df[table_df['Name'] == selected_name] 

        st.dataframe(df2)

        df3 = df2.copy()

        col1, col2 = st.columns(2)

        with col1:

            mod_name = st.text_input("Name", df2['Name'].unique()[0])
            mod_Designation = st.text_input("Designation", df2['Designation'].unique()[0])
            mod_Comp_name = st.text_input("Company_name", df2['Company_name'].unique()[0])
            mod_Contact = st.text_input("Contact", df2['Contact'].unique()[0])
            mod_email = st.text_input("Email", df2['Email'].unique()[0])

            df3['Name'] = mod_name
            df3['Designation'] = mod_Designation
            df3['Company_name'] = mod_Comp_name
            df3['Contact'] = mod_Contact
            df3['Email'] = mod_email 

        with col2:

            mod_web = st.text_input("Website", df2['Website'].unique()[0])
            mod_address = st.text_input("Address", df2['Address'].unique()[0])
            mod_pincode = st.text_input("Pincode", df2['Pincode'].unique()[0])
            mod_img = st.text_input("Image", df2['Image'].unique()[0])

            df3['Website'] = mod_web
            df3['Address'] = mod_address
            df3['Pincode'] = mod_pincode
            df3['Image'] = mod_img

        st.dataframe(df3)

        col1, col2 = st.columns(2)
        with col1:
            button2 = st.button("Modify", use_container_width = True)

        if button2:
            mydb = mysql.connector.connect(
                                host="127.0.0.1",
                                user="root",
                                password="madhu123",
                                database="bizcardx",
                                port = "3306"
                              )
                        
            cursor = mydb.cursor()
            cursor.execute(f'delete from bizcard_detail where Name = "{selected_name}"')
            mydb.commit()

            insert1 = '''insert into bizcard_detail(
                Name, Designation, Company_name,
                Contact, Email, Website, Address, Pincode, Image
            ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            
            # Convert DataFrame to list of tuples
            datas = [tuple(row) for row in df3.values]
            cursor.executemany(insert1, datas)
            
            # Commit the changes
            mydb.commit()

            st.success("Modification Saved and uploaded into Database successfully")
            

elif select == 'Delete':
    mydb = mysql.connector.connect(
                                host="127.0.0.1",
                                user="root",
                                password="madhu123",
                                database="bizcardx",
                                port = "3306"
                              )
                        
    cursor = mydb.cursor()

    col1, col2 = st.columns(2)
    with col1:
        select_query  = '''select Name from bizcard_detail'''
        cursor.execute(select_query)
        table1 = cursor.fetchall()
        mydb.commit()
        
        name1 = []
        
        for i in table1:
            name1.append(i[0])

        name = st.selectbox("Select the name", name1)

    with col2:
        select_query1  = f'''select Designation from bizcard_detail where Name = "{name}"'''
        cursor.execute(select_query1)
        table2 = cursor.fetchall()
        mydb.commit()
        
        Designation1 = []
        
        for i in table2:
            Designation1.append(i[0])

        desig = st.selectbox("Select the Designation", Designation1)

    if name and desig:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"Selected name : {name}")
            st.write("")
            st.write("")
            st.write("")
            st.write(f"Selected Designation : {desig}")

        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            remove = st.button("Delete",use_container_width = True)

            if remove:
                cursor.execute(f"delete from bizcard_detail where Name = '{name}' and Designation = '{desig}'")
                mydb.commit()
                st.warning("Deleted Successfully")
    