import streamlit as st
import os
import zipfile

# ================= CUSTOM CSS =================
st.markdown("""
<style>
/* Sidebar fix */
[data-testid="stSidebarNav"] ul li:nth-child(2) { display:none; }
section[data-testid="stSidebar"] { opacity:1 !important; position:relative; z-index:100; }

/* Dashboard buttons */
div.stButton > button {
    height:65px !important;
    font-size:20px !important;
    font-weight:800 !important;
    border-radius:12px !important;
    padding:14px 24px !important;
}

/* Logout button */
button[kind="secondary"]{
    font-size:18px !important;
    padding:12px 22px !important;
}

/* White card for species options */
.species-card {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    color: black;
    margin-bottom: 20px;
}

/* Horizontal radio buttons */
.stRadio > div[role="radiogroup"] {
    display: flex;
    gap: 20px;
}

/* Radio button styling */
.species-card .stRadio label {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: black !important;
}

/* Selectbox and text input inside card */
.species-card .stSelectbox > div, .species-card input[type="text"] {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: black !important;
    background-color: white !important;
}

/* File uploader inside card */
.species-card .stFileUploader {
    font-size: 18px !important;
    color: black !important;
}

/* Image captions */
.stImage img { border-radius:12px !important; border:3px solid #fff !important; }
.stImage figcaption { font-size:16px !important; font-weight:600 !important; color:black !important; }

/* Headings */
h1,h2,h3,h4,h5,h6{ font-weight:700 !important; color:black !important; }
.welcome-text{ font-size:28px !important; font-weight:700 !important; color:black; }
</style>
""", unsafe_allow_html=True)

# ================= BACKGROUND IMAGE =================
def set_bg():
    image_url = "https://img.pikbest.com/photo/20251013/misty-forest-with-sunlight-filtering-through-tall-trees-dreamy-cinematic-nature-scene_11940012.jpg%21w700wp"
    st.markdown(f"""
    <style>
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
        background: rgba(0,0,0,0.35);
        z-index: -1;
    }}
    .main .block-container {{
        background: rgba(255,255,255,0.90);
        padding: 2rem;
        border-radius: 15px;
    }}
    h1,h2,h3,p,label,span {{ color:black !important; }}
    </style>
    """, unsafe_allow_html=True)

set_bg()

# ================= LOGIN PROTECTION =================
if "logged_user" not in st.session_state or st.session_state.logged_user is None:
    st.switch_page("app.py")

# ================= LOGOUT BUTTON =================
col_logout, col_space = st.columns([1,5])
with col_logout:
    if st.button("🚪 Logout"):
        st.session_state.logged_user = None
        st.switch_page("app.py")

# ================= TITLE =================
st.title("📊 Dashboard")
st.markdown(f"<div class='welcome-text'>Welcome, {st.session_state.logged_user}</div>", unsafe_allow_html=True)

# ================= DATASET PATH =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "wood_species")

if not os.path.exists(DATASET_PATH):
    st.error("Dataset folder not found ❌")
    st.stop()

# ================= DASHBOARD OPTIONS =================
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("1️⃣ Upload Extra Images"): st.session_state.option = "upload"
if col2.button("2️⃣ Classify Images"): st.switch_page("pages/2_classify.py")
if col3.button("3️⃣ Download Full Dataset"): st.session_state.option = "download_all"
if col4.button("4️⃣ Download Species Images"): st.session_state.option = "download_one"
if col5.button("5️⃣ Recent Uploads"): st.session_state.option = "recent_uploads"

# ================= OPTION 1 : UPLOAD =================
if st.session_state.get("option") == "upload":

    st.subheader("📤 Upload Extra Images to Extend Dataset")

    classes = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))]

    # ===== White Box =====
    st.markdown('<div class="species-card">', unsafe_allow_html=True)

    st.markdown("<h3 style='font-size:22px; font-weight:700;'>🌳 Choose Species Option</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Existing Species"):
            st.session_state.species_choice = "Existing Species"

    with col2:
        if st.button("Create New Species"):
            st.session_state.species_choice = "Create New Species"

    species_choice = st.session_state.get("species_choice", None)

    selected = None

    if species_choice == "Existing Species":
        selected = st.selectbox("Select Species", classes)

    elif species_choice == "Create New Species":
        new_species = st.text_input("Enter New Species Name")
        if new_species:
            selected = new_species.strip()

    files = st.file_uploader(
        "Upload Images or ZIP File",
        type=["jpg","jpeg","png","zip"],
        accept_multiple_files=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ===== Upload Handling =====
    if files and selected:
        pending_path = os.path.join(BASE_DIR, "pending_uploads", selected)
        os.makedirs(pending_path, exist_ok=True)

        saved_count = 0

        for f in files:
            if f.name.lower().endswith(".zip"):
                with zipfile.ZipFile(f, "r") as zip_ref:
                    zip_ref.extractall(pending_path)
                    saved_count += len(zip_ref.namelist())
            else:
                save_path = os.path.join(pending_path, f.name)
                with open(save_path, "wb") as save:
                    save.write(f.getbuffer())
                saved_count += 1

        st.success(f"{saved_count} images uploaded for admin approval ✅")
        # ================= OPTION 3 : DOWNLOAD FULL DATASET =================
# ================= OPTION 3 : DOWNLOAD FULL DATASET =================
if st.session_state.get("option") == "download_all":

    st.subheader("📥 Download Complete Dataset")

    # ✅ Calculate first
    species_list = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))]
    total_species = len(species_list)

    total_images = sum(
        len([
            f for f in os.listdir(os.path.join(DATASET_PATH, s))
            if f.lower().endswith((".jpg",".jpeg",".png"))
        ])
        for s in species_list
    )

    # ✅ Show stats (NOW it will work)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="
            background:#2e7d32;
            padding:20px;
            border-radius:12px;
            text-align:center;
            color:white;
            font-size:22px;
            font-weight:bold;
        ">
        🌳 Total Species<br>{total_species}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background:#1565c0;
            padding:20px;
            border-radius:12px;
            text-align:center;
            color:white;
            font-size:22px;
            font-weight:bold;
        ">
        🖼 Total Images<br>{total_images}
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ✅ Download ZIP
    zip_path = os.path.join(BASE_DIR, "wood_species_full.zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(DATASET_PATH):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, os.path.relpath(full_path, DATASET_PATH))

    with open(zip_path, "rb") as f:
        st.download_button("⬇ Download Full Dataset ZIP", f, file_name="wood_species_dataset.zip")

# ================= OPTION 4 : DOWNLOAD SPECIES =================
if st.session_state.get("option") == "download_one":

    st.subheader("📥 Download Images of Selected Species")

    classes = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH,d))]
    selected = st.selectbox("Select Species to Download", classes)

    species_path = os.path.join(DATASET_PATH, selected)
    images = [f for f in os.listdir(species_path) if f.lower().endswith((".jpg",".jpeg",".png"))]

    # ✅ Highlight Total Images
    st.markdown(f"""
    <div style="
        background:#1565c0;
        color:white;
        padding:15px;
        border-radius:10px;
        font-size:20px;
        font-weight:bold;
        text-align:center;
        margin-bottom:15px;
    ">
    📷 Total Images in {selected}: {len(images)}
    </div>
    """, unsafe_allow_html=True)

    if images:

        st.markdown("### 📄 Image Files")

        # ✅ Scrollable container
        st.markdown('<div style="max-height:400px; overflow-y:auto;">', unsafe_allow_html=True)

        for img in images:
            colA, colB = st.columns([5,1])

            with colA:
                st.markdown(f"""
             <div style="
            font-size:20px;
            font-weight:600;
            color:#000000;
            padding:6px 0px;
            ">
            📷 {img}
            </div>
            """, unsafe_allow_html=True)

            with colB:
                img_path = os.path.join(species_path, img)
                with open(img_path, "rb") as file:
                    st.download_button(
                        "⬇",
                        file,
                        file_name=img,
                        mime="image/jpeg",
                        key=f"download_{img}"
                    )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # ✅ ZIP DOWNLOAD (Styled)
        st.markdown("### 📦 Download Entire Species as ZIP")

        zip_path = os.path.join(BASE_DIR, f"{selected}.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img in images:
                full_path = os.path.join(species_path, img)
                zipf.write(full_path, img)

        with open(zip_path, "rb") as f:
            st.download_button(
                f"⬇ Download {selected}.zip",
                f,
                file_name=f"{selected}.zip",
                mime="application/zip"
            )

    else:
        st.warning("No images found in this species.")
# ================= OPTION 5 : RECENT UPLOADS =================
if st.session_state.get("option") == "recent_uploads":
    st.subheader("🖼 Recent Uploads")
    PENDING_PATH = os.path.join(BASE_DIR, "pending_uploads")
    APPROVED_PATH = os.path.join(BASE_DIR, "approved_uploads")
    os.makedirs(PENDING_PATH, exist_ok=True)
    os.makedirs(APPROVED_PATH, exist_ok=True)

    # -------- PENDING --------
    st.markdown("## ⏳ Pending Uploads")
    pending_species = [d for d in os.listdir(PENDING_PATH) if os.path.isdir(os.path.join(PENDING_PATH, d))]
    if not pending_species: st.info("No pending uploads.")
    else:
        for species in pending_species:
            species_path = os.path.join(PENDING_PATH, species)
            images = [img for img in os.listdir(species_path) if img.lower().endswith((".jpg",".jpeg",".png"))]
            st.markdown(f"### 🌳 {species}")
            for img in images:
                img_path = os.path.join(species_path, img)
                col1, col2, col3 = st.columns([2,1,1])
                with col1: st.image(img_path, width=150, caption=img)
                with col2:
                    if st.button("✅ Approve", key=f"approve_{species}_{img}"):
                        approved_species_path = os.path.join(APPROVED_PATH, species)
                        os.makedirs(approved_species_path, exist_ok=True)
                        os.rename(img_path, os.path.join(approved_species_path, img))
                        st.success(f"{img} approved!")
                        st.rerun()
                with col3:
                    if st.button("🗑 Delete", key=f"del_pending_{species}_{img}"):
                        os.remove(img_path)
                        st.success("Deleted!")
                        st.rerun()

    # -------- APPROVED --------
    st.markdown("---")
    st.markdown("## ✅ Approved Uploads")
    approved_species = [d for d in os.listdir(APPROVED_PATH) if os.path.isdir(os.path.join(APPROVED_PATH, d))]
    if not approved_species: st.info("No approved uploads yet.")
    else:
        for species in approved_species:
            species_path = os.path.join(APPROVED_PATH, species)
            images = [img for img in os.listdir(species_path) if img.lower().endswith((".jpg",".jpeg",".png"))]
            st.markdown(f"### 🌳 {species}")
            for img in images:
                img_path = os.path.join(species_path, img)
                col1, col2, col3, col4 = st.columns([2,1,1,1])
                with col1: st.image(img_path, width=150, caption=img)
                with col2:
                    if st.button("💾 Save", key=f"save_{species}_{img}"):
                        dataset_species_path = os.path.join(DATASET_PATH, species)
                        os.makedirs(dataset_species_path, exist_ok=True)
                        os.rename(img_path, os.path.join(dataset_species_path, img))
                        st.success("Saved to dataset!")
                        st.rerun()
                with col3:
                    if st.button("👁 View", key=f"view_{species}_{img}"):
                        st.image(img_path, width=400)
                with col4:
                    if st.button("🗑 Delete", key=f"del_{species}_{img}"):
                        os.remove(img_path)
                        st.success("Deleted!")
                        st.rerun()