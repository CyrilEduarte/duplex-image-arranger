import os
import tempfile
import math
from io import BytesIO
import streamlit as st
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyPDF2 import PdfWriter

# Increase max image size to prevent DecompressionBombError for high-res print files
Image.MAX_IMAGE_PIXELS = None

# Set page configuration
st.set_page_config(
    page_title="Duplex Arranger (CMYK/RGB Safe)",
    page_icon="🖨️",
    layout="wide"
)

# --- HELPER FUNCTIONS ---

def prepare_image(uploaded_file, dpi, w_mm, h_mm):
    """Processes an uploaded file/path and returns a path to a temp resized image."""
    if uploaded_file is None:
        return None
    try:
        if isinstance(uploaded_file, str):
            # If path string was provided
            if uploaded_file.lower().endswith('.pdf'):
                from pdf2image import convert_from_path
                img = convert_from_path(uploaded_file, dpi=dpi)[0]
            else:
                img = Image.open(uploaded_file)
        else:
            # If Streamlit UploadedFile object was provided
            if uploaded_file.name.lower().endswith('.pdf'):
                from pdf2image import convert_from_bytes
                img = convert_from_bytes(uploaded_file.read(), dpi=dpi)[0]
            else:
                img = Image.open(uploaded_file)

        img = ImageOps.exif_transpose(img)
        
        # --- COLOR MODE PRESERVATION LOGIC ---
        target_format = 'PNG' # Default safe choice for RGB/Grayscale
        save_args = {'dpi': (dpi, dpi)}

        if img.mode == 'CMYK':
            target_format = 'JPEG'
            save_args['quality'] = 100 # Max quality to avoid artifacts
            save_args['subsampling'] = 0 # No chroma subsampling
            suffix = '.jpg'
        else:
            suffix = '.png'

        # Resize (LANCZOS preserves mode generally)
        px_w = int(w_mm / 25.4 * dpi)
        px_h = int(h_mm / 25.4 * dpi)
        img = img.resize((px_w, px_h), Image.LANCZOS)
        
        fd, tmp = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        
        # Handle ICC Profiles if present
        if 'icc_profile' in img.info:
            save_args['icc_profile'] = img.info['icc_profile']
            
        img.save(tmp, format=target_format, **save_args)
        return tmp
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None


def generate_dual_streams(front_items, back_items, out_path_f, out_path_b, dpi, off_x, off_y, rows, progress_bar, status_text, progress_offset=0.0, progress_chunk=1.0):
    c_f = canvas.Canvas(out_path_f, pagesize=A4)
    c_b = canvas.Canvas(out_path_b, pagesize=A4) if back_items else None

    img_w_mm, img_h_mm = 92.7, 56.7
    img_w_pt = img_w_mm * mm
    img_h_pt = img_h_mm * mm
    
    top_margin = (6.2907 if rows == 4 else 4.0) * mm + off_y * mm
    side_margin_base = (A4[0] - (2 * img_w_pt)) / 2
    center_x = A4[0] / 2 + off_x * mm

    items_per_page = rows * 2
    total_items = len(front_items)
    num_pages = math.ceil(total_items / items_per_page)

    for p_idx in range(num_pages):
        start = p_idx * items_per_page
        end = start + items_per_page
        chunk_front = front_items[start:end]

        current_pct = progress_offset + ((p_idx + 1) / num_pages) * progress_chunk
        progress_bar.progress(min(current_pct, 1.0))
        status_text.text(f"Arranging page {p_idx + 1} of {num_pages}...")

        # --- DRAW FRONT PAGE ---
        c_f.setStrokeColorRGB(0.8, 0.8, 0.8)
        c_f.setLineWidth(1)
        c_f.line(center_x, 0, center_x, A4[1]) 

        for i, f_file in enumerate(chunk_front):
            col = i % 2
            row = i // 2
            x = (side_margin_base + off_x * mm) + (col * img_w_pt)
            y = A4[1] - top_margin - (row * img_h_pt) - img_h_pt
            
            tmp = prepare_image(f_file, dpi, img_w_mm, img_h_mm)
            if tmp:
                c_f.drawImage(tmp, x, y, img_w_pt, img_h_pt)
                os.unlink(tmp)
        
        c_f.showPage()

        # --- DRAW BACK PAGE ---
        if c_b:
            c_b.setStrokeColorRGB(0.8, 0.8, 0.8)
            c_b.setLineWidth(1)
            c_b.line(center_x, 0, center_x, A4[1])

            chunk_back_indices = range(start, start + len(chunk_front))
            chunk_back = [back_items[k % len(back_items)] if back_items else None for k in chunk_back_indices]

            for i, b_file in enumerate(chunk_back):
                if not b_file: continue
                
                front_col = i % 2
                back_col = 1 if front_col == 0 else 0 
                row = i // 2
                
                x = (side_margin_base + off_x * mm) + (back_col * img_w_pt)
                y = A4[1] - top_margin - (row * img_h_pt) - img_h_pt
                
                tmp = prepare_image(b_file, dpi, img_w_mm, img_h_mm)
                if tmp:
                    c_b.drawImage(tmp, x, y, img_w_pt, img_h_pt)
                    os.unlink(tmp)
            
            c_b.showPage()

    c_f.save()
    if c_b: 
        c_b.save()


def merge_pdfs(pdf_paths):
    """Merges a list of PDF file paths into an in-memory BytesIO buffer."""
    merger = PdfWriter()
    for pdf in pdf_paths:
        merger.append(pdf)
    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return output


# --- APP INTERFACE ---

st.title("🖨️ Duplex Arranger (CMYK/RGB Safe)")

# Sidebar Settings
st.sidebar.header("Configuration Settings")
dpi = st.sidebar.number_input("DPI Resolution", min_value=72, max_value=1200, value=300, step=50)
rows = st.sidebar.radio("Rows per Page", options=[4, 5], index=0)

col_off1, col_off2 = st.sidebar.columns(2)
off_x = col_off1.number_input("X Offset (mm)", value=0.0, step=0.5)
off_y = col_off2.number_input("Y Offset (mm)", value=0.0, step=0.5)

# Mode Navigation Tabs
tab_repeater, tab_sequential = st.tabs(["Mode A: Repeater (Batch)", "Mode B: Sequential (Sequence)"])

# ---------------- MODE A: REPEATER ----------------
with tab_repeater:
    st.subheader("Batch Processing Mode")
    
    rep_front_files = st.file_uploader(
        "Select Image(s) to repeat across pages:",
        type=["jpg", "jpeg", "tif", "tiff", "png", "pdf"],
        accept_multiple_files=True,
        key="rep_front"
    )
    
    rep_back_active = st.checkbox("Enable Back Side", key="rep_back_active")
    rep_back_files = []
    rep_back_mode = "rep"
    
    if rep_back_active:
        rep_back_mode = st.radio(
            "Back Logic:",
            options=["rep", "seq"],
            format_func=lambda x: "Repeater (Same back for all slots)" if x == "rep" else "Sequential (Different back for slots 1-8)",
            key="rep_back_mode"
        )
        rep_back_files = st.file_uploader(
            "Select Back Side Image(s):",
            type=["jpg", "jpeg", "tif", "tiff", "png", "pdf"],
            accept_multiple_files=True,
            key="rep_back_files"
        )

    var_merge = st.checkbox("Merge Repeater batches into a single Front/Back PDF set", value=True)

# ---------------- MODE B: SEQUENTIAL ----------------
with tab_sequential:
    st.subheader("Sequential Processing Mode")
    
    seq_front_files = st.file_uploader(
        "Select Images (Sequence):",
        type=["jpg", "jpeg", "tif", "tiff", "png", "pdf"],
        accept_multiple_files=True,
        key="seq_front"
    )
    
    seq_back_active = st.checkbox("Enable Back Side", key="seq_back_active")
    seq_back_files = []
    seq_back_mode = "rep"
    
    if seq_back_active:
        seq_back_mode = st.radio(
            "Back Logic:",
            options=["rep", "seq"],
            format_func=lambda x: "Repeater (Same back for all fronts)" if x == "rep" else "Sequential (Unique back for each front)",
            key="seq_back_mode"
        )
        seq_back_files = st.file_uploader(
            "Select Back Side Images:",
            type=["jpg", "jpeg", "tif", "tiff", "png", "pdf"],
            accept_multiple_files=True,
            key="seq_back_files"
        )

# --- GENERATION CONTROL ---
st.divider()

if st.button("🚀 GENERATE FRONT & BACK PDFs", use_container_width=True, type="primary"):
    cards_per_page = rows * 2
    temp_dir = tempfile.mkdtemp()
    
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    try:
        # Determine active mode based on inputs provided
        if rep_front_files:
            # RUN REPEATER MODE
            temp_front_pdfs = []
            temp_back_pdfs = []
            total_files = len(rep_front_files)

            for i, f_img in enumerate(rep_front_files):
                page_fronts = [f_img] * cards_per_page
                page_backs = []
                
                if rep_back_active and rep_back_files:
                    if rep_back_mode == 'rep':
                        page_backs = [rep_back_files[0]] * cards_per_page
                    else:
                        page_backs = [rep_back_files[k % len(rep_back_files)] for k in range(cards_per_page)]

                out_f = os.path.join(temp_dir, f"chunk_{i}_f.pdf")
                out_b = os.path.join(temp_dir, f"chunk_{i}_b.pdf")
                
                prog_start = i / total_files
                prog_size = 1.0 / total_files
                
                generate_dual_streams(page_fronts, page_backs, out_f, out_b, dpi, off_x, off_y, rows, progress_bar, status_text, prog_start, prog_size)
                
                temp_front_pdfs.append(out_f)
                if rep_back_active: 
                    temp_back_pdfs.append(out_b)

            status_text.text("Finalizing files...")
            
            if var_merge:
                merged_front = merge_pdfs(temp_front_pdfs)
                st.download_button("📥 Download Front PDF", data=merged_front, file_name="Generated_Front.pdf", mime="application/pdf")
                
                if rep_back_active and temp_back_pdfs:
                    merged_back = merge_pdfs(temp_back_pdfs)
                    st.download_button("📥 Download Back PDF", data=merged_back, file_name="Generated_Back.pdf", mime="application/pdf")
            else:
                for idx, tf in enumerate(temp_front_pdfs):
                    with open(tf, "rb") as f:
                        st.download_button(f"📥 Download Front PDF #{idx+1}", data=f.read(), file_name=f"Generated_Front_{idx+1}.pdf", mime="application/pdf")
                if rep_back_active:
                    for idx, tb in enumerate(temp_back_pdfs):
                        with open(tb, "rb") as f:
                            st.download_button(f"📥 Download Back PDF #{idx+1}", data=f.read(), file_name=f"Generated_Back_{idx+1}.pdf", mime="application/pdf")

        elif seq_front_files:
            # RUN SEQUENTIAL MODE
            final_back_list = []
            if seq_back_active and seq_back_files:
                if seq_back_mode == 'rep':
                    final_back_list = [seq_back_files[0]] * len(seq_front_files)
                else:
                    for k in range(len(seq_front_files)):
                        final_back_list.append(seq_back_files[k % len(seq_back_files)])

            out_f = os.path.join(temp_dir, "seq_front.pdf")
            out_b = os.path.join(temp_dir, "seq_back.pdf")
            
            generate_dual_streams(
                seq_front_files, final_back_list, out_f, out_b if seq_back_active else None, 
                dpi, off_x, off_y, rows, progress_bar, status_text, 0.0, 1.0
            )

            status_text.text("Finalizing files...")
            
            with open(out_f, "rb") as f:
                st.download_button("📥 Download Front PDF", data=f.read(), file_name="Sequential_Front.pdf", mime="application/pdf")
            if seq_back_active:
                with open(out_b, "rb") as f:
                    st.download_button("📥 Download Back PDF", data=f.read(), file_name="Sequential_Back.pdf", mime="application/pdf")
        else:
            st.warning("Please upload at least one Front side image to proceed.")

        progress_bar.progress(1.0)
        status_text.success("Complete!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")