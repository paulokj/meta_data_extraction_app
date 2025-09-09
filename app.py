# Core pkg
import streamlit as st
import streamlit.components.v1 as stc

# EDA Pkgs
import pandas as pd
import numpy as np

# Data Viz Pkgs
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg') # you can use TkAgg

# MetaData Extraction Pkgs
# images
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread
import os
from datetime import datetime
import base64
import time

# Audio
import mutagen

# pdf
import PyPDF2

# Database Management
import sqlite3
conn = sqlite3.connect('data.db') # Creating a database or connecting to one if exists
c = conn.cursor() # Creating a cursor object using the con

# Table to store the details
def create_uploaded_filetable():
    c.execute('CREATE TABLE IF NOT EXISTS filestable'
    '(filename TEXT, filetype TEXT, filesize TEXT, uploadDate TIMESTAMP)')

# Adding data to the table
def add_file_details(filename, filetype, filesize):
    c.execute('INSERT INTO filestable(filename, filetype, filesize, uploadDate) VALUES (?,?,?,?)',
              (filename, filetype, filesize, datetime.now()))
    conn.commit()

# Fetching all the data from the table
def view_all_data():
    c.execute('SELECT * FROM filestable')
    data = c.fetchall()
    return data



# HTML
metadata_wiki = """
Metadata is defined as the data providing information about one or more aspects of the data; it is used to summarize basic information about data which can make tracking and working with specific data easier
"""

HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">MetaData Extractor App </h1>
    </div>
    """

# Fuctions
@st.cache_resource
def load_image(image_file):
    img = Image.open(image_file)
    return img

# Fuction to get human readable time
def get_human_readable_time(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%d-%H:%M:%S")

def safe_str(v):
    if isinstance(v, (tuple, list, dict)):
        return str(v)
    elif v is None:
        return ""
    return str(v)

def get_geotags(filename):
    """
    Extracts and organizes geographical information (geotags) from an image file's EXIF data.

    Args:
        filename (str): The path to the image file.

    Returns:
        dict: A dictionary containing the organized EXIF data.
              Returns an empty dictionary if no EXIF data is found.
    """
    exif = {}
    try:
        image = Image.open(filename)
        # The _getexif() method gets the raw EXIF data.
        raw_exif = image._getexif()
    except IOError:
        print("Error: The file could not be opened or is not a valid image.")
        return exif

    if raw_exif:
        # Loop through the raw EXIF data to translate tag numbers to human-readable names.
        for tag, value in raw_exif.items():
            tag_name = TAGS.get(tag, tag)
            exif[tag_name] = value

        # Check for GPSInfo key, which contains geographical data.
        if 'GPSInfo' in exif:
            gps_info = {}
            # Loop through the GPSInfo dictionary to translate tag numbers to names.
            for tag, value in exif['GPSInfo'].items():
                tag_name = GPSTAGS.get(tag, tag)
                gps_info[tag_name] = value

            # Replace the numerical GPSInfo dictionary with the more readable one.
            exif['GPSInfo'] = gps_info
    
    return exif

def get_coordinates(info):
    """
    Extract GPS coordinates as strings from EXIF info.
    Returns a tuple of (Latitude, Longitude) if available.
    """
    for key in ['Latitude', 'Longitude']:
        gps_key = 'GPS' + key
        gps_ref_key = gps_key + 'Ref'
        if gps_key in info and gps_ref_key in info:
            e = info[gps_key]
            ref = info[gps_ref_key]
            # Convert from DMS (degrees, minutes, seconds) tuple to string
            info[key] = (
                str(e[0][0]/e[0][1]) + '°' +
                str(e[1][0]/e[1][1]) + '\'' +
                str(e[2][0]/e[2][1]) + '"' +
                ref
            )

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]


def get_decimal_coordinates(info):
    """
    Convert GPS coordinates in EXIF info to decimal format.
    Returns a tuple of (Latitude, Longitude) in decimal degrees.
    """
    for key in ['Latitude', 'Longitude']:
        gps_key = 'GPS' + key
        gps_ref_key = gps_key + 'Ref'
        if gps_key in info and gps_ref_key in info:
            e = info[gps_key]
            ref = info[gps_ref_key]
            # Convert from DMS to decimal degrees
            info[key] = (
                e[0][0]/e[0][1] +          # degrees
                e[1][0]/e[1][1]/60 +       # minutes
                e[2][0]/e[2][1]/3600       # seconds
            ) * (-1 if ref in ['S', 'W'] else 1)

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]

# time format
timestr = time.strftime("%Y%m%d-%H%M%S")

# Fxn to Download file
def make_downloadable(data, file_name='output.csv'):
    csvfile = data.to_csv(index=False)
    b64 = base64.b64encode(csvfile.encode()).decode()  # makes the file downloadble for html
    st.markdown("### Download File ###")
    new_file_name = file_name.split(".")[0] + "_" + timestr + ".csv"
    href = f'<a href="data:file/csv;base64,{b64}" download="{new_file_name}">Click Here!!</a>' # create download link
    st.markdown(href, unsafe_allow_html=True)

def read_pdf(file):
    pdfReader = PyPDF2.PdfReader(file)
    count = len(pdfReader.pages)
    all_page_text = ""
    for i in range(count):
        page = pdfReader.pages[i]
        all_page_text += page.extract_text()

    return all_page_text

def main():
    """
    This is a meta data extractor app
    """
    
    # st.title("Meta Data Extractor App")
    stc.html(HTML_BANNER)

    menu = ["Home", "Image", "Audio", "Document Files", "Analytics", "About"]
    choice = st.sidebar.selectbox("Menu", menu)
    create_uploaded_filetable() # create the table if not exists - see above

    if choice == "Home":
        st.subheader("Home")
        #image
        st.image(load_image("./images/metadataextraction_app.png"))
        #description
        st.write(metadata_wiki)
        #expanders
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.expander("Get image Meta Data 📷"):
                st.info("Image Meta Data")
                st.markdown("📷")
                st.text("Upload JPEG, JPG, PNG files")
        with col2:
            with st.expander("Get Audio Meta Data 🔉"):
                st.info("Audio Meta Data")
                st.markdown("🔉")
                st.text("Upload MP3, OGG files")
        with col3:
            with st.expander("Get Document Data 📄📁"):
                st.info("Document Meta Data")
                st.markdown("📄📁")
                st.text("Upload PDF, Docx files")
        
    
    elif choice == "Image":
        st.subheader("Image Meta Data Extractor")
        image_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
        if image_file:
            # UploadFile Class Like Binary Byte
            # st.write(type(image_file))
            # st.write(dir(image_file))
            with st.expander("File Stats"):
                file_details = {"Filename":image_file.name, 
                                "FileType":image_file.type, 
                                "FileSize":image_file.size,
                                "FileTyepe":image_file.type}
                st.json(file_details)

                statinfo = os.stat(image_file.readable())
                st.write(statinfo)
                stats_details = {"Accessed_Time":get_human_readable_time(statinfo.st_atime),
                                 "Creation_Time":get_human_readable_time(statinfo.st_ctime),
                                 "Modified_Time":get_human_readable_time(statinfo.st_mtime)}
                st.json(stats_details)

                # Combining all the details
                all_details = {**file_details, **stats_details}
                # Covert the values to string
                all_details_str = {k: safe_str(v) for k, v in all_details.items()}

                # Convert to DataFrame
                all_details_df = pd.DataFrame(list(all_details_str.items()), columns=["Meta Tags", "Value"])
                st.dataframe(all_details_df)

                # Add the file details to the database
                add_file_details(image_file.name, image_file.type, image_file.size)

            # layout
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("View Image"):
                    img = load_image(image_file)
                    st.image(img, caption=image_file.name, width=250)
            with col2:
                with st.expander("Default  (JPEG)"):
                    st.info("Using PILLOW")
                    img = load_image(image_file)
                    # st.write(dir(img))
                    img_details = {
                                    "format": img.format,
                                    "format_description": img.format_description,
                                    "file_name": img.filename,
                                    "size": img.size,
                                    "height": img.height,
                                    "width": img.width,
                                    "info": img.info,
                                    "encoder_info": getattr(img, "encoderinfo", None),
                                    "mode": img.mode
                                }
                    # st.json(img_details)
                    df_img_details_default = pd.DataFrame(
                                                        [(k, safe_str(v)) for k, v in img_details.items()],
                                                        columns=["Meta Tags", "Value"]
                                                    )
                    st.dataframe(df_img_details_default)

            # Forensic layout
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                with  st.expander("Exifread Tool"):
                    meta_tags = exifread.process_file(image_file)
                    st.write(meta_tags)

                    df_img_details_exifread = pd.DataFrame(
                                                        [(k, safe_str(v)) for k, v in meta_tags.items()],
                                                        columns=["Meta Tags", "Value"]
                                                    )
                    st.dataframe(df_img_details_exifread)
            
            with fcol2:
                with  st.expander("Image Geo-Coordinate"):
                    img_details_with_exif = get_geotags(image_file)
                    try:
                        gps_info = img_details_with_exif
                    except:
                        gps_info = None

                    st.write(gps_info)
                    img_coordinates = get_coordinates(gps_info) if gps_info else None
                    st.write(img_coordinates)


            with st.expander("Download Results"):
                final_df = pd.concat([all_details_df, df_img_details_default, df_img_details_exifread]).reset_index(drop=True)
                st.dataframe(final_df)
                make_downloadable(final_df, file_name=image_file.name.split(".")[0]+".csv")


    elif choice == "Audio":
        st.subheader("Audio Meta Data Extractor")
        # File  Uplodader
        # Extraction Process using mutagen (There are other pkgs too: tinytag, eyed3, pydub, pyaudio, librosa)
        audio_file = st.file_uploader("Upload Audio", type=['mp3', 'ogg'])
        if audio_file:          

            # Layout
            col1, col2 = st.columns(2)
            with col1:
                st.audio(audio_file.read())

            with col2:
                with st.expander("File Stats"):
                    file_details = {"Filename":audio_file.name, 
                                    "FileType":audio_file.type, 
                                    "FileSize":audio_file.size,
                                    "FileTyepe":audio_file.type}
                    st.json(file_details)

                    statinfo = os.stat(audio_file.readable())
                    st.write(statinfo)
                    stats_details = {"Accessed_Time":get_human_readable_time(statinfo.st_atime),
                                     "Creation_Time":get_human_readable_time(statinfo.st_ctime),
                                     "Modified_Time":get_human_readable_time(statinfo.st_mtime)}
                    st.json(stats_details)

                    # Combining all the details
                    all_details = {**file_details, **stats_details}
                    # Covert the values to string
                    all_details_str = {k: safe_str(v) for k, v in all_details.items()}

                    # Convert to DataFrame
                    all_details_df = pd.DataFrame(list(all_details_str.items()), columns=["Meta Tags", "Value"])
                    st.dataframe(all_details_df)

                    # Add the file details to the database
                    add_file_details(audio_file.name, audio_file.type, audio_file.size)


            # Extraction Process Using Mutagen
            with st.expander("Meta Data Using Mutagen"):
                meta_tags = mutagen.File(audio_file)
                # st.write(dir(audio))
                df_audio_details_with_mutagen = pd.DataFrame(
                                            [(k, safe_str(v)) for k, v in meta_tags.items()],
                                            columns=["Meta Tags", "Value"]
                                        )
                st.table(df_audio_details_with_mutagen)

            with st.expander("Download Results"):
                final_df = pd.concat([all_details_df, df_audio_details_with_mutagen]).reset_index(drop=True)
                st.dataframe(final_df)
                make_downloadable(final_df, file_name=audio_file.name.split(".")[0]+".csv")


                





    elif choice == "Document Files":
        st.subheader("Document Files Meta Data Extractor")

        # File Upload
        text_file = st.file_uploader("Upload File", type=['pdf', 'docx'])
        # st.write(dir(text_file))
        if text_file:

            tcol1, tcol2 = st.columns([1, 2])
            with tcol1:
                with st.expander("File Stats"):
                    file_details = {"Filename":text_file.name, 
                                    "FileType":text_file.type, 
                                    "FileSize":text_file.size,
                                    "FileTyepe":text_file.type}
                    st.json(file_details)

                    statinfo = os.stat(text_file.readable())
                    st.write(statinfo)
                    stats_details = {"Accessed_Time":get_human_readable_time(statinfo.st_atime),
                                    "Creation_Time":get_human_readable_time(statinfo.st_ctime),
                                    "Modified_Time":get_human_readable_time(statinfo.st_mtime)}
                    st.json(stats_details)

                   # Combining all the details
                    all_details = {**file_details, **stats_details}
                    # Covert the values to string
                    all_details_str = {k: safe_str(v) for k, v in all_details.items()}

                    # Convert to DataFrame
                    all_details_df = pd.DataFrame(list(all_details_str.items()), columns=["Meta Tags", "Value"])
                    st.dataframe(all_details_df)

                    # Add the file details to the database
                    add_file_details(text_file.name, text_file.type, text_file.size)

            with tcol2:
                if text_file.type == "application/pdf":
                    with st.expander("Meta Data Using PyPDF2"):
                        pdf_text = read_pdf(text_file)
                        st.write(pdf_text)
                        pdf_details = {
                                        "Number_of_Pages": len(pdf_text.split("\n")),
                                        # "Content": pdf_text,
                                        "File_Name": text_file.name,
                                        "File_Size": text_file.size,
                                        "File_Type": text_file.type
                                    }
                        df_pdf_details_with_pypdf2 = pd.DataFrame(
                                                    [(k, safe_str(v)) for k, v in pdf_details.items()],
                                                    columns=["Meta Tags", "Value"]
                                                )
                                            
                        st.dataframe(df_pdf_details_with_pypdf2)

                        # Add the file details to the database
                        add_file_details(text_file.name, text_file.type, text_file.size)


        # Download
            with st.expander("Download"):
                final_df = pd.concat([all_details_df, df_pdf_details_with_pypdf2]).reset_index(drop=True)
                st.dataframe(final_df)
                make_downloadable(final_df, file_name=text_file.name.split(".")[0]+".csv")

    elif choice == "Analytics":
        st.subheader("Analytics")

        # View All Uploads
        all_uploaded_files = view_all_data()
        df = pd.DataFrame(all_uploaded_files, columns=["Filename", "FileType", "FileSize", "UploadDateTime"])

        # Monitor All uploads
        with st.expander("Monitor All Uploads"):
            st.success("View All Uploaded Files")
            st.dataframe(df)

            # Download
            with st.expander("Download"):
                make_downloadable(df, file_name="All_Files_Stats.csv")


        # Stats of Uploaded Files
        with st.expander("Distribution of FileTypes"):
            fig = plt.figure()
            sns.countplot(df['FileType'])
            st.pyplot(fig)  
    
    else:
        st.subheader("About")
        #image
        st.image(load_image("./images/metadataextraction_app.png"))
        
        # Stats of Uploaded Files
        all_uploaded_files = view_all_data()
        df = pd.DataFrame(all_uploaded_files, columns=["Filename", "FileType", "FileSize", "UploadDateTime"])

        with st.expander("Distribution of FileTypes"):
            fig = plt.figure()
            sns.countplot(df['FileType'])
            st.pyplot(fig)  

if __name__ == '__main__':
    main()