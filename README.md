# 🧊 Smart Fridge Sensor App

This is a full-stack application that **simulates a smart fridge sensor**. Using your **webcam**, it detects items going **in and out of the fridge** and updates the **fridge inventory** accordingly.

Behind the scenes, the app captures a camera frame and uses a powerful **LLM** (Large Language Model) to identify the item shown. Based on user input (`Add` or `Delete`), the inventory is updated in **Firebase**.

---

## 🧠 Overview

- **LLM:** [`ollama-llama3.2-vision-11b`](https://replicate.com/lucataco/ollama-llama3.2-vision-11b)
- **Frontend:** Built with **Next.js + Tailwind + Material UI**
- **Backend:** **Flask** server handles LLM requests and Firebase updates
- **Database:** **Firebase Firestore** stores inventory data

---

## 🌐 Web Pages

| Route     | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| `/`       | Landing page with introduction and description                              |
| `/fridge` | Live fridge simulation with webcam, item detection, and inventory tracking  |

---

## ⚙️ Features

✅ Simulates a fridge sensor using your webcam  
✅ Uses an **LLM to identify items visually**  
✅ Captures frame when **Add** or **Delete** is clicked  
✅ Dynamically **updates Firebase inventory**  
✅ Clean UI built with Material UI + Tailwind  
✅ Auto-refresh and status popups for detected items

---

## 🛠️ Setup Guide

### 🔌 Backend (Flask API)

1. `cd flask-backend`
2. Create virtual environment:

   - **Mac/Linux**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

   - **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your Replicate API token:
   ```env
   REPLICATE_API_TOKEN=<YOUR_API_TOKEN>
   ```

5. Run the Flask server:
   ```bash
   python app.py
   ```

---

### 💻 Frontend (Next.js)

1. `cd ts-frontend`
2. Install dependencies:
   ```bash
   npm i
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```

---

## 📸 Example Workflow

1. Go to `/fridge`
2. Your webcam activates
3. Hold an item in front of the camera
4. Click **Add** ➕ or **Delete** 🗑️
5. The LLM identifies the object (e.g., "Tofu")
6. The inventory is updated in Firebase!

---

## 📦 Technologies Used

- **React / Next.js**
- **Material UI**
- **Tailwind CSS**
- **Flask**
- **Firebase Firestore**
- **Replicate (LLM API)**

---

## 🧪 Credits

Built with ❤️ for a fridge that’s smarter than your roommate.  
Made for CS614 ✨
