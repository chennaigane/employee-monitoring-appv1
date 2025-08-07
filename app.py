import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime
import matplotlib.pyplot as plt
import io

# Simulated app and website pool
apps = ["Chrome", "Excel", "Slack", "Outlook", "VS Code", "YouTube"]
websites = ["gmail.com", "github.com", "stackoverflow.com", "linkedin.com", "youtube.com"]

if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.logs = []
    st.session_state.idle_time = 0
    st.session_state.start_time = None

st.title("🖥️ Employee Time & Activity Tracker")

user_type = st.sidebar.selectbox("Login as", ["Employee", "Admin"])
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if user_type == "Admin" and username == "admin" and password == "admin123":
        st.success("Logged in as Admin")
        st.session_state.user_type = "Admin"
    elif user_type == "Employee" and username and password:
        st.success(f"Logged in as {username}")
        st.session_state.user_type = username
    else:
        st.error("Invalid credentials")

if "user_type" in st.session_state and st.session_state.user_type != "Admin":
    st.subheader(f"Welcome, {st.session_state.user_type}")
    if not st.session_state.started:
        if st.button("▶️ Start Tracking"):
            st.session_state.started = True
            st.session_state.start_time = time.time()
            st.success("Monitoring started...")
    else:
        if st.button("⏹ Stop Tracking"):
            st.session_state.started = False
            st.success("Monitoring stopped.")

    if st.session_state.started:
        for _ in range(5):
            activity_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            app = random.choice(apps)
            website = random.choice(websites)
            duration = random.randint(1, 5)
            idle = random.choice([0, 1])
            st.session_state.logs.append({
                "timestamp": activity_time,
                "application": app,
                "website": website,
                "duration_min": duration,
                "idle": idle
            })
            st.session_state.idle_time += duration if idle else 0
        time.sleep(1)

    if len(st.session_state.logs) > 0:
        df = pd.DataFrame(st.session_state.logs)
        prod_time = df[df['idle'] == 0]['duration_min'].sum()
        idle_time = df[df['idle'] == 1]['duration_min'].sum()
        st.subheader("🕒 Time Distribution")
        fig, ax = plt.subplots()
        ax.pie([prod_time, idle_time], labels=["Productive", "Idle"], autopct="%1.1f%%")
        st.pyplot(fig)
        st.dataframe(df)

elif "user_type" in st.session_state and st.session_state.user_type == "Admin":
    st.subheader("Admin Dashboard")
    logs = st.session_state.logs if "logs" in st.session_state else []
    if logs:
        df = pd.DataFrame(logs)
        st.write("All employee activity logs:")
        st.dataframe(df)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Activity Logs')
            writer.save()
        st.download_button("📥 Download Excel Report", data=buffer.getvalue(), file_name="activity_logs.xlsx")
        st.subheader("🔍 Filter By")
        for emp in df["application"].unique():
            sub_df = df[df["application"] == emp]
            st.write(f"**{emp} - Total Usage**: {sub_df['duration_min'].sum()} min")
