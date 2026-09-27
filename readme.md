# 🖨️ Duplex A4 Image Arranger & Imposition Tool

A high-resolution, print-ready imposition utility built with **Streamlit**, **ReportLab**, and **Pillow**. This application automates the layout of image and PDF assets into double-sided (duplex) A4 grids with precise alignment, CMYK color preservation, and automated back-side column mirroring.

---

## ✨ Features

* **Dual Imposition Modes:**
  * **Mode A: Repeater (Batch)** — Duplicates individual assets across full-page grids. Ideal for high-volume runs of identical business cards, badges, or tags.
  * **Mode B: Sequential** — Arranges multi-image sequences across consecutive grid slots in strict order.
* **Smart Duplex Alignment:** Automatically flips column positions on back pages so front and back graphics align when printed double-sided along the long edge.
* **CMYK & Print-Safe:**
  * Preserves native CMYK channels using uncompressed JPEG encoding.
  * Maintains embedded ICC profiles.
  * Bypasses standard image size constraints (`DecompressionBombError`) for ultra-high-resolution assets.
* **Flexible Page Layouts:**
  * Choose between **4-row** or **5-row** grids (2 columns per page).
  * Fine-tune positioning with millimeter-level **X and Y offset controls**.
  * Customizable target DPI (72 to 1200 DPI).
* **Multi-Format Input:** Accepts `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, and `.pdf` files.

---

## 🛠️ Project Structure

```text
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── packages.txt        # System-level dependencies for Streamlit Cloud (Poppler)
└── README.md           # Project documentation
```

---

## 🚀 Quick Start (Local Run)

### 1. Prerequisites
Ensure you have **Python 3.8+** installed. You will also need **Poppler** installed on your system for PDF processing:
* **macOS:** `brew install poppler`
* **Ubuntu/Debian:** `sudo apt-get install -y poppler-utils`
* **Windows:** Download Poppler binaries and add the `bin` directory to your System PATH.

### 2. Installation
Clone the repository and install the dependencies:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git
cd YOUR-REPOSITORY-NAME
pip install -r requirements.txt
```

### 3. Run the App
Launch the Streamlit web interface:

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push your code, `requirements.txt`, and `packages.txt` to a **public GitHub repository**.
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
3. Click **Deploy an app**, select your repository, set the main file path to `app.py`, and click **Deploy**.

---

## 📋 Requirements

### Python (`requirements.txt`)
```text
streamlit
Pillow
reportlab
PyPDF2
pdf2image
```

### System (`packages.txt`)
```text
poppler-utils
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).