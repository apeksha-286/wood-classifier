import streamlit as st
import json
import os

st.set_page_config(
    page_title="Wood Species Classification",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- BACKGROUND ----------------
def set_bg():
    image_url = "https://images.unsplash.com/photo-1542202229-7d93c33f5d07?q=80&w=870&auto=format&fit=crop"

    st.markdown(
        f"""
        <style>

        [data-testid="stSidebarNav"] {{display: none !important;}}
        [data-testid="stSidebar"] {{display: none !important;}}

        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.25);
        }}

        .main {{
            position: relative;
            z-index: 1;
        }}

        /* Navbar buttons */
        div.stButton > button {{
            height:40px;
            width:110px;
            font-size:16px;
            border-radius:6px;
            background-color:white;
            color:black;
            border:2px solid #2e7d32;
            font-weight:bold;
        }}

        div.stButton > button:hover {{
            background-color:#2e7d32;
            color:white;
        }}

        /* Login card */
        .login-card {{
            background:rgba(0,0,0,0.75);
            padding:35px 25px;
            border-radius:15px;
            box-shadow:0px 10px 30px rgba(0,0,0,0.5);
        }}

        .card-subtitle {{
            text-align:center;
            color:white;
            margin-bottom:20px;
        }}

        .stTextInput > label {{
            color:white !important;
            font-weight:500;
        }}

        /* Fix login card buttons */
        div[data-testid="column"] div.stButton > button {{
            width:100% !important;
            height:45px !important;
            font-size:13px !important;
            padding:4px 6px !important;
            white-space:normal !important;
            word-wrap:break-word !important;
            line-height:1.2 !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# ---------------- NAVBAR ----------------
col1,col2,col3,col4,col5,col6 = st.columns([0.2,0.6,0.6,0.6,0.6,3])

with col2:
    if st.button("Home"):
        st.switch_page("app.py")

with col3:
    if st.button("About"):
        st.switch_page("app.py")

with col4:
    if st.button("Admin"):
        st.switch_page("pages/3_admin.py")

with col5:
    if st.button("Login"):
        pass

st.write("")
st.write("")

# ---------------- HERO TEXT ----------------

st.markdown(
"""
<h2 style='text-align:left; color:white; font-weight:600; margin-left:40px; font-size:22px;'>
Discover the Life of Trees:
</h2>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<h1 style='text-align:center; color:white; font-size:36px; font-weight:bold;'>
Welcome to Wood Species Classification System
</h1>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<p style='text-align:center; color:white; font-size:18px; font-style:italic;'>
"Every tree is unique, every bark has a story".
</p>
""",
unsafe_allow_html=True
)

st.write("")
st.write("")

# ---------------- USER FILE ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE = os.path.join(BASE_DIR,"..","users.json")

if not os.path.exists(USER_FILE):
    with open(USER_FILE,"w") as f:
        json.dump({},f)

def load_users():
    with open(USER_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USER_FILE,"w") as f:
        json.dump(data,f,indent=4)

# ---------------- SESSION ----------------
if "mode" not in st.session_state:
    st.session_state.mode="login"

# ---------------- LOGIN CARD ----------------
left,center,right = st.columns([1.5,2,1.5])

with center:

    st.markdown('<div class="login-card">',unsafe_allow_html=True)

    if st.session_state.mode=="login":

        st.markdown('<div class="card-subtitle">Login to your account</div>',unsafe_allow_html=True)

        username = st.text_input("Enter your name or email")
        password = st.text_input("Password",type="password")

        st.write("")

        c1,c2,c3 = st.columns(3)

        with c1:
            if st.button("Sign In", use_container_width=True):
                users = load_users()
                if username in users and users[username]==password:
                    st.session_state.logged_user=username
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Invalid credentials")

        with c2:
            if st.button("Forgot Password", use_container_width=True):
                st.warning("Reset feature coming soon")

        with c3:
            if st.button("New user? Sign up", use_container_width=True):
                st.session_state.mode="signup"
                st.rerun()

    elif st.session_state.mode=="signup":

        st.markdown('<div class="card-subtitle">Create new account</div>',unsafe_allow_html=True)

        new_user = st.text_input("Enter your name or email")
        new_pass = st.text_input("Password",type="password")

        st.write("")

        c1,c2 = st.columns(2)

        with c1:
            if st.button("Register", use_container_width=True):
                users = load_users()
                if new_user in users:
                    st.error("User already exists")
                else:
                    users[new_user]=new_pass
                    save_users(users)
                    st.success("Account created successfully!")
                    st.session_state.mode="login"
                    st.rerun()

        with c2:
            if st.button("Back", use_container_width=True):
                st.session_state.mode="login"
                st.rerun()

    st.markdown('</div>',unsafe_allow_html=True)