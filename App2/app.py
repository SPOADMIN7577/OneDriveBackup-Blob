import streamlit as st
from core.auth import get_app, get_graph_headers
from core.graph import discover_files
from core.blob import get_container
from core.copy_engine import run_copy

# -------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Instacloudsolution | OneDrive to Azure Blob",
    layout="wide"
)

# -------------------------------------------------
# Global Styling (Professional Dark Theme)
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* Remove Streamlit default header */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* Remove Streamlit top padding */
    .block-container{
        padding-top: 0rem;
        padding-bottom: 2rem;
    }

    /* Full app background */
    .stApp {
        background: linear-gradient(180deg, #0B132B 0%, #1C2541 100%);
        color: #FFFFFF;
    }

    h1, h2, h3, h4 {
        color: #FFFFFF !important;
    }

    label {
        color: #E5E7EB !important;
        font-weight: 500;
    }

    .custom-card {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 10px 28px rgba(0,0,0,0.35);
    }

    .stButton > button {
        background-color: #3A86FF;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        border: none;
    }

    .stButton > button:hover {
        background-color: #265DCC;
    }

    .stButton > button:disabled {
        background-color: #4B5563;
        color: #D1D5DB;
    }

    div[data-testid="stProgressBar"] > div > div {
        background-color: #3A86FF;
    }

    .stDownloadButton > button {
        background-color: #22C55E;
        color: white;
        font-weight: 600;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# App Header (Centered)
# -------------------------------------------------
st.markdown(
    """
    <div style="
        width: 100%;
        background: linear-gradient(180deg, #070E27 0%, #0B132B 100%);
        padding: 26px 0 22px 0;
        text-align: center;
        box-shadow: 0 4px 18px rgba(0,0,0,0.45);
    ">
        <div style="
            font-size: 36px;
            font-weight: 700;
            color: white;
        ">
            Instacloudsolution
        </div>
        <div style="
            font-size: 14px;
            color: #9CA3AF;
            margin-top: 4px;
        ">
            OneDrive → Azure Blob Copier
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "copy_done" not in st.session_state:
    st.session_state.copy_done = False

if "report_data" not in st.session_state:
    st.session_state.report_data = []

# -------------------------------------------------
# Layout
# -------------------------------------------------
left_col, right_col = st.columns([3, 2])

# -------------------------------------------------
# LEFT: INPUT CARD
# -------------------------------------------------
with left_col:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    st.subheader("Configuration")

    tenant_id = st.text_input("Tenant ID")
    client_id = st.text_input("Application (Client) ID")
    client_secret = st.text_input("Client Secret", type="password")
    user_email = st.text_input("User Email (UPN)")

    st.subheader("Azure Storage")
    storage_account = st.text_input("Storage Account Name")
    storage_key = st.text_input("Storage Account Key", type="password")
    container_name = st.text_input("Container Name")

    st.subheader("OneDrive Source")
    copy_root = st.toggle("Copy OneDrive Root", value=True)
    onedrive_path = None if copy_root else st.text_input(
        "OneDrive Subfolder Path (e.g. HR Docs/2025)"
    )

    st.subheader("Blob Destination")
    copy_container_root = st.toggle("Copy to Container Root", value=True)
    blob_directory = "" if copy_container_root else st.text_input(
        "Blob Directory (e.g. backups/hrdocs)"
    )

    start_copy = st.button("🚀 Start Copy")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# RIGHT: STATUS CARD
# -------------------------------------------------
with right_col:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    st.subheader("Copy Status")

    current_file_box = st.empty()
    progress_bar = st.progress(0)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# COPY EXECUTION
# -------------------------------------------------
if start_copy:
    st.session_state.copy_done = False
    st.session_state.report_data = []

    app = get_app(tenant_id, client_id, client_secret)
    headers = get_graph_headers(app)

    files = discover_files(headers, user_email, onedrive_path)
    total_files = len(files)

    if total_files == 0:
        st.warning("No files found to copy.")
    else:
        container = get_container(
            storage_account,
            storage_key,
            container_name
        )

        copied_paths = []

        for i, item in enumerate(files, start=1):
            current_file_box.markdown(f"**Copying:** `{item['name']}`")

            uploaded = run_copy(
                files=[item],
                container=container,
                base_dir=blob_directory,
                headers=headers
            )

            if uploaded:
                copied_paths.extend(uploaded)

            progress_bar.progress(i / total_files)

        st.session_state.report_data = copied_paths
        st.session_state.copy_done = True

        st.success("✅ Copy completed successfully")
