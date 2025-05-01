# 🧼 Image Cleanup Pipeline

This project is designed to audit, clean, and organize a large collection of product image files, matching them to a master product catalog by `style_cd`. It helps identify missing images, orphaned files, and standardize the image repository for production use.

---

## 📁 Project Structure

image_cleanup/
├── scan_drive.py              # Scans full drive for image files and builds initial audit  
├── enrich_audit.py            # Adds image metadata (size, resolution) and copies clean images  
├── fuzzy_matcher.py           # (WIP) Recovers fuzzy matches for missing styles  
├── utils/  
│   ├── image_tools.py         # Image metadata helpers  
│   └── file_ops.py            # File operations (copying, moving)  
├── data/                      # Raw input data (.csv)  
├── output/                    # Cleaned image folder + enhanced audit outputs  
│   └── cleaned_images/  
├── README.md  
└── .gitignore  

---

## 🚀 How It Works

### 1. `scan_drive.py`
- Recursively scans the image directory
- Maps style numbers to full image paths
- Compares with a master list (`StyleImageData.csv`)
- Outputs an audit: `style_image_audit.csv`

### 2. `enrich_audit.py`
- Reads the audit
- Adds file size and resolution columns
- Copies valid images into a standardized clean folder

### 3. `fuzzy_matcher.py` *(Coming soon)*
- Will use string similarity (e.g. Levenshtein distance) to recover partial matches
- Helps find styles with typos or extra characters

---

## ✅ To Do
- [x] Build working audit generator  
- [x] Add resolution & file size enrichment  
- [x] Organize cleaned image folder  
- [ ] Implement fuzzy matching  
- [ ] Validate and tag orphan images  
- [ ] Train back office team on audit review and SOP  

---

## 📦 Requirements

```bash
pip install pandas pillow

👤 Author
Managed by Rafi Khouzam, built for Aneri Jewel's internal product image cleanup and catalog matching.
