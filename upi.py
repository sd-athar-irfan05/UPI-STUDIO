import streamlit as st
import qrcode
import cv2
import numpy as np
import av
import re
import threading

from io import BytesIO
from datetime import datetime
from urllib.parse import urlencode
from PIL import Image, ImageDraw
from qrcode.constants import ERROR_CORRECT_H

from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    RTCConfiguration,
    VideoProcessorBase
)


# =========================================
# 1. PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="UPI Studio | Smart QR Platform",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================
# 2. SESSION STATE
# =========================================

if "qr_history" not in st.session_state:
    st.session_state.qr_history = []

if "qr_image" not in st.session_state:
    st.session_state.qr_image = None

if "payment_link" not in st.session_state:
    st.session_state.payment_link = None


# =========================================
# 3. CUSTOM CSS
# =========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080D19;
    color: #FFFFFF;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

header {
    background: transparent !important;
}

.hero {
    padding: 35px;
    border-radius: 22px;
    background: linear-gradient(120deg, #14243D, #101827, #172C35);
    border: 1px solid #263A52;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 8px;
}

.hero p {
    color: #AAB8CA;
    font-size: 15px;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 5px;
}

.section-subtitle {
    color: #93A4BA;
    font-size: 13px;
    margin-bottom: 20px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111B2C;
    border: 1px solid #26364D;
    border-radius: 16px;
    padding: 18px;
}

.stTextInput input,
.stNumberInput input {
    background: #0B1423;
    color: white;
    border: 1px solid #34445B;
    border-radius: 9px;
}

.stButton button {
    background: linear-gradient(90deg, #00C6A2, #00A88A);
    color: #06131A;
    font-weight: 700;
    border: none;
    border-radius: 9px;
    padding: 10px 20px;
}

.stButton button:hover {
    background: #00E0B5;
    color: #06131A;
}

.metric-box {
    background: #111B2C;
    border: 1px solid #26364D;
    padding: 18px;
    border-radius: 14px;
}

.metric-box h3 {
    color: #00D5AA;
    font-size: 24px;
    margin: 0;
}

.metric-box p {
    color: #AAB8CA;
    font-size: 13px;
}

.footer {
    text-align: center;
    color: #64748B;
    padding: 30px 0 10px;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


# =========================================
# 4. HEADER
# =========================================

st.html("""
<div class="hero">

    <h1>UPI STUDIO.</h1>

    <p>Smart QR Generation & Scanning Platform</p>

    <p>Create • Customize • Scan • Download • Manage</p>

</div>
""")

# =========================================
# 5. DASHBOARD METRICS
# =========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-box">
        <h3>01</h3>
        <p>QR GENERATOR</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-box">
        <h3>02</h3>
        <p>QR SCANNER</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-box">
        <h3>03</h3>
        <p>QR MANAGEMENT</p>
    </div>
    """, unsafe_allow_html=True)


st.write("")


# =========================================
# 6. APPLICATION TABS
# =========================================

generate_tab, scanner_tab, history_tab = st.tabs([
    "✦ Generate QR",
    "⌕ Scan QR",
    "◷ QR History"
])


# =========================================
# 7. QR GENERATOR
# =========================================

with generate_tab:

    st.markdown(
        '<div class="section-title">Create Your UPI QR</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Enter payment details and customize your QR code.'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1.3, 1])

    with left:

        with st.container(border=True):

            st.subheader("Payment Details")

            with st.form("qr_generation_form"):

                upi_id = st.text_input(
                    "UPI ID",
                    placeholder="example@okaxis"
                )

                payee_name = st.text_input(
                    "Account Holder Name",
                    placeholder="Enter your name"
                )

                amount = st.number_input(
                    "Amount (Optional ₹)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0
                )

                note = st.text_input(
                    "Payment Note (Optional)",
                    placeholder="Payment for..."
                )

                st.divider()

                st.subheader("QR Customization")

                color1, color2 = st.columns(2)

                with color1:
                    qr_color = st.color_picker(
                        "QR Color",
                        "#102A43"
                    )

                with color2:
                    bg_color = st.color_picker(
                        "Background Color",
                        "#FFFFFF"
                    )

                logo_file = st.file_uploader(
                    "Upload Logo (Optional)",
                    type=["png", "jpg", "jpeg"]
                )

                generate_button = st.form_submit_button(
                    "✦ Generate My QR Code",
                    use_container_width=True
                )

    # -------------------------------------
    # GENERATE QR
    # -------------------------------------

    if generate_button:

        upi_pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$"

        if not upi_id.strip() or not payee_name.strip():

            st.error(
                "Please enter both UPI ID and account holder name."
            )

        elif not re.match(upi_pattern, upi_id.strip()):

            st.error("Please enter a valid UPI ID.")

        elif amount < 0:

            st.error("Amount cannot be negative.")

        else:

            try:

                params = {
                    "pa": upi_id.strip(),
                    "pn": payee_name.strip(),
                    "cu": "INR"
                }

                if amount > 0:
                    params["am"] = f"{amount:.2f}"

                if note.strip():
                    params["tn"] = note.strip()

                payment_link = "upi://pay?" + urlencode(params)

                qr = qrcode.QRCode(
                    version=None,
                    error_correction=ERROR_CORRECT_H,
                    box_size=12,
                    border=4
                )

                qr.add_data(payment_link)
                qr.make(fit=True)

                qr_image = qr.make_image(
                    fill_color=qr_color,
                    back_color=bg_color
                ).convert("RGB")

                # Optional logo

                if logo_file is not None:

                    logo = Image.open(logo_file).convert("RGBA")

                    logo_size = qr_image.width // 5

                    logo.thumbnail(
                        (logo_size, logo_size)
                    )

                    position = (
                        (qr_image.width - logo.width) // 2,
                        (qr_image.height - logo.height) // 2
                    )

                    draw = ImageDraw.Draw(qr_image)

                    padding = 10

                    draw.rounded_rectangle(
                        [
                            position[0] - padding,
                            position[1] - padding,
                            position[0] + logo.width + padding,
                            position[1] + logo.height + padding
                        ],
                        radius=12,
                        fill="white"
                    )

                    qr_image.paste(
                        logo,
                        position,
                        logo
                    )

                # Convert image to bytes

                image_buffer = BytesIO()

                qr_image.save(
                    image_buffer,
                    format="PNG"
                )

                qr_bytes = image_buffer.getvalue()

                # Save latest QR

                st.session_state.qr_image = qr_bytes

                st.session_state.payment_link = payment_link

                # Save history

                history_record = {
                    "name": payee_name.strip(),
                    "upi_id": upi_id.strip(),
                    "amount": amount,
                    "date": datetime.now().strftime(
                        "%d-%m-%Y %I:%M %p"
                    ),
                    "image": qr_bytes,
                    "payment_link": payment_link
                }

                st.session_state.qr_history.insert(
                    0,
                    history_record
                )

                st.success("QR Code generated successfully!")

            except Exception as error:

                st.error(f"QR Generation failed: {error}")

    # -------------------------------------
    # QR PREVIEW
    # -------------------------------------

    with right:

        with st.container(border=True):

            st.subheader("QR Preview")

            if st.session_state.qr_image is not None:

                st.image(
                    st.session_state.qr_image,
                    use_container_width=True
                )

                st.success("QR Code Ready!")

                st.download_button(
                    "⬇ Download QR Code",
                    data=st.session_state.qr_image,
                    file_name="UPI_STUDIO_QR.png",
                    mime="image/png",
                    use_container_width=True
                )

                st.caption(
                    "Scan using a compatible UPI application."
                )

            else:

                st.info(
                    "Your customized QR Code will appear here."
                )


# =========================================
# 8. LIVE QR SCANNER
# =========================================

class QRVideoProcessor(VideoProcessorBase):

    def __init__(self):

        self.detector = cv2.QRCodeDetector()

        self.result = None

        self.lock = threading.Lock()

    def recv(self, frame):

        image = frame.to_ndarray(format="bgr24")

        data, points, _ = self.detector.detectAndDecode(image)

        if points is not None:

            points = points.astype(int)

            for i in range(4):

                cv2.line(
                    image,
                    tuple(points[0][i]),
                    tuple(points[0][(i + 1) % 4]),
                    (0, 255, 150),
                    3
                )

        if data:

            with self.lock:
                self.result = data

            cv2.putText(
                image,
                "QR DETECTED",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 150),
                2
            )

        return av.VideoFrame.from_ndarray(
            image,
            format="bgr24"
        )


# =========================================
# 9. SCANNER TAB
# =========================================

with scanner_tab:

    st.markdown(
        '<div class="section-title">Smart QR Scanner</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Scan QR codes using your live camera or upload an image.'
        '</div>',
        unsafe_allow_html=True
    )

    # -------------------------------------
    # LIVE CAMERA
    # -------------------------------------

    st.subheader("📷 Live Camera Scanner")

    st.info(
        "Press START to activate the camera. "
        "Press STOP to deactivate it."
    )

    rtc_configuration = RTCConfiguration({
        "iceServers": [
            {
                "urls": ["stun:stun.l.google.com:19302"]
            }
        ]
    })

    webrtc_ctx = webrtc_streamer(
        key="upi-live-scanner",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        video_processor_factory=QRVideoProcessor,
        media_stream_constraints={
            "video": True,
            "audio": False
        },
        async_processing=True
    )

    if webrtc_ctx.state.playing and webrtc_ctx.video_processor:

        processor = webrtc_ctx.video_processor

        with processor.lock:
            scanned_data = processor.result

        if scanned_data:

            st.success("QR Code detected successfully!")

            st.subheader("Scanned Information")

            st.code(scanned_data)

            if scanned_data.startswith("upi://pay?"):

                st.info(
                    "UPI Payment QR detected. "
                    "Verify recipient details in your UPI app "
                    "before making payment."
                )

            if st.button("Clear Scanned Result"):

                with processor.lock:
                    processor.result = None

                st.rerun()

    # -------------------------------------
    # IMAGE UPLOAD SCANNER
    # -------------------------------------

    st.divider()

    st.subheader("📁 Scan QR From Image")

    uploaded_file = st.file_uploader(
        "Upload QR Image",
        type=["png", "jpg", "jpeg"],
        key="advanced_scanner_upload"
    )

    if uploaded_file is not None:

        try:

            image = Image.open(uploaded_file).convert("RGB")

            image_array = np.array(image)

            image_bgr = cv2.cvtColor(
                image_array,
                cv2.COLOR_RGB2BGR
            )

            detector = cv2.QRCodeDetector()

            data, points, _ = detector.detectAndDecode(
                image_bgr
            )

            if data:

                st.success("QR Code detected!")

                st.code(data)

                if data.startswith("upi://pay?"):

                    st.info(
                        "UPI payment QR detected. "
                        "Verify details before payment."
                    )

            else:

                st.error("QR Code not found in this image.")

        except Exception as error:

            st.error(f"Scanning failed: {error}")


# =========================================
# 10. QR HISTORY
# =========================================

with history_tab:

    st.markdown(
        '<div class="section-title">QR History</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Manage your previously generated UPI QR codes.'
        '</div>',
        unsafe_allow_html=True
    )

    history = st.session_state.qr_history

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total QR Generated",
            len(history)
        )

    with col2:

        st.metric(
            "Saved QR Records",
            len(history)
        )

    st.divider()

    if history:

        if st.button("🗑 Clear All History"):

            st.session_state.qr_history = []

            st.rerun()

        st.write("### Previously Generated QR Codes")

        for index, record in enumerate(history):

            with st.container(border=True):

                left, right = st.columns([2, 1])

                with left:

                    st.markdown(
                        f"### {record['name']}"
                    )

                    st.write(
                        f"**UPI ID:** {record['upi_id']}"
                    )

                    if record["amount"] > 0:

                        st.write(
                            f"**Amount:** ₹{record['amount']:.2f}"
                        )

                    else:

                        st.write(
                            "**Amount:** Not specified"
                        )

                    st.caption(
                        f"Generated: {record['date']}"
                    )

                    st.code(
                        record["payment_link"]
                    )

                with right:

                    st.image(
                        record["image"],
                        width=160
                    )

                    st.download_button(
                        "⬇ Download QR",
                        data=record["image"],
                        file_name=f"UPI_QR_{index + 1}.png",
                        mime="image/png",
                        key=f"history_download_{index}"
                    )

    else:

        st.info(
            "No QR history available. "
            "Generate your first QR code to see it here."
        )


# =========================================
# 11. FOOTER
# =========================================

st.markdown(
    "<div class='footer'>"
    "UPI STUDIO © 2026<br><br>"
    "Designed for smarter digital experiences."
    "</div>",
    unsafe_allow_html=True
)