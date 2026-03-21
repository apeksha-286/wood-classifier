import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Wood World", layout="wide")

# ---------------- PAGE STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

# ---------------- CSS ----------------
st.markdown("""
<style>

.stApp{ background-color:#f4f6f7; }

/* Buttons */
div.stButton > button{
    height:42px;
    width:120px;
    font-size:17px;
    border-radius:8px;
    background-color:white;
    color:black;
    border:2px solid #2e7d32;
    font-weight:bold;
}
div.stButton > button:hover{
    background-color:#2e7d32;
    color:white;
}

/* Titles */
.center{ text-align:center; color:#1b5e20; }
.big{ font-size:70px; font-weight:bold; }
.mid{ font-size:40px; }
.small{ font-size:24px; font-style:italic; }

/* Text Box */
.whitebox{
    background:white;
    padding:30px;
    border-radius:12px;
    color:black;
    box-shadow:0px 4px 15px rgba(0,0,0,0.1);
    font-size:22px;
    line-height:1.9;
}
.whitebox h3{
    font-size:30px;
    margin-bottom:12px;
}

/* Image Box */
.image-box{
    background:#2e7d32;
    padding:12px;
    border-radius:15px;
    box-shadow:0px 6px 20px rgba(0,0,0,0.3);
}
.image-box img{
    width:100%;
    border-radius:10px;
}

/* Feature Cards */
.feature-card{
    background:white;
    padding:25px;
    border-radius:12px;
    text-align:center;
    box-shadow:0px 4px 15px rgba(0,0,0,0.15);
    transition:0.3s;
}
.feature-card:hover{
    transform:translateY(-6px);
    box-shadow:0px 8px 25px rgba(0,0,0,0.25);
}

.feature-title{
    font-size:26px;
    font-weight:bold;
    color:#1b5e20;
    margin-bottom:12px;
}

.feature-text{
    font-size:19px;
    line-height:1.8;
}

/* About Cards */
.about-card{
    background:linear-gradient(135deg,#e8f5e9,#ffffff);
    padding:30px;
    border-radius:15px;
    box-shadow:0px 6px 20px rgba(0,0,0,0.15);
    transition:0.3s;
    border-left:6px solid #2e7d32;

    display:flex;
    flex-direction:column;
    justify-content:flex-start;

    height:100%;
    min-height:320px;
}

.about-card:hover{
    transform:translateY(-6px);
    box-shadow:0px 10px 30px rgba(0,0,0,0.25);
}

.about-title{
    font-size:28px;
    font-weight:bold;
    color:#1b5e20;
    margin-bottom:12px;
}

.about-text{
    font-size:21px;
    line-height:1.9;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVBAR ----------------
col1,col2,col3,col4,col5,col6 = st.columns([0.2,0.6,0.6,0.6,0.6,3])

with col2:
    if st.button("Home"):
        st.session_state.page="home"

with col3:
    if st.button("About"):
        st.session_state.page="about"

with col4:
    if st.button("Admin"):
        st.switch_page("pages/3_admin.py")

with col5:
    if st.button("Login"):
        st.switch_page("pages/login.py")

page = st.session_state.page


# ---------------- HOME PAGE ----------------
if page=="home":

    st.markdown('<div class="center big">🌳Welcome to Wood World</div>',unsafe_allow_html=True)
    st.markdown('<div class="center mid">Wood Species Identification System</div>',unsafe_allow_html=True)
    st.markdown('<div class="center small">"Every tree tells a story through its bark"</div>',unsafe_allow_html=True)

    st.write("")
    st.write("")

    # ---------------- SLIDESHOW ----------------
    components.html("""
    <!DOCTYPE html>
    <html>
    <head>

    <style>

    *{box-sizing:border-box;}

    .mySlides{display:none;}
    .mySlides:first-child{display:block;}

    .slideshow-container{
        width:90%;
        max-width:1200px;
        height:450px;
        margin:auto;
        position:relative;
        overflow:hidden;
        border-radius:12px;
    }

    .mySlides img{
        width:100%;
        height:450px;
        object-fit:cover;
        display:block;
    }

    .text{
        color:white;
        font-size:24px;
        padding:12px;
        position:absolute;
        bottom:10px;
        width:100%;
        text-align:center;
        background:rgba(0,0,0,0.4);
    }

    .numbertext{
        color:white;
        font-size:14px;
        padding:8px;
        position:absolute;
        top:0;
    }

    .dot{
        height:12px;
        width:12px;
        margin:0 4px;
        background:#bbb;
        border-radius:50%;
        display:inline-block;
    }

    .active{background:#2e7d32;}

    .fade{
        animation-name:fade;
        animation-duration:1.5s;
    }

    @keyframes fade{
        from{opacity:.4}
        to{opacity:1}
    }

    </style>
    </head>

    <body>

    <div class="slideshow-container">

    <div class="mySlides fade">
    <img src="https://freerangestock.com/sample/101137/towering-trees-dominate-lush-forest-landscape.jpg">
    <div class="text">Forest View</div>
    </div>

    <div class="mySlides fade">
    <img src="https://png.pngtree.com/background/20250523/original/pngtree-a-dense-forest-with-tall-trees-and-lush-green-moss-covered-picture-image_16556075.jpg">
    <div class="text">Tree Bark Texture</div>
    </div>

    <div class="mySlides fade">
    <img src="https://images.unsplash.com/photo-1704144269803-fa101811e2a7?fm=jpg&w=3000">
    <div class="text">Nature Forest</div>
    </div>

    </div>

    <br>

    <div style="text-align:center">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
    </div>

    <script>

    let slideIndex=0;
    showSlides();

    function showSlides(){

        let i;
        let slides=document.getElementsByClassName("mySlides");
        let dots=document.getElementsByClassName("dot");

        for(i=0;i<slides.length;i++){
            slides[i].style.display="none";
        }

        slideIndex++;

        if(slideIndex>slides.length){slideIndex=1;}

        slides[slideIndex-1].style.display="block";

        for(i=0;i<dots.length;i++){
            dots[i].className=dots[i].className.replace(" active","");
        }

        dots[slideIndex-1].className+=" active";

        setTimeout(showSlides,3000);
    }

    </script>

    </body>
    </html>
    """,height=500)

    st.write("")
    st.write("")

    # ---------------- CONTENT ----------------
    col1,col2=st.columns([1,2])

    with col1:
        st.markdown("""
        <div class="image-box">
        <img src="https://images.unsplash.com/photo-1440581572325-0bea30075d9d?auto=format&fit=crop&w=900">
        </div>
        """,unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="whitebox">
        <h3>Nature Thought</h3>
        Trees communicate their history through bark texture, color patterns and surface structures. 
        Each tree carries a unique identity and story. 
        By analyzing bark patterns, AI models can classify wood species accurately.
        </div>
        """,unsafe_allow_html=True)

    st.write("")
    st.write("")

    col3,col4=st.columns([2,1])

    with col3:
        st.markdown("""
        <div class="whitebox">
        The bark of a tree serves as a protective layer that preserves the life and health of the tree. 
        It prevents damage from insects, diseases, and extreme weather conditions. 
        Each tree develops a unique bark texture that reflects its species and growth environment. 
        These patterns provide valuable information for researchers and environmental studies. 
        By analyzing bark images, technology can help identify and understand different wood species.
        </div>
        """,unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="image-box">
        <img src="https://images.unsplash.com/photo-1624118600862-a34e077039c2?auto=format&fit=crop&w=900">
        </div>
        """,unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.markdown('<div class="center mid">Key Features</div>',unsafe_allow_html=True)

    st.write("")

    col1,col2,col3=st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">🌳 AI Classification</div>
        <div class="feature-text">
        The system analyzes bark images using Artificial Intelligence to identify different wood species accurately.
        </div>
        </div>
        """,unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">⚡ Fast Prediction</div>
        <div class="feature-text">
        Users can upload bark images and receive predictions instantly with high confidence scores.
        </div>
        </div>
        """,unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">📊 Deep Learning Models</div>
        <div class="feature-text">
        The system uses advanced CNN architectures like MobileNetV2, DenseNet121, and ResNet50.
        </div>
        </div>
        """,unsafe_allow_html=True)


# ---------------- ABOUT ----------------
# ---------------- ABOUT ----------------
elif page=="about":

    st.markdown('<div class="center big">About the Project</div>',unsafe_allow_html=True)

    # -------- SMALL SLIDESHOW --------
    components.html("""
    <html>
    <head>
    <style>

    .slider-box{
    width:70%;
    max-width:700px;
    height:300px;
    margin:auto;
    overflow:hidden;
    border-radius:12px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.3);
    }

    .slider-box img{
    width:100%;
    height:300px;
    object-fit:cover;
    }

    </style>
    </head>

    <body>

    <div class="slider-box">
    <img id="aboutslide" src="https://images.unsplash.com/photo-1704144269803-fa101811e2a7?fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDE4fHx8ZW58MHx8fHx8&ixlib=rb-4.1.0&q=60&w=3000">
    </div>

    <script>

    let images=[
    "https://images.unsplash.com/photo-1704144269803-fa101811e2a7?fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDE4fHx8ZW58MHx8fHx8&ixlib=rb-4.1.0&q=60&w=3000",
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
    "https://images.unsplash.com/photo-1440581572325-0bea30075d9d"
    ]

    let index=0

    setInterval(function(){

    index++
    if(index>=images.length){index=0}

    document.getElementById("aboutslide").src=images[index]

    },3000)

    </script>

    </body>
    </html>
    """, height=320)

    st.write("")
    st.write("")

    # -------- IMPORTANCE SECTION --------
    st.markdown('<div class="center mid">Importance of Tree Identification</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="whitebox">

    Tree identification plays a vital role in environmental conservation, forestry management,
    and biodiversity research. Different tree species have unique characteristics such as
    bark texture, leaf structure, and growth patterns.

    Traditional identification methods require expert knowledge and can be time-consuming.
    With the help of Artificial Intelligence and deep learning models, tree species can
    be identified quickly and accurately using bark images.

    This project demonstrates how modern computer vision techniques can assist researchers
    and environmental scientists in understanding forest ecosystems and preserving biodiversity.

    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # -------- CARDS --------
    col1,col2 = st.columns(2)

    with col1:
     st.markdown("""
    <div class="about-card">
    <div class="about-title">🎯 Project Objective</div>
    <div class="about-text">
    The main objective of this project is to design an intelligent system capable of 
    identifying different wood species by analyzing bark images. 

    Using deep learning and computer vision techniques, the system learns unique 
    patterns and textures found in tree bark. This allows users to quickly identify 
    tree species without requiring expert knowledge.

    The project demonstrates how Artificial Intelligence can support forestry research,
    environmental monitoring and biodiversity conservation.
    </div>
    </div>
    """,unsafe_allow_html=True)
    with col2:
     st.markdown("""
    <div class="about-card">
    <div class="about-title">💻 Technologies Used</div>
    <div class="about-text">
    This system is developed using modern Artificial Intelligence and 
    web application technologies.
    Python is used as the core programming language for building the 
    machine learning model and data processing pipeline.

    Deep learning frameworks such as TensorFlow and Convolutional 
    Neural Networks (CNN) are used for image classification.
    
    Pre-trained architectures including MobileNetV2, DenseNet121 and 
    ResNet50 are utilized to improve prediction accuracy.
    </div>
    </div>
    """,unsafe_allow_html=True)

    st.write("")
    st.write("")

    col3,col4 = st.columns(2)

    with col3:
        st.markdown("""
        <div class="about-card">
        <div class="about-title">📂 Dataset</div>
        <div class="about-text">
        The dataset consists of 558 bark images collected from multiple tree species. 
    Each image captures unique bark textures, patterns and color variations.

    These images are used to train deep learning models to recognize and 
    classify tree species automatically.

    A well-organized dataset plays a critical role in improving the accuracy 
    and performance of machine learning models.
        </div>
        </div>
        """,unsafe_allow_html=True)

    with col4:
     st.markdown("""
    <div class="about-card">
    <div class="about-title">🚀 Future Improvements</div>
    <div class="about-text">
    In the future, the system can be expanded by including a larger 
    dataset with more tree species to improve the model's learning ability.

    Advanced deep learning architectures and optimization techniques 
    can also be implemented to increase classification accuracy.
    
    Additional features such as real-time bark recognition using 
    mobile cameras and cloud-based deployment can be developed.
    </div>
    </div>
    """,unsafe_allow_html=True)

elif page=="admin":
    st.switch_page("pages/3_admin.py")

elif page=="login":
    st.switch_page("pages/login.py")