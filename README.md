# My-Bizcardx-project
Bizcard is a user friendly application designed to streamline the process of capturing and organizing information from business cards. With its advanced optical character recognition (OCR) technology, Bizcard can effortlessly extract key details such as names, phone numbers, email addresses, and company names from any business card image.

## Lets start!

## 1. Importing the requried packages:
![image](https://github.com/mad-huS/My-Bizcardx-project/assets/156919023/d08fb201-8c9c-4d04-bbc3-2c5bc14aa51a)

## 2. Extracting the information:
The image is converted in to array format using numpy and then it is read and text is extracted using EasyOCR

## 3. Parsing various types of information from the OCR data:
we have to imply certain conditions. If all these conditions are satisfied, the code will append the text to the dict variable we have created.

## 4. Uploading into the database:
These extracted information will be uploaded into the database by clicking on the save button.

## 5. Creating an web app through Streamlit app:
After this we can use various streamlit functions to upload, modify and delete the data present in the database.
