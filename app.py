import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from gmail_send import send_email
from db import init_db, save_email, get_emails, delete_email

# INIT
load_dotenv()
init_db()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Email Writer", layout="wide")
st.markdown("## ✉️ AI Email Writer")

# SESSION STATE (STRICT CONTROL)
for key in ["prompt", "recipient", "email_body"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# LAYOUT
col1, col2 = st.columns([2, 1])

# ================= LEFT: COMPOSE =================
with col1:
    st.subheader("📝 Compose Email")

    st.session_state.prompt = st.text_area(
        "Email Instruction",
        value=st.session_state.prompt,
        placeholder="Write a professional leave request email"
    )

    st.session_state.recipient = st.text_input(
        "Recipient Email",
        value=st.session_state.recipient
    )

    if st.button("⚡ Generate Email"):
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": "Write professional business emails."},
                {"role": "user", "content": st.session_state.prompt}
            ]
        )
        st.session_state.email_body = response.output_text

        save_email(
            st.session_state.recipient,
            "Draft",
            st.session_state.email_body,
            "draft"
        )

    st.session_state.email_body = st.text_area(
        "Email Content",
        value=st.session_state.email_body,
        height=250
    )

    if st.button("📤 Send Email"):
        send_email(
            st.session_state.recipient,
            "Official Communication",
            st.session_state.email_body
        )

        save_email(
            st.session_state.recipient,
            "Official Communication",
            st.session_state.email_body,
            "sent"
        )

        # HARD RESET — REQUIREMENT #2
        st.session_state.prompt = ""
        st.session_state.recipient = ""
        st.session_state.email_body = ""

        st.success("Email sent successfully")

# ================= RIGHT: HISTORY =================
with col2:
    st.subheader("📜 Email History")

    tab1, tab2 = st.tabs(["📨 Sent", "📝 Drafts"])

    with tab1:
        for email_id, r, s, b, t in get_emails("sent"):
            st.markdown(f"**To:** {r}")
            st.caption(t)
            st.caption(b[:120] + "...")
            if st.button("🗑 Delete", key=f"sent_{email_id}"):
                delete_email(email_id)
                st.experimental_rerun()

    with tab2:
        for email_id, r, s, b, t in get_emails("draft"):
            st.markdown(f"**Draft for:** {r}")
            st.caption(t)
            st.caption(b[:120] + "...")
            if st.button("🗑 Delete", key=f"draft_{email_id}"):
                delete_email(email_id)
                st.experimental_rerun()


# FOOTER
# ======================
st.markdown(
    """
    <div class="glass" style="text-align:center;">
        <p>Developed by @MOHAN KODURU </p>
    </div>
    """,
    unsafe_allow_html=True
)
