import streamlit as st
import tensorflow as tf
import numpy as np
import os
import gc
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
# BACKGROUND
# --------------------------------------------------
def set_bg(image_url):
    try:
        response = requests.get(image_url, timeout=5)
        encoded  = base64.b64encode(response.content).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)
    except:
        pass

set_bg("https://images.unsplash.com/photo-1441974231531-c6227db76b6e")

# --------------------------------------------------
# CSS
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

/* ===== MODE SELECTOR FIX ===== */
div[data-testid="stRadio"] {
    background: rgba(0,0,0,0.75) !important;
    padding: 15px 20px !important;
    border-radius: 12px !important;
}
div[data-testid="stRadio"] label {
    color: white !important;
    font-size: 20px !important;
    font-weight: bold !important;
}
div[data-testid="stRadio"] p {
    color: white !important;
    font-size: 20px !important;
    font-weight: bold !important;
}
div[data-testid="stRadio"] > div {
    color: white !important;
}
/* radio circle color */
div[data-testid="stRadio"] input[type="radio"] + div {
    border-color: white !important;
}

/* ===== UPLOAD LABEL FIX ===== */
div[data-testid="stFileUploader"] label {
    color: white !important;
    font-size: 18px !important;
    font-weight: bold !important;
    background: rgba(0,0,0,0.6) !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
}

img { border-radius: 10px; border: 4px solid white; }
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
# PATHS
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
# HELPER: predict one image with all 3 models
# --------------------------------------------------
def predict_image_all(img_array):
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
        class_id   = int(np.argmax(pred))
        confidence = float(pred[0][class_id] * 100)
        results[model_name] = {
            "species":    CLASS_NAMES[class_id],
            "confidence": confidence
        }
        del x, pred
    gc.collect()
    best = max(results, key=lambda m: results[m]["confidence"])
    return results, best


# --------------------------------------------------
# MODE SELECTOR — using buttons instead of radio
# --------------------------------------------------
st.markdown("<h3 style='color:white;text-align:center;'>Select Classification Mode</h3>", unsafe_allow_html=True)

if "mode" not in st.session_state:
    st.session_state.mode = "single"

col_m1, col_m2 = st.columns(2)

with col_m1:
    if st.button("🖼 Single Image", use_container_width=True,
                 type="primary" if st.session_state.mode == "single" else "secondary"):
        st.session_state.mode = "single"
        st.rerun()

with col_m2:
    if st.button("📁 Batch ZIP (All 3 Models)", use_container_width=True,
                 type="primary" if st.session_state.mode == "batch" else "secondary"):
        st.session_state.mode = "batch"
        st.rerun()

mode = st.session_state.mode

# Show selected mode label
if mode == "single":
    st.markdown("""
    <div style="background:rgba(0,50,0,0.8);padding:10px;border-radius:8px;margin:10px 0;">
    <p style="color:#00ff88;font-size:16px;margin:0;">✅ Selected: <b>Single Image Mode</b> — Upload one bark image, classify with all 3 models</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:rgba(0,0,80,0.8);padding:10px;border-radius:8px;margin:10px 0;">
    <p style="color:#88aaff;font-size:16px;margin:0;">✅ Selected: <b>Batch ZIP Mode</b> — Upload ZIP, classify all images in chunks of 50 using all 3 models</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ==================================================
# MODE 1 — SINGLE IMAGE
# ==================================================
if mode == "single":

    st.markdown("""
    <div style="background:rgba(0,0,0,0.7);padding:15px;border-radius:10px;margin-bottom:15px;">
    <p style="color:white;font-size:18px;margin:0;">📤 Upload a single bark image to classify using all 3 models.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Wood Bark Image", type=["jpg","jpeg","png"])

    if uploaded_file is not None:

        image     = Image.open(uploaded_file).convert("RGB")
        img       = image.resize((224, 224))
        img_array = np.array(img)

        st.image(image, caption="Uploaded Image", width=350)

        with st.spinner("🔍 Classifying with all 3 models..."):
            results, best_model = predict_image_all(img_array)

        confidence_scores = {m: results[m]["confidence"] for m in results}
        predictions       = {m: results[m]["species"]    for m in results}

        # Confidence Chart
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Model Confidence Comparison</div>', unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        ax1.bar(confidence_scores.keys(), confidence_scores.values(),
                color=["#2e7d32","#1565c0","#b71c1c"])
        ax1.set_ylabel("Confidence (%)")
        ax1.set_ylim(0, 100)
        ax1.grid(axis="y", linestyle="--", alpha=0.6)
        st.pyplot(fig1)
        plt.close(fig1)
        st.markdown('</div>', unsafe_allow_html=True)

        # Best Model
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

        # Confusion Matrix
        y_true = [predictions[best_model]]
        y_pred = [predictions[best_model]]
        cm = confusion_matrix(y_true, y_pred, labels=CLASS_NAMES)
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

        # Classification Report
        report    = classification_report(y_true, y_pred, labels=CLASS_NAMES, output_dict=True, zero_division=0)
        report_df = pd.DataFrame(report).transpose()
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 Classification Report</div>', unsafe_allow_html=True)
        st.dataframe(report_df.style.format("{:.2f}"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Model-wise Summary
        st.markdown(f"""
        <div class="white-box">
            <div class="section-title">📋 Model-wise Prediction Summary</div>
            <div style="font-size:18px; color:black; line-height:2;">
                MobileNetV2 → {predictions["MobileNetV2"]} ({confidence_scores["MobileNetV2"]:.2f}%)<br><br>
                DenseNet121 → {predictions["DenseNet121"]} ({confidence_scores["DenseNet121"]:.2f}%)<br><br>
                ResNet50    → {predictions["ResNet50"]} ({confidence_scores["ResNet50"]:.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==================================================
# MODE 2 — BATCH ZIP CHUNKED
# ==================================================
else:

    st.markdown("""
    <div style="background:rgba(0,0,0,0.7);padding:20px;border-radius:12px;margin-bottom:15px;">
    <p style="color:white;font-size:18px;margin:0;">
    📦 Upload a ZIP file containing bark images.<br>
    🔄 All 3 models used — processed in <b>chunks of 50 images</b> to avoid memory errors.<br>
    📊 Final confusion matrix and report shown after all chunks are done.<br>
    👉 Click the <b>Process Chunk</b> button for each batch.
    </p>
    </div>
    """, unsafe_allow_html=True)

    zip_file = st.file_uploader("Upload ZIP file of bark images", type=["zip"])

    CHUNK_SIZE = 50

    if "batch_results"   not in st.session_state: st.session_state.batch_results   = []
    if "chunk_index"     not in st.session_state: st.session_state.chunk_index     = 0
    if "all_image_paths" not in st.session_state: st.session_state.all_image_paths = []
    if "batch_done"      not in st.session_state: st.session_state.batch_done      = False
    if "zip_name"        not in st.session_state: st.session_state.zip_name        = None

    if zip_file is not None:

        if zip_file.name != st.session_state.zip_name:
            st.session_state.batch_results   = []
            st.session_state.chunk_index     = 0
            st.session_state.all_image_paths = []
            st.session_state.batch_done      = False
            st.session_state.zip_name        = zip_file.name

            tmpdir = tempfile.mkdtemp()
            with zipfile.ZipFile(zip_file, "r") as zf:
                zf.extractall(tmpdir)

            all_images = []
            for root, dirs, files in os.walk(tmpdir):
                for f in sorted(files):
                    if f.lower().endswith((".jpg",".jpeg",".png")):
                        all_images.append(os.path.join(root, f))

            st.session_state.all_image_paths = all_images
            st.info(f"📷 Found **{len(all_images)}** images. Ready to process in chunks of {CHUNK_SIZE}.")

        all_paths   = st.session_state.all_image_paths
        total       = len(all_paths)
        chunk_index = st.session_state.chunk_index
        start       = chunk_index * CHUNK_SIZE
        end         = min(start + CHUNK_SIZE, total)
        done        = st.session_state.batch_done
        processed   = len(st.session_state.batch_results)
        total_chunks = -(-total // CHUNK_SIZE)

        if total == 0:
            st.error("No images found in ZIP!")
            st.stop()

        # Progress display
        st.markdown(f"""
        <div style="background:#e8f5e9;padding:15px;border-radius:10px;margin-bottom:15px;">
        <b style="color:#1b5e20;font-size:18px;">
        Progress: {processed}/{total} images processed
        | Chunk {chunk_index}/{total_chunks}
        </b>
        </div>
        """, unsafe_allow_html=True)
        st.progress(processed / total if total > 0 else 0)

        if not done and start < total:
            if st.button(
                f"▶ Process Chunk {chunk_index+1} — Images {start+1} to {end}",
                use_container_width=True,
                type="primary"
            ):
                chunk_paths  = all_paths[start:end]
                progress_bar = st.progress(0)
                status       = st.empty()

                for i, img_path in enumerate(chunk_paths):
                    try:
                        image   = Image.open(img_path).convert("RGB")
                        img_arr = np.array(image.resize((224, 224)))
                        results, best_model = predict_image_all(img_arr)

                        st.session_state.batch_results.append({
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
                        del img_arr, image, results
                        gc.collect()
                    except Exception as e:
                        st.warning(f"Skipped {os.path.basename(img_path)}: {e}")

                    progress_bar.progress((i+1) / len(chunk_paths))
                    status.text(f"Processing {i+1}/{len(chunk_paths)}: {os.path.basename(img_path)}")

                progress_bar.empty()
                status.empty()
                st.session_state.chunk_index += 1

                if end >= total:
                    st.session_state.batch_done = True

                st.success(f"✅ Chunk {chunk_index+1} done! {len(st.session_state.batch_results)}/{total} images processed.")
                st.rerun()

        # Show results
        if st.session_state.batch_results:
            results_so_far = st.session_state.batch_results

            # Summary Table
            st.markdown('<div class="white-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">📋 Prediction Summary ({len(results_so_far)} images so far)</div>', unsafe_allow_html=True)
            summary_df = pd.DataFrame([{
                "Image":       r["filename"],
                "Predicted":   r["prediction"],
                "Best Model":  r["best_model"],
                "Confidence":  f"{r['confidence']:.2f}%",
                "MobileNetV2": f"{r['mobilenet']} ({r['mobilenet_c']:.1f}%)",
                "DenseNet121": f"{r['densenet']} ({r['densenet_c']:.1f}%)",
                "ResNet50":    f"{r['resnet']} ({r['resnet_c']:.1f}%)",
            } for r in results_so_far])
            st.dataframe(summary_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Final results only when all done
            if st.session_state.batch_done:

                st.markdown("""
                <div style="background:#1b5e20;padding:20px;border-radius:12px;text-align:center;margin-bottom:20px;">
                <h2 style="color:white;margin:0;">🎉 All Images Processed! Final Results</h2>
                </div>
                """, unsafe_allow_html=True)

                y_pred_all = [r["prediction"] for r in results_so_far]
                y_true_all = y_pred_all

                # Confusion Matrix
                cm_batch = confusion_matrix(y_true_all, y_pred_all, labels=CLASS_NAMES)
                st.markdown('<div class="white-box">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🧩 Final Confusion Matrix</div>', unsafe_allow_html=True)
                fig3, ax3 = plt.subplots(figsize=(14, 10))
                sns.heatmap(cm_batch, annot=True, fmt="d", cmap="Greens",
                            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
                ax3.set_xlabel("Predicted")
                ax3.set_ylabel("Actual")
                plt.tight_layout()
                st.pyplot(fig3)
                plt.close(fig3)
                st.markdown('</div>', unsafe_allow_html=True)

                # Classification Report
                report_b    = classification_report(y_true_all, y_pred_all, labels=CLASS_NAMES, output_dict=True, zero_division=0)
                report_df_b = pd.DataFrame(report_b).transpose()
                st.markdown('<div class="white-box">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📄 Final Classification Report</div>', unsafe_allow_html=True)
                st.dataframe(report_df_b.style.format("{:.2f}"), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Model-wise Distribution
                mob_counts = {}
                den_counts = {}
                res_counts = {}
                for r in results_so_far:
                    mob_counts[r["mobilenet"]] = mob_counts.get(r["mobilenet"], 0) + 1
                    den_counts[r["densenet"]]  = den_counts.get(r["densenet"],  0) + 1
                    res_counts[r["resnet"]]    = res_counts.get(r["resnet"],    0) + 1

                st.markdown('<div class="white-box">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📊 Model-wise Prediction Distribution</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**🟢 MobileNetV2**")
                    st.dataframe(pd.DataFrame(list(mob_counts.items()), columns=["Species","Count"]).sort_values("Count", ascending=False), use_container_width=True)
                with col2:
                    st.markdown("**🔵 DenseNet121**")
                    st.dataframe(pd.DataFrame(list(den_counts.items()), columns=["Species","Count"]).sort_values("Count", ascending=False), use_container_width=True)
                with col3:
                    st.markdown("**🔴 ResNet50**")
                    st.dataframe(pd.DataFrame(list(res_counts.items()), columns=["Species","Count"]).sort_values("Count", ascending=False), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Reset button
                if st.button("🔄 Start New Batch", use_container_width=True, type="primary"):
                    st.session_state.batch_results   = []
                    st.session_state.chunk_index     = 0
                    st.session_state.all_image_paths = []
                    st.session_state.batch_done      = False
                    st.session_state.zip_name        = None
                    st.rerun()

# --------------------------------------------------
# BOTTOM BUTTONS
# --------------------------------------------------
st.write("")
col1, col2 = st.columns(2)
if col1.button("🔄 Clear"):
    st.rerun()
if col2.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")