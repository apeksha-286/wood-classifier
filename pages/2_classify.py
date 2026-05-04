import streamlit as st
import tensorflow as tf
import numpy as np
import os
import zipfile
import tempfile
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import requests
import pandas as pd

from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mob_pre
from tensorflow.keras.applications.densenet import preprocess_input as dense_pre
from tensorflow.keras.applications.resnet import preprocess_input as res_pre


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Wood Species Classification", layout="wide")


# --------------------------------------------------
# HIDE SIDEBAR
# --------------------------------------------------
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
[data-testid="stSidebar"] {display: none !important;}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# BACKGROUND IMAGE
# --------------------------------------------------
def set_bg(image_url):
    try:
        response = requests.get(image_url, timeout=5)
        encoded = base64.b64encode(response.content).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

set_bg("https://images.unsplash.com/photo-1441974231531-c6227db76b6e")


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
.white-box {
    background: rgba(255,255,255,0.96);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
}
.section-title {
    background: white;
    padding: 12px 18px;
    border-radius: 10px;
    font-size: 22px;
    font-weight: bold;
    color: black;
    margin-bottom: 15px;
    border-left: 6px solid #2b7cff;
}
img {
    border-radius: 10px;
    border: 4px solid white;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.markdown(
    "<h1 style='color:white;text-align:center;'>🌳 Wood Species Classification System</h1>",
    unsafe_allow_html=True
)


# --------------------------------------------------
# PATH SETTINGS
# --------------------------------------------------
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "wood_species")
MODEL_DIR    = os.path.join(BASE_DIR, "models")

if not os.path.exists(DATASET_PATH):
    st.error("Dataset folder not found ❌")
    st.stop()

CLASS_NAMES = sorted([
    d for d in os.listdir(DATASET_PATH)
    if os.path.isdir(os.path.join(DATASET_PATH, d))
])


# --------------------------------------------------
# LOAD MODELS
# --------------------------------------------------
@st.cache_resource
def load_models():
    return {
        "MobileNetV2": tf.keras.models.load_model(
            os.path.join(MODEL_DIR, "mobilenetv2_trained (1).h5")
        ),
        "DenseNet121": tf.keras.models.load_model(
            os.path.join(MODEL_DIR, "densenet121_trained.h5")
        ),
        "ResNet50": tf.keras.models.load_model(
            os.path.join(MODEL_DIR, "resnet_trained.h5")
        ),
    }

models = load_models()


# --------------------------------------------------
# HELPER: predict single image array
# --------------------------------------------------
def predict_image(img_array):
    results = {}
    for model_name, model in models.items():
        if model_name == "MobileNetV2":
            x = mob_pre(img_array.copy())
        elif model_name == "DenseNet121":
            x = dense_pre(img_array.copy())
        else:
            x = res_pre(img_array.copy())
        x    = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        class_id   = np.argmax(pred)
        confidence = float(pred[0][class_id] * 100)
        results[model_name] = {
            "species":    CLASS_NAMES[class_id],
            "confidence": confidence
        }
    best = max(results, key=lambda m: results[m]["confidence"])
    return results, best


# --------------------------------------------------
# MODE SELECTOR
# --------------------------------------------------
st.markdown(
    "<h3 style='color:white;text-align:center;'>Select Classification Mode</h3>",
    unsafe_allow_html=True
)

mode = st.radio(
    "",
    ["🖼 Single Image", "📁 Batch (ZIP of images)"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")


# ==================================================
# MODE 1 — SINGLE IMAGE
# ==================================================
if mode == "🖼 Single Image":

    uploaded_file = st.file_uploader(
        "📤 Upload a Wood Bark Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        image     = Image.open(uploaded_file).convert("RGB")
        img       = image.resize((224, 224))
        img_array = np.array(img)

        st.image(image, caption="Uploaded Image", width=350)

        with st.spinner("🔍 Classifying..."):
            results, best_model = predict_image(img_array)

        confidence_scores = {m: results[m]["confidence"] for m in results}
        predictions       = {m: results[m]["species"]    for m in results}

        # ---- Confidence Chart ----
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Model Confidence Comparison</div>', unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        ax1.bar(confidence_scores.keys(), confidence_scores.values(), color=["#2e7d32","#1565c0","#b71c1c"])
        ax1.set_ylabel("Confidence (%)")
        ax1.set_ylim(0, 100)
        ax1.grid(axis="y", linestyle="--", alpha=0.6)
        st.pyplot(fig1)
        plt.close(fig1)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- Best Model ----
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏆 Best Model Prediction</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:white;padding:20px;border-radius:12px;font-size:18px;color:black;">
            🏆 <b>Best Model:</b> {best_model}<br>
            🌲 <b>Predicted Species:</b> {predictions[best_model]}<br>
            📈 <b>Confidence:</b> {confidence_scores[best_model]:.2f}%
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- Confusion Matrix ----
        y_true = [predictions[best_model]]
        y_pred = [predictions[best_model]]
        cm     = confusion_matrix(y_true, y_pred, labels=CLASS_NAMES)

        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧩 Confusion Matrix</div>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
                    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
        ax2.set_xlabel("Predicted")
        ax2.set_ylabel("Actual")
        st.pyplot(fig2)
        plt.close(fig2)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- Classification Report ----
        report    = classification_report(y_true, y_pred, labels=CLASS_NAMES, output_dict=True, zero_division=0)
        report_df = pd.DataFrame(report).transpose()
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 Classification Report</div>', unsafe_allow_html=True)
        st.dataframe(report_df.style.format("{:.2f}"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- Model-wise Summary ----
        st.markdown(f"""
        <div class="white-box">
            <div class="section-title">📋 Model-wise Prediction Summary</div>
            <div style="font-size:18px; color:black; line-height:2;">
                MobileNetV2 → {predictions["MobileNetV2"]} ({confidence_scores["MobileNetV2"]:.2f}%)<br><br>
                DenseNet121 → {predictions["DenseNet121"]} ({confidence_scores["DenseNet121"]:.2f}%)<br><br>
                ResNet50    → {predictions["ResNet50"]}    ({confidence_scores["ResNet50"]:.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==================================================
# MODE 2 — BATCH ZIP
# ==================================================
else:

    st.markdown(
        "<p style='color:white;font-size:18px;'>Upload a ZIP file containing bark images. "
        "The system will classify all images and show individual + overall results.</p>",
        unsafe_allow_html=True
    )

    zip_file = st.file_uploader("📦 Upload ZIP file of bark images", type=["zip"])

    if zip_file is not None:

        with tempfile.TemporaryDirectory() as tmpdir:

            # Extract ZIP
            with zipfile.ZipFile(zip_file, "r") as zf:
                zf.extractall(tmpdir)

            # Collect all images
            all_images = []
            for root, dirs, files in os.walk(tmpdir):
                for f in sorted(files):
                    if f.lower().endswith((".jpg",".jpeg",".png")):
                        all_images.append(os.path.join(root, f))

            if not all_images:
                st.error("No images found in the ZIP file!")
                st.stop()

            st.info(f"📷 Found **{len(all_images)}** images. Classifying...")

            # ---- Classify all images ----
            batch_results = []

            progress = st.progress(0)
            status   = st.empty()

            for idx, img_path in enumerate(all_images):
                try:
                    image     = Image.open(img_path).convert("RGB")
                    img_arr   = np.array(image.resize((224, 224)))
                    results, best_model = predict_image(img_arr)

                    batch_results.append({
                        "image_path":  img_path,
                        "image":       image,
                        "filename":    os.path.basename(img_path),
                        "best_model":  best_model,
                        "prediction":  results[best_model]["species"],
                        "confidence":  results[best_model]["confidence"],
                        "mobilenet":   results["MobileNetV2"]["species"],
                        "mobilenet_c": results["MobileNetV2"]["confidence"],
                        "densenet":    results["DenseNet121"]["species"],
                        "densenet_c":  results["DenseNet121"]["confidence"],
                        "resnet":      results["ResNet50"]["species"],
                        "resnet_c":    results["ResNet50"]["confidence"],
                    })
                except Exception as e:
                    st.warning(f"Could not process {os.path.basename(img_path)}: {e}")

                progress.progress((idx + 1) / len(all_images))
                status.text(f"Processing {idx+1}/{len(all_images)}: {os.path.basename(img_path)}")

            progress.empty()
            status.empty()

            if not batch_results:
                st.error("No images could be processed!")
                st.stop()

            st.success(f"✅ Successfully classified {len(batch_results)} images!")

            # ---- Per Image Results ----
            st.markdown('<div class="white-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🖼 Individual Image Predictions</div>', unsafe_allow_html=True)

            cols_per_row = 3
            for i in range(0, len(batch_results), cols_per_row):
                row_items = batch_results[i:i+cols_per_row]
                cols = st.columns(cols_per_row)
                for col, item in zip(cols, row_items):
                    with col:
                        st.image(item["image"], width=200, caption=item["filename"])
                        st.markdown(f"""
                        <div style="background:#e8f5e9;padding:10px;border-radius:8px;font-size:14px;color:black;">
                        🌲 <b>{item["prediction"]}</b><br>
                        🏆 {item["best_model"]}<br>
                        📈 {item["confidence"]:.1f}%
                        </div>
                        """, unsafe_allow_html=True)
                        st.write("")

            st.markdown('</div>', unsafe_allow_html=True)

            # ---- Summary Table ----
            st.markdown('<div class="white-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📋 Prediction Summary Table</div>', unsafe_allow_html=True)

            summary_df = pd.DataFrame([{
                "Image":       r["filename"],
                "Predicted":   r["prediction"],
                "Best Model":  r["best_model"],
                "Confidence":  f"{r['confidence']:.2f}%",
                "MobileNetV2": f"{r['mobilenet']} ({r['mobilenet_c']:.1f}%)",
                "DenseNet121": f"{r['densenet']} ({r['densenet_c']:.1f}%)",
                "ResNet50":    f"{r['resnet']} ({r['resnet_c']:.1f}%)",
            } for r in batch_results])

            st.dataframe(summary_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ---- Confusion Matrix (batch) ----
            y_pred_all = [r["prediction"] for r in batch_results]
            y_true_all = y_pred_all  # no ground truth available from ZIP

            cm_batch = confusion_matrix(y_true_all, y_pred_all, labels=CLASS_NAMES)

            st.markdown('<div class="white-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🧩 Confusion Matrix (All Images)</div>', unsafe_allow_html=True)
            fig3, ax3 = plt.subplots(figsize=(14, 10))
            sns.heatmap(cm_batch, annot=True, fmt="d", cmap="Greens",
                        xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
            ax3.set_xlabel("Predicted")
            ax3.set_ylabel("Actual")
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)
            st.markdown('</div>', unsafe_allow_html=True)

            # ---- Classification Report (batch) ----
            report_b    = classification_report(y_true_all, y_pred_all, labels=CLASS_NAMES, output_dict=True, zero_division=0)
            report_df_b = pd.DataFrame(report_b).transpose()

            st.markdown('<div class="white-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📄 Classification Report (All Images)</div>', unsafe_allow_html=True)
            st.dataframe(report_df_b.style.format("{:.2f}"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ---- Model-wise Summary (batch) ----
            mob_counts  = {}
            den_counts  = {}
            res_counts  = {}

            for r in batch_results:
                mob_counts[r["mobilenet"]] = mob_counts.get(r["mobilenet"], 0) + 1
                den_counts[r["densenet"]]  = den_counts.get(r["densenet"],  0) + 1
                res_counts[r["resnet"]]    = res_counts.get(r["resnet"],    0) + 1

            st.markdown('<div class="white-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📊 Model-wise Prediction Distribution</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**MobileNetV2**")
                mob_df = pd.DataFrame(list(mob_counts.items()), columns=["Species","Count"]).sort_values("Count", ascending=False)
                st.dataframe(mob_df, use_container_width=True)

            with col2:
                st.markdown("**DenseNet121**")
                den_df = pd.DataFrame(list(den_counts.items()), columns=["Species","Count"]).sort_values("Count", ascending=False)
                st.dataframe(den_df, use_container_width=True)

            with col3:
                st.markdown("**ResNet50**")
                res_df = pd.DataFrame(list(res_counts.items()), columns=["Species","Count"]).sort_values("Count", ascending=False)
                st.dataframe(res_df, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------
# BOTTOM BUTTONS
# --------------------------------------------------
st.write("")
col1, col2 = st.columns(2)

if col1.button("🔄 Clear"):
    st.rerun()

if col2.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")