# full_dashboard_modern_ui.py
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score
import seaborn as sns
import matplotlib.pyplot as plt
from openai import OpenAI
from streamlit_option_menu import option_menu

# -----------------------------------
# OpenAI Client Setup (Secure Key Use)
# -----------------------------------
# The API key is now read from an environment variable instead of being
# hardcoded. It is injected at container runtime by Ansible (see
# ansible/deploy.yml), which in turn gets it from the GitHub Actions
# secret OPENROUTER_API_KEY. Locally, set it with:
#   export OPENROUTER_API_KEY="your-key-here"
st.set_page_config(page_title="AI Driven Analytics", page_icon="🚀", layout="wide")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

if not OPENROUTER_API_KEY:
    st.warning(
        "OPENROUTER_API_KEY is not set. AI-powered features will not work "
        "until this environment variable is configured."
    )

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# -----------------------------------
# Streamlit Config
# -----------------------------------


# -----------------------------------
# Custom CSS for Modern Look
# -----------------------------------
st.markdown("""
    <style>
    /* Base styles (Kept for completeness) */
    body {
        background-color: #fafafa;
        color: #333;
        font-family: "Inter", sans-serif;
    }

    /* Sidebar styling (Kept for completeness) */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6a0dad, #9b30ff);
        padding: 30px 20px;
        width: 270px !important;
        min-height: 100vh;
        color: white;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
        font-weight: 500;
    }

    /* === 📂 Upload Box Styling === */
    div[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.12);
        border: 2px solid rgba(255, 255, 255, 0.25);
        border-radius: 16px;
        padding: 1.5rem 1rem 1rem 1rem; 
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
        backdrop-filter: blur(8px);
        transition: 0.3s ease-in-out;
    }

    /* Instructional text */
    div[data-testid="stFileUploader"]::before {
        content: "📂 Please upload your CSV or Excel file below 👇";
        display: block;
        color: #fff !important;
        font-size: 14px;
        margin-bottom: 10px;
        font-weight: 500;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    /* Upload label text (The 'Upload CSV/Excel file' text) */
    div[data-testid="stFileUploader"] label {
        color: white !important; 
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* Drop zone */
    div[data-testid="stFileUploader"] > div:nth-child(2) > div:first-child {
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 2px dashed rgba(255, 255, 255, 0.7) !important;
        padding: 1.5rem 1rem; 
        border-radius: 12px;
        min-height: 150px;
    }
    
    /* Text inside the drop zone area (e.g. 'Drag and drop file here, or') */
    div[data-testid="stFileUploader"] > div:nth-child(2) > div:first-child p {
        color: white !important; 
        font-weight: 500;
    }

    /* === 📁 Uploaded file card styling === */
    /* Uploaded file card container */
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        background-color: #f8f8f8 !important; /* Light background for visibility */
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        /* Fixes for rectangular shape and full name visibility */
        width: 100% !important; 
        overflow: visible !important; 
        min-height: auto !important; 
    }

    /* File text container */
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] > div:first-child {
        flex: 1;
        min-width: 0;
        /* Fixes for full name visibility */
        overflow: visible !important;
        white-space: normal !important; 
    }
    
    /* CRITICAL FIX: File Name/Size Visibility (V7 - Transparent Background) */
    
    /* 1. Ensure the container holding the icon and text is transparent */
    div[data-testid="stFileUploaderFile"] > div:first-child {
        background-color: transparent !important;
        color: #000000 !important; /* Force text color on container */
    }
    
    /* 2. Target ALL internal divs/spans inside the file info area */
    div[data-testid="stFileUploaderFile"] > div:first-child div,
    div[data-testid="stFileUploaderFile"] > div:first-child span {
        background-color: transparent !important;
        color: #000000 !important;
    }

    /* 3. Target the specific file name and size paragraphs for black color */
    div[data-testid="stFileUploaderFile"] p {
        color: #000000 !important;
        background-color: transparent !important; /* Clear any background on p tag */
    }
    
    /* 4. Target the file icon's SVG path/fill (Fixes icon color and shape) */
    div[data-testid="stFileUploaderFile"] svg {
        color: #000000 !important; /* Use color property for icon in Streamlit */
        fill: #000000 !important; /* Fallback for SVG fill */
        background-color: transparent !important; /* Clear icon background */
    }

    /* File name (visible + truncated) */
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] p:first-child {
        font-weight: 600 !important;
        color: #000 !important; /* Re-affirm black color */
        /* Fixes for full file name visibility */
        overflow: visible !important; 
        white-space: normal !important; 
        text-overflow: clip !important; 
        margin: 0 0 2px 0 !important;
        display: block !important;
        max-width: 100%; 
        word-break: break-all; 
    }

    /* File size */
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] p:last-child {
        font-size: 0.85em;
        color: #333 !important; /* Re-affirm dark gray color */
        margin: 0 !important;
        white-space: normal !important; 
    }
    /* === END Uploaded file card styling === */

    /* Delete (X) button */
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button {
        background: none !important;
        color: #E60000 !important;
        font-size: 20px !important;
        padding: 5px;
        flex-shrink: 0;
    }
    /* === Hero Section Specific Styles === */
    .hero-section {
        background: linear-gradient(90deg, #6a0dad, #9b30ff);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        margin-bottom: 30px;
        /* Add transition for smooth hover effects */
        transition: all 0.4s ease-in-out; 
        position: relative; /* Needed for pseudo-elements or more complex hovers if desired */
        overflow: hidden; /* Ensures inner elements don't overflow during scaling */
    }

    .hero-section:hover {
        /* Slightly change gradient direction or color on hover */
        background: linear-gradient(100deg, #5a099d, #8b20ef); 
        /* Slightly scale up the card */
        transform: translateY(-5px) scale(1.01);
        /* Enhance the shadow on hover */
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    }

    .hero-section h1 {
        color: white;
        font-size: 40px;
        font-weight: 700; /* Make title bolder */
        margin-bottom: 10px; /* Adjust margin */
        text-shadow: 2px 2px 5px rgba(0,0,0,0.3); /* Add text shadow for pop */
    }

    .hero-section p {
        color: white;
        font-size: 18px;
        margin-top: 10px;
        line-height: 1.5; /* Improve readability */
        opacity: 0.9; /* Slightly transparent for depth */
    }

    /* --- HOME PAGE METRIC CARDS --- */
    /* Add styling for these new cards as well, including hover */
    .metric-card-container {
        display: flex;
    justify-content: center;
    gap: 25px;
    margin-top: 30px;
    flex-wrap: wrap; 
    /* NEW: Ensure the container is centered on the page */
    width: 100%;
    margin-left: auto;
    margin-right: auto;
    /* NEW: Ensure text inside metric cards is centered (if needed) */
    text-align: center;
    }

    .metric-card {
        background-color: white; /* White background for contrast */
        border-radius: 12px;
        padding: 20px 25px;
        width: 220px; /* Fixed width for consistency */
        min-height: 120px; /* Ensure consistent height */
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease-in-out;
        cursor: pointer; /* Indicate interactivity */
        border: 1px solid #eee; /* Subtle border */
        display: flex; /* Use flex for vertical centering */
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.03); /* Lift and grow significantly on hover */
        box-shadow: 0 10px 25px rgba(0,0,0,0.15); /* Stronger shadow */
        background-color: #f9f9f9; /* Slight background change on hover */
    }

    .metric-card h3 {
        color: #6a0dad; /* Primary purple color for titles */
        font-size: 18px;
        margin-bottom: 8px;
        font-weight: 600;
        display: flex; /* Allow icon and text to sit together */
        align-items: center;
        gap: 8px; /* Space between icon and text */
        justify-content: center;
    }
    .metric-card h3 img { /* Style for icons within h3 (if you embed them as images) */
        width: 24px;
        height: 24px;
        vertical-align: middle;
    }

    .metric-card p {
        color: #555; /* Darker gray for description */
        font-size: 14px;
        line-height: 1.4;
    }
    
    /* Ensure the icons within the metric card headers have correct color if they are svgs/emojis */
    .metric-card h3 .st-emotion-cache-1e7r66k { /* Target specific emoji/icon span */
        color: #6a0dad !important; /* Force purple color */
    }
    .metric-card h3 svg path {
        fill: #6a0dad !important; /* For FontAwesome or similar SVG icons */
    }
    /* Browse files button container and style (Kept) */
    div[data-testid="stFileUploader"] > div:nth-child(2) button {
        position: relative !important;
        display: block !important;
        margin: 12px auto 0 auto !important;
        background: #ffffff !important;
        border: 2px solid #000 !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.3rem !important;
        font-weight: 700 !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.25);
    }
    
    /* CRITICAL FIX for Browse files button text color (Kept) */
    div[data-testid="stFileUploader"] button p, 
    div[data-testid="stFileUploader"] button label,
    div[data-testid="stFileUploader"] button span {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stFileUploader"] > div:nth-child(2) button div {
        color: #000000 !important;
    }
    div[data-testid="stFileUploader"] button {
        color: #000000 !important;
    }

    div[data-testid="stFileUploader"] > div:nth-child(2) button:hover {
        background: #f3f3f3 !important; 
        transform: scale(1.05) !important;
    }
    </style>
""", unsafe_allow_html=True)







# -----------------------------------
# Sidebar Navigation
# -----------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1055/1055644.png", width=80)
    st.title("AI Driven Analytics 🚀")
    selected = option_menu(
        "Navigation",
        ["🏠 Home", "🧹 Preprocessing", "📊 Visualization", "🤖 Model Building", "💡 AI Insights"],
        icons=["house", "tools", "bar-chart", "cpu", "lightbulb"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "4px 0"},
            "nav-link-selected": {"background-color": "#9b30ff"},
        },
    )
    uploaded_file = st.file_uploader("📂 Upload CSV/Excel file", type=["csv", "xlsx"])

# -----------------------------------
# Hero Section
# -----------------------------------
st.markdown("""
    <div class="hero-section">
        <h1 style="color:white; font-size: 40px;">🚀 AI Driven Analytics Dashboard</h1>
        <p style="color:white; font-size: 18px; margin-top:10px;">
            Unlock insights, visualize trends, and build predictive models — all in one place.
        </p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------
# HOME PAGE
# -----------------------------------
if selected == "🏠 Home":
    st.subheader("👋 Welcome to AIDriven Analytics")
    st.write("Upload your dataset in the sidebar to get started.")
    st.markdown("""
        <div class="metric-card-container">
            <div class="metric-card">
                <h3>🧹 Preprocessing</h3>
                <p>Clean & Prepare Data</p>
            </div>
            <div class="metric-card">
                <h3>📊 Visualization</h3>
                <p>Discover Trends</p>
            </div>
            <div class="metric-card">
                <h3>🤖 Modeling</h3>
                <p>Train Predictive Models</p>
            </div>
            <div class="metric-card">
                <h3>💡 AI Insights</h3>
                <p>AI-Generated Analysis</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------
# FILE HANDLING
# -----------------------------------
elif uploaded_file:
    # Load Data
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # -----------------------------------
    # PREPROCESSING
    # -----------------------------------
    if selected == "🧹 Preprocessing":
        st.title("🧹 Data Preprocessing")
        st.subheader("Raw Data Preview")
        st.dataframe(df.head())

        st.subheader("Duplicate Check")
        duplicate_count = df.duplicated().sum()
        if duplicate_count == 0:
            st.success("No duplicate rows found ✅")
        else:
            st.warning(f"Found {duplicate_count} duplicate rows. Removing duplicates...")
            df = df.drop_duplicates()
            st.info("Duplicates removed")

        st.subheader("Missing Value Treatment")
        missing = df.isnull().sum()
        st.dataframe(missing[missing > 0])

        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].mean())
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode()[0])

        st.success("✅ Missing values handled automatically")
        st.dataframe(df.head())

    # -----------------------------------
    # VISUALIZATION
    # -----------------------------------
    elif selected == "📊 Visualization":
        st.title("📊 Visualization Dashboard")
        tab1, tab2 = st.tabs(["Univariate", "Bivariate"])

        with tab1:
            st.markdown("### 📈 Univariate Analysis")
            for col in numeric_cols[:4]:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.histogram(df, x=col, nbins=30, template="plotly_dark", title=f"{col} Distribution"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.box(df, y=col, template="plotly_dark", title=f"{col} Box Plot"), use_container_width=True)

        with tab2:
            st.markdown("### 🔗 Bivariate Analysis")
            if len(numeric_cols) > 1:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], template="plotly_dark",
                                               title=f"{numeric_cols[0]} vs {numeric_cols[1]}"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.violin(df, y=numeric_cols[0], x=numeric_cols[1], box=True, points="all",
                                              template="plotly_dark", title=f"{numeric_cols[0]} vs {numeric_cols[1]} Violin"), use_container_width=True)

    # -----------------------------------
    # MODEL BUILDING
    # -----------------------------------
    elif selected == "🤖 Model Building":
        st.title("🤖 Automated Model Building")
        target_col = st.selectbox("🎯 Select Target Column", df.columns)

        X = df.drop(columns=[target_col])
        y = df[target_col]
        X_encoded = pd.get_dummies(X, drop_first=True)

        is_classification = y.dtype == 'object' or len(y.unique()) < 20
        if is_classification:
            le = LabelEncoder()
            y = le.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        models = (
            {"Random Forest": RandomForestClassifier(),
             "Logistic Regression": LogisticRegression(max_iter=1000),
             "Decision Tree": DecisionTreeClassifier()}
            if is_classification else
            {"Random Forest Regressor": RandomForestRegressor(),
             "Linear Regression": LinearRegression(),
             "Decision Tree Regressor": DecisionTreeRegressor()}
        )

        best_model_name = None
        best_score = -np.inf

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            st.subheader(f"📘 {name} Results")
            if is_classification:
                acc = accuracy_score(y_test, y_pred)
                st.write(f"Accuracy: {acc:.4f}")
                cm = confusion_matrix(y_test, y_pred)
                fig, ax = plt.subplots()
                sns.heatmap(cm, annot=True, fmt="d", cmap="Purples", ax=ax)
                st.pyplot(fig)
                score = acc
            else:
                r2 = r2_score(y_test, y_pred)
                st.write(f"R² Score: {r2:.4f}")
                score = r2
            if score > best_score:
                best_score = score
                best_model_name = name

        st.success(f"🏆 Best Model: {best_model_name} (Score: {best_score:.4f})")

    # -----------------------------------
    # AI INSIGHTS
    # -----------------------------------
    elif selected == "💡 AI Insights":
        st.title("💡 AI Insights & Quick Stats")
        st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")

        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            st.subheader("📊 Top Correlations")
            corr = df.corr().abs().unstack().sort_values(ascending=False)
            corr = corr[corr != 1].drop_duplicates()
            st.dataframe(corr.head(10))

        st.subheader("📋 Column Insights")
        for col in df.columns:
            st.write(f"**{col}** → Unique: {df[col].nunique()}, Most Frequent: {df[col].mode()[0]}")

        # AI Generated Insight
        st.subheader("🤖 AI-Generated Overview")

        def get_ai_insights(df):
            sample_summary = df.describe().transpose().to_string()
            sample_rows = df.head(10).to_string()
            prompt = f"""
            You are a data analyst. Provide a detailed dataset overview including:
            - Column names and data types
            - Summary statistics
            - Observed trends or correlations
            - Potential data issues or missing values
            - Suggestions for next steps

            Summary:
            {sample_summary}

            Sample:
            {sample_rows}
            """
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful data analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700
            )
            return response.choices[0].message.content

        if st.button("✨ Generate AI Insight"):
            with st.spinner("Analyzing dataset..."):
                insight_text = get_ai_insights(df)
                st.success("✅ Insight Generated")
                st.write(insight_text)

# -----------------------------------
# Fallback if No File
# -----------------------------------
else:
    st.warning("⬆️ Please upload a CSV or Excel file to begin.")
