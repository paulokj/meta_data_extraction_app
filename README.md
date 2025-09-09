# 🗂️ Metadata Extraction App

A Streamlit application that extracts and displays metadata from **Image**, **Audio**, and **PDF** files.  

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://metadataextractionapp-jnkx6fmmcezu9dmvadcgd3.streamlit.app/)

---

## 🚀 App Overview

Upload files and instantly view embedded metadata such as:
- 📸 **Images** → EXIF data (camera, GPS, timestamp)  
- 🎵 **Audio** → bitrate, codec, duration  
- 📄 **PDFs** → author, creation date, PDF version  

---

## ✨ Features

- Multi-format support: Image, Audio, and PDF  
- Interactive UI for exploring metadata  
- Zero setup needed — just click the badge above to launch the app  
- Lightweight and fast (built with Streamlit)  

---

## 💻 Run Locally

Clone this repository and install dependencies:

```bash
git clone https://github.com/paulokj/meta_data_extraction_app.git
cd meta_data_extraction_app
pip install -r requirements.txt
streamlit run app.py
