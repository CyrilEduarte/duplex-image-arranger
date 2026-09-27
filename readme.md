# 🖨️ Duplex A4 Image Arranger

A high-precision print imposition and layout application built with Streamlit and ReportLab. This tool converts image sequences and batch assets into print-ready, double-sided (duplex) A4 PDF documents with automatic grid positioning, column mirroring, and color profile preservation.

---

## ✨ Key Features

### 🔄 Dual Imposition Modes
* **Mode A: Repeater (Batch Mode)**
  * Fills an entire page grid (8 or 10 slots) with copies of a single front image.
  * Processes multiple images in batch, outputting consolidated front and back PDF sets.
  * Supports repeating a single uniform back design or assigning sequential backs across grid slots.
* **Mode B: Sequential Mode**
  * Arranges an ordered sequence of distinct images across continuous page grids.
  * Pairs ordered front image sequences with either a static repeating back image or a matching sequence of unique back designs.

### 📐 Precision Layout & Duplex Alignment
* **Automatic Back-Side Mirroring:** Automatically flips column positioning on back pages so front and back cards align perfectly when printed and turned along the long edge.
* **Custom Grid Rows:** Choose between **4 rows** (8 cards per page) or **5 rows** (10 cards per page) on standard A4 dimensions ($92.7 \text{ mm} \times 56.7 \text{ mm}$ per slot).
* **Millimetric Offset Adjustments:** Fine-tune horizontal ($X$) and vertical ($Y$) grid positioning in millimeters to compensate for printer alignment drift.
* **Batch Merging:** Option to merge multiple generated batch pages into unified master Front and Back PDF files or export them as individual files.

### 🎨 Print & Color Safe
* **CMYK Color Preservation:** Automatically detects CMYK color spaces and applies uncompressed JPEG encoding to preserve native CMYK channels without forcing RGB conversions.
* **ICC Metadata Support:** Preserves embedded color profiles across processed assets.
* **High-Resolution Bypass:** Relaxes default pixel bounds (`DecompressionBombError`) to seamlessly render 300+ DPI print graphics.

---

## 📄 Supported File Types

| Asset Type | Supported Formats | Color Profile Handling |
| :--- | :--- | :--- |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff` | CMYK (JPEG/TIFF) & RGB (PNG/JPEG) |
| **Documents** | `.pdf` (Single or multi-page) | Rasterized at target DPI |

---

## ⚙️ Configurable Options

* **Target DPI:** Adjust output resolution (72 to 1200 DPI; default is 300 DPI).
* **Grid Selection:** Toggle between 4-row ($2 \times 4$) and 5-row ($2 \times 5$) page grids.
* **Margins & Shifts:** Independent $X$-offset and $Y$-offset controls in millimeter increments.
* **Back-Side Logic:** Toggle back-side generation on/off, and select between uniform repeat or sequential pairing modes.
