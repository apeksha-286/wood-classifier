import streamlit as st
import os
import shutil
import pandas as pd
import zipfile
import tempfile

st.set_page_config(page_title="Admin Panel", layout="centered")

# ================= STYLE =================
st.markdown("""
<style>

[data-testid="stSidebarNav"] {display: none !important;}
[data-testid="stSidebar"] {display: none !important;}

.card{
background:rgba(0,0,0,0.75);
padding:30px;
border-radius:15px;
}

h1,h2,h3,h4,h5,h6{ color:white !important; }
label,span,p{ color:white !important; }

div.stButton > button{
background-color:rgba(0,0,0,0.8);
color:white;
border-radius:10px;
height:40px;
font-weight:bold;
}

div.stButton > button:hover{ background-color:#2e7d32; }

[data-testid="stMetricValue"]{ color:white !important; font-size:32px; font-weight:bold; }
[data-testid="stMetricLabel"]{ color:white !important; font-size:18px; }

[data-testid="stFileUploader"]{ background:rgba(0,0,0,0.55); padding:15px; border-radius:10px; }
[data-testid="stFileUploader"] section{ background:transparent !important; }
[data-testid="stFileUploader"] p{ color:white !important; font-size:16px; font-weight:500; }
[data-testid="stFileUploader"] small{ color:#dcdcdc !important; font-size:13px; }
[data-testid="stFileUploader"] span{ color:white !important; }
[data-testid="stFileUploader"] button{ background:white !important; color:black !important; font-weight:bold; border-radius:6px; }

</style>
""", unsafe_allow_html=True)

# ================= BACKGROUND =================
def set_bg():
    image_url = "https://images.unsplash.com/photo-1507041957456-9c397ce39c97?auto=format&fit=crop&w=3000&q=60"
    st.markdown(f"""
        <style>
        .stApp {{ background-image:url("{image_url}"); background-size:cover; background-position:center; background-attachment:fixed; }}
        .stApp::before {{ content:""; position:fixed; inset:0; background:rgba(0,0,0,0.45); z-index:-1; }}
        </style>
        """, unsafe_allow_html=True)

set_bg()

# ================= PATHS =================
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_PATH  = os.path.join(BASE_DIR, "pending_uploads")
APPROVED_PATH = os.path.join(BASE_DIR, "approved_uploads")
DATASET_PATH  = os.path.join(BASE_DIR, "dataset", "wood_species")

os.makedirs(PENDING_PATH,  exist_ok=True)
os.makedirs(APPROVED_PATH, exist_ok=True)

# ================= ADMIN CREDENTIALS =================
ADMIN_USER = st.secrets["admin"]["username"]
ADMIN_PASS = st.secrets["admin"]["password"]

# ================= SESSION =================
if "admin_logged" not in st.session_state: st.session_state.admin_logged = False
if "current_user" not in st.session_state: st.session_state.current_user = ADMIN_USER
if "current_pass" not in st.session_state: st.session_state.current_pass = ADMIN_PASS

# ==================================================
# LOGIN
# ==================================================
if not st.session_state.admin_logged:

    if st.button("⬅ Back to Home"):
        st.switch_page("app.py")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🔐 Admin Panel")
        st.subheader("Admin Login")

        user = st.text_input("Username")
        pw   = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if user == st.session_state.current_user and pw == st.session_state.current_pass:
                st.session_state.admin_logged = True
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Wrong credentials")

        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# DASHBOARD
# ==================================================
else:

    # ===== TOP BUTTONS =====
    c1, c2, c3 = st.columns([1,1,4])
    with c1:
        if st.button("⬅ Back to Home"):
            st.switch_page("app.py")
    with c2:
        if st.button("🚪 Logout"):
            st.session_state.admin_logged = False
            st.rerun()

    st.title("🛠 Admin Dashboard")

    # ===== DATASET STATS =====
    st.subheader("📊 Dataset Statistics")

    species_counts = {}
    total_images   = 0

    if os.path.exists(DATASET_PATH):
        for sp in sorted(os.listdir(DATASET_PATH)):
            sp_path = os.path.join(DATASET_PATH, sp)
            if os.path.isdir(sp_path):
                imgs = [i for i in os.listdir(sp_path) if i.lower().endswith((".jpg",".jpeg",".png"))]
                species_counts[sp] = len(imgs)
                total_images += len(imgs)

    pending_count = 0
    for sp in os.listdir(PENDING_PATH):
        sp_path = os.path.join(PENDING_PATH, sp)
        if os.path.isdir(sp_path):
            pending_count += len([i for i in os.listdir(sp_path) if i.lower().endswith((".jpg",".jpeg",".png"))])

    approved_count = 0
    for sp in os.listdir(APPROVED_PATH):
        sp_path = os.path.join(APPROVED_PATH, sp)
        if os.path.isdir(sp_path):
            approved_count += len([i for i in os.listdir(sp_path) if i.lower().endswith((".jpg",".jpeg",".png"))])

    # also count dataset extra images added this session
    dataset_total = total_images

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Species",  len(species_counts))
    col2.metric("Total Images",   dataset_total)
    col3.metric("Pending",        pending_count)
    col4.metric("Approved",       approved_count)

    if species_counts:
        df = pd.DataFrame(list(species_counts.items()), columns=["Species","Images"])
        st.bar_chart(df.set_index("Species"))

    # ===== IMAGE UPLOAD =====
    st.subheader("➕ Upload Images")

    species_list = sorted([d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))])

    option = st.radio("Select Option", ["Existing Species","Create New Species"])

    if option == "Existing Species":
        species_name = st.selectbox("Select Species", species_list)
    else:
        species_name = st.text_input("Enter New Species Name")

    uploaded_files = st.file_uploader("Upload Image(s) or ZIP file", type=["jpg","jpeg","png","zip"], accept_multiple_files=True)

    if st.button("Upload Files"):
        if uploaded_files and species_name:
            folder = os.path.join(PENDING_PATH, species_name.strip())
            os.makedirs(folder, exist_ok=True)
            for file in uploaded_files:
                if file.name.lower().endswith(".zip"):
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(file.read())
                        tmp_path = tmp.name
                    with zipfile.ZipFile(tmp_path, "r") as zf:
                        zf.extractall(folder)
                else:
                    with open(os.path.join(folder, file.name), "wb") as f:
                        f.write(file.getbuffer())
            st.success("Images uploaded successfully ✅")
            st.rerun()

    # ===== PENDING IMAGES =====
    st.markdown("---")
    st.subheader("📥 Pending Images — Waiting for Approval")

    pending_species = sorted([d for d in os.listdir(PENDING_PATH) if os.path.isdir(os.path.join(PENDING_PATH, d))])

    if not pending_species:
        st.info("No pending images.")
    else:
        for species in pending_species:
            sp_path = os.path.join(PENDING_PATH, species)
            images  = sorted([i for i in os.listdir(sp_path) if i.lower().endswith((".jpg",".jpeg",".png"))])
            if not images: continue

            st.markdown(f"### 🌳 {species}")

            for img in images:
                img_path = os.path.join(sp_path, img)
                col1, col2, col3, col4 = st.columns([3,1,1,1])

                with col1:
                    st.image(img_path, width=200, caption=img)

                with col2:
                    if st.button("✅ Approve", key=f"app_{species}_{img}"):
                        # Move to approved folder AND copy to dataset
                        approved_sp = os.path.join(APPROVED_PATH, species)
                        dataset_sp  = os.path.join(DATASET_PATH, species)
                        os.makedirs(approved_sp, exist_ok=True)
                        os.makedirs(dataset_sp,  exist_ok=True)
                        # Copy to dataset
                        shutil.copy(img_path, os.path.join(dataset_sp, img))
                        # Move to approved
                        shutil.move(img_path, os.path.join(approved_sp, img))
                        st.success(f"✅ {img} approved and saved to dataset!")
                        st.rerun()

                with col3:
                    if st.button("👁 View", key=f"vpend_{species}_{img}"):
                        st.image(img_path, width=500, caption=img)

                with col4:
                    if st.button("🗑 Delete", key=f"dpend_{species}_{img}"):
                        os.remove(img_path)
                        st.warning(f"🗑 {img} deleted!")
                        st.rerun()

    # ===== APPROVED IMAGES =====
    st.markdown("---")
    st.subheader("✅ Approved Images")
    st.caption("These images have been approved and saved to dataset. You can view or delete them here.")

    approved_species = sorted([d for d in os.listdir(APPROVED_PATH) if os.path.isdir(os.path.join(APPROVED_PATH, d))])

    if not approved_species:
        st.info("No approved images yet.")
    else:
        for species in approved_species:
            sp_path = os.path.join(APPROVED_PATH, species)
            images  = sorted([i for i in os.listdir(sp_path) if i.lower().endswith((".jpg",".jpeg",".png"))])
            if not images: continue

            st.markdown(f"### 🌳 {species}")

            for img in images:
                img_path = os.path.join(sp_path, img)
                col1, col2, col3 = st.columns([3,1,1])

                with col1:
                    st.image(img_path, width=200, caption=img)

                with col2:
                    if st.button("👁 View", key=f"vappr_{species}_{img}"):
                        st.image(img_path, width=500, caption=img)

                with col3:
                    if st.button("🗑 Delete", key=f"dappr_{species}_{img}"):
                        # Delete from approved AND from dataset
                        os.remove(img_path)
                        dataset_img = os.path.join(DATASET_PATH, species, img)
                        if os.path.exists(dataset_img):
                            os.remove(dataset_img)
                        st.warning(f"🗑 {img} deleted from approved and dataset!")
                        st.rerun()

    # ===== CHANGE USERNAME =====
    st.markdown("---")
    st.subheader("👤 Change Username")
    with st.expander("Click to change username"):
        new_username = st.text_input("Enter New Username", key="new_username")
        confirm_pass = st.text_input("Confirm Current Password", type="password", key="confirm_pass_user")
        if st.button("Update Username"):
            if confirm_pass == st.session_state.current_pass:
                if new_username.strip() == "":
                    st.error("Username cannot be empty!")
                else:
                    st.session_state.current_user = new_username.strip()
                    st.success(f"Username changed to: {new_username.strip()} ✅")
            else:
                st.error("Wrong current password!")

    # ===== CHANGE PASSWORD =====
    st.markdown("---")
    st.subheader("🔑 Change Password")
    with st.expander("Click to change password"):
        current_pass_input = st.text_input("Enter Current Password", type="password", key="current_pass_input")
        new_pass           = st.text_input("Enter New Password",      type="password", key="new_pass")
        confirm_new_pass   = st.text_input("Confirm New Password",    type="password", key="confirm_new_pass")
        if st.button("Update Password"):
            if current_pass_input != st.session_state.current_pass:
                st.error("Current password is wrong!")
            elif new_pass.strip() == "":
                st.error("New password cannot be empty!")
            elif new_pass != confirm_new_pass:
                st.error("New passwords do not match!")
            else:
                st.session_state.current_pass = new_pass
                st.success("Password changed successfully ✅")