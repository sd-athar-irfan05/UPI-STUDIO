# 💳 UPI STUDIO
### Smart UPI QR Generation & Scanning Platform

UPI STUDIO is a Python-based web application built using Streamlit that allows users to generate customized UPI QR codes, scan QR codes using a live camera or uploaded images, and manage previously generated QR codes through a history section.

## 🚀 Features

- **UPI QR Generation:** Generate QR codes using UPI ID, payee name, amount, and transaction note.
- **QR Customization:** Customize QR code and background colors.
- **Logo Integration:** Add a custom logo to the center of the QR code.
- **QR Download:** Download generated QR codes as image files.
- **Live QR Scanner:** Scan QR codes using a webcam.
- **Image QR Scanner:** Upload an existing QR image and decode its information.
- **QR History:** View previously generated QR codes and their transaction details.
- **History Management:** Download QR codes from history or clear saved history.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core Programming Language |
| Streamlit | Web Application Framework |
| OpenCV | QR Code Detection and Scanning |
| qrcode | QR Code Generation |
| Pillow | Image Processing |
| NumPy | Image Array Processing |
| Streamlit-WebRTC | Live Camera Streaming |
| AV | Video Frame Processing |

## 📂 Project Structure

```text
UPI-QR/
│
├── upi.py
├── upi_backup.py
├── QR.ipynb
├── requirements.txt
├── README.md
├── .gitignore
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sd-athar-irfan05/UPI-STUDIO.git
```

### 2. Navigate to Project Folder

```bash
cd UPI-STUDIO
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the Application

```bash
streamlit run upi.py
```

The application will open in your browser.

## 📱 Application Modules

1. **Generate QR** – Create and customize UPI payment QR codes.
2. **Scan QR** – Scan QR codes through live camera or image upload.
3. **QR History** – Manage previously generated QR codes.

## 🔐 Important Note

UPI STUDIO generates UPI payment QR codes. It does not directly process payments, access bank accounts, or verify successful transactions.

Always verify the recipient's UPI ID and payment amount in your UPI application before authorizing a transaction.

## 🎯 Project Objective

The objective of UPI STUDIO is to build a simple and user-friendly platform for generating, customizing, scanning, and managing UPI QR codes using Python.

## 👨‍💻 Developer

Developed as a Python and Streamlit project.

---

⭐ If you find this project useful, consider giving it a star!