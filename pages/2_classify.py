import streamlit as st
import tensorflow as tf
import numpy as np
import os
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
# BACKGROUND IMAGE
# --------------------------------------------------
def set_bg(image_url):
    response = requests.get(image_url)
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

set_bg("https://images.unsplash.com/photo-1441974231531-c6227db76b6e")


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown(
    """
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
    .instruction-box {
        background: rgba(255,255,255,0.95);
        padding: 15px;
        border-radius: 10px;
        font-size: 16px;
        color: black;
    }
    img {
        border-radius: 10px;
        border: 4px solid white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "wood_species")
MODEL_DIR = os.path.join(BASE_DIR, "models")

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
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("""
### Instructions
1. Upload a clear wood bark image.
2. Wait for prediction.
3. View model comparison & report.
""")


# --------------------------------------------------
# IMAGE UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "📤 Upload Wood Bark Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", width=350)

    img = image.resize((224, 224))
    img_array = np.array(img)

    confidence_scores = {}
    predictions = {}

    # --------------------------------------------------
    # MODEL PREDICTIONS
    # --------------------------------------------------
    for model_name, model in models.items():

        if model_name == "MobileNetV2":
            x = mob_pre(img_array.copy())
        elif model_name == "DenseNet121":
            x = dense_pre(img_array.copy())
        else:
            x = res_pre(img_array.copy())

        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)

        class_id = np.argmax(pred)
        confidence = float(pred[0][class_id] * 100)

        predictions[model_name] = CLASS_NAMES[class_id]
        confidence_scores[model_name] = confidence


    # --------------------------------------------------
    # CONFIDENCE BAR CHART
    # --------------------------------------------------
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Model Confidence Comparison</div>', unsafe_allow_html=True)

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(confidence_scores.keys(), confidence_scores.values())
    ax1.set_ylabel("Confidence (%)")
    ax1.set_ylim(0, 100)
    ax1.grid(axis="y", linestyle="--", alpha=0.6)
    st.pyplot(fig1)
    plt.close(fig1)

    st.markdown('</div>', unsafe_allow_html=True)


    # --------------------------------------------------
        # --------------------------------------------------
     # BEST MODEL
    # --------------------------------------------------
    best_model = max(confidence_scores, key=confidence_scores.get)

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏆 Best Model Prediction</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="background:white;padding:20px;border-radius:12px;font-size:18px;color:black;">
            🏆 <b>Best Model:</b> {best_model}<br>
            🌲 <b>Predicted Species:</b> {predictions[best_model]}<br>
            📈 <b>Confidence:</b> {confidence_scores[best_model]:.2f}%
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)


    # --------------------------------------------------
    # CONFUSION MATRIX
    # --------------------------------------------------
    y_true = [predictions[best_model]]
    y_pred = [predictions[best_model]]

    cm = confusion_matrix(y_true, y_pred, labels=CLASS_NAMES)

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧩 Confusion Matrix</div>', unsafe_allow_html=True)

    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
                xticklabels=CLASS_NAMES,
                yticklabels=CLASS_NAMES)
    ax2.set_xlabel("Predicted")
    ax2.set_ylabel("Actual")
    st.pyplot(fig2)
    plt.close(fig2)

    st.markdown('</div>', unsafe_allow_html=True)


    # --------------------------------------------------
    # CLASSIFICATION REPORT
    # --------------------------------------------------
    report = classification_report(
        y_true,
        y_pred,
        labels=CLASS_NAMES,
        output_dict=True,
        zero_division=0
    )

    report_df = pd.DataFrame(report).transpose()

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Classification Report</div>', unsafe_allow_html=True)
    st.dataframe(report_df.style.format("{:.2f}"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


    # --------------------------------------------------
        # --------------------------------------------------
    # MODEL-WISE SUMMARY
    # --------------------------------------------------
    st.markdown(
        """
        <div class="white-box">
            <div class="section-title">📋 Model-wise Prediction Summary</div>
            <div style="font-size:18px; color:black; line-height:2;">
                MobileNetV2 → {0} ({1:.2f}%)<br><br>
                DenseNet121 → {2} ({3:.2f}%)<br><br>
                ResNet50 → {4} ({5:.2f}%)
            </div>
        </div>
        """.format(
            predictions["MobileNetV2"], confidence_scores["MobileNetV2"],
            predictions["DenseNet121"], confidence_scores["DenseNet121"],
            predictions["ResNet50"], confidence_scores["ResNet50"],
        ),
        unsafe_allow_html=True
    ) 

# --------------------------------------------------
# EXTRA BUTTONS
# --------------------------------------------------
col1, col2 = st.columns(2)

if col1.button("🔄 Clear"):
    st.rerun()

if col2.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")