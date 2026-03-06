<div align="center">
  <h1>🖼️ LoRA Master Ultimate</h1>
  <p><strong>Professional web interface for lightning-fast image dataset tagging</strong></p>
  <p>Designed for Stable Diffusion trainers and LoRA creators.</p>

  <!-- Бейджи (можно добавить свои) -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Flask-2.0-red?logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker" alt="Docker">
    <img src="https://img.shields.io/github/license/yourusername/lora-master" alt="License">
  </p>

  <!-- Скриншот интерфейса (главный) -->
  <img src="screenshots/image 1.png" alt="LoRA Master Interface" width="800">
</div>

---

## ✨ Key Features

| | |
|---|---|
| **Smart Bulk Operations** | Add tags to all images or selected ones at a specific position (e.g., set your Trigger Word as the 1st tag). |
| **Dataset Health Check** | Automatically identifies images with missing `.txt` files and creates them on the fly. |
| **Tag Analytics** | Real-time stats with sorting by Frequency or Alphabet. |
| **Precision Control** | Select specific images using checkboxes for targeted tagging. |
| **Intuitive UI** | Drag-and-drop tag reordering and `Ctrl+Click` to delete. |

---

## 📸 Interface Preview

<div align="center">
  <img src="screenshots/image 1.png" alt="Dashboard" width="45%">
  <img src="screenshots/image 2.png" alt="Tag Editor" width="45%">
  <br>
</div>

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/lora-master.git
cd lora-master

# Build the Docker image
docker build -t lora-master .

# Run the container (mount your dataset folder)
docker run -p 5000:5000 -v /path/to/your/dataset:/data lora-master
```

Then open http://localhost:5000 in your browser.
Manual Setup (without Docker)
bash

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

📖 Usage Guide

    Prepare your dataset
    Place images (.jpg, .jpeg, .png, .webp) in a folder.
    Optionally, add .txt files with comma-separated tags (same base name as image).

    Launch the app and open the browser.

    Browse and filter images using the search bar or by clicking on tags in the global stats bar.

    Select images with checkboxes for bulk operations.

    Add/remove tags:

        Individually: Type a tag in the input field under a card and press Enter or click "Add".

        Bulk: Enter a tag in the toolbar, choose position (0 = end, 1 = first), and click "Add Tag" or "Delete Tag Everywhere".

        Reorder: Drag and drop tags inside any card.

        Delete single tag: Ctrl+Click on a tag.

    Check missing .txt files – cards with red "MISSING TXT" badge indicate images without a text file; they will be created automatically when you save tags.

⚙️ Advanced Tips

    Copy tag between search and bulk field: Use the ⬇️ / ⬆️ buttons in the toolbar.

    Sort global tags: Click "Name A-Z" or "Popularity" in the stats bar.

    Select all visible: Use "Select All Visible" button after filtering.

    Bulk delete with caution: If no checkboxes are selected, the tag will be removed from ALL files – a confirmation dialog will appear.

🛠️ Built With

    Flask – lightweight Python web framework

    SortableJS – drag-and-drop reordering

    Docker – easy deployment

🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the issues page.
📄 License

This project is MIT licensed.
