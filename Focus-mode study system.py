# Importing required libraries
import streamlit as st  # For UI
from streamlit_autorefresh import st_autorefresh # For refreshing the website
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase  # For webcam
import time     # For tracking the time
import pandas as pd     # To covert the data into a format for ploting
import cv2      # For facial recognition


st.set_page_config(page_title="AI Study Focus System", layout="wide")

# Load face detector

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

class FaceDetector(VideoTransformerBase): # Setup for the webcame
    def __init__(self):
        self.face_detected = False

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:  # Checking if the student is distracted or focused
            self.face_detected = True
            label = "Focused"
            color = (0, 255, 0)
        else:
            self.face_detected = False
            label = "Distracted"
            color = (0, 0, 255)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)

        cv2.putText(img, label, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        return img

st.title("AI-Based Study Focus System")
st.write("This is a Anti-distraction system, designed to provide a distraction free environment to a student for studying and learning.")

st_autorefresh(interval=1000, key="timerrefresh") # For smooth functioning

# Session state initialization
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "focus_data" not in st.session_state:
    st.session_state.focus_data = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# Start / Stop buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Start Session"):
        st.session_state.start_time = time.time()
        st.session_state.is_running = True

with col2:
    if st.button("⏹ Stop Session"):
        st.session_state.is_running = False

st.divider()


# Timer display
if st.session_state.is_running:
    elapsed = int(time.time() - st.session_state.start_time)

    minutes = elapsed // 60
    seconds = elapsed % 60

    st.metric("⏱️ Time Studied", f"{minutes} min {seconds} sec")

    st.subheader("🎥 Live Focus Detection")

    webrtc_ctx = webrtc_streamer(
        key="example",
        video_transformer_factory=FaceDetector,
        rtc_configuration={
            "iceServers": [
                {"urls": ["stun:stun.relay.metered.ca:80"]},
                {
                    "urls": [
                        "turn:global.relay.metered.ca:80",
                        "turn:global.relay.metered.ca:80?transport=tcp",
                        "turn:global.relay.metered.ca:443",
                        "turns:global.relay.metered.ca:443?transport=tcp"
                    ],
                    "username": "c4816b6fd98531c59b6731ee",
                    "credential": "iORGIYD6bCo7X6M9"
                }
            ]
        }
    )
    })



# Convert to DataFrame
df = pd.DataFrame(st.session_state.focus_data)

# Show graph
if not df.empty:
    st.subheader("📈 Focus Tracking")
    st.line_chart(df.set_index("time"))

    # Calculate focus score
    focus_score = int(df["state"].mean() * 100)
    st.metric("🎯 Focus Score", f"{focus_score}%")

    # Burnout detection
    if len(df) > 0:
        total_time = df["time"].max()

        if total_time > 60 and focus_score < 50:
            st.error("⚠️ High Burnout Risk! Take a break.")
        elif total_time > 120:
            st.warning("⚠️ You've been studying for long. Consider a break.")
        else:
            st.success("✅ You're doing well!")

st.divider()
st.header("📝 Notes Section")

# For noting system
if "notes" not in st.session_state:
    st.session_state.notes = []


new_note = st.text_area("Write your goal / task / note:")   # Input box


if st.button("➕ Add Note"):    # Add button
    if new_note.strip() != "":
        st.session_state.notes.append(new_note)
        st.success("Note added!")


st.subheader("📌 Your Notes")   # Display notes

for i, note in enumerate(st.session_state.notes):   # Delete notes
    col1, col2 = st.columns([5, 1])

    with col1:
        st.write(f"{i+1}. {note}")

    with col2:
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.notes.pop(i)
            st.experimental_rerun()

# For suggestions
st.subheader("💡 Smart Suggestions")

if not df.empty:
    if focus_score < 50:
        st.write("- Reduce distractions (keep phone away 📵)")

    else:
        st.write("- Great focus! Maintain this consistency 💪")

    if len(df) > 0 and df["time"].max() > 90:
        st.write("- Take a 10 min break to avoid burnout 🧘")
