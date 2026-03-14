# 🛰️ Military Radar & Electronic Warfare (EW) Simulator PRO

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)
![Radar](https://img.shields.io/badge/Field-Radar%20Engineering-green)

An **interactive radar simulation platform** demonstrating modern radar engineering concepts including:

- Radar Cross Section (RCS)
- Doppler signal processing
- Electronic Warfare (EW)
- Radar detection performance

---

# ✈️ Aircraft Models

| Aircraft | Type | Typical RCS |
|--------|------|------|
| F-22 Raptor | Stealth Fighter | -40 dBsm |
| F-16 Fighting Falcon | Conventional Fighter | 10 dBsm |
| MQ-9 Reaper | Military Drone | -5 dBsm |

---

# ⚙️ Features

### 📡 Radar Cross Section Simulation
- Calculates RCS using **Physical Optics approximation**
- Uses **3D facet models**
- Generates **360° radar signature plots**

### 📈 Frequency Sweep Analysis
- Radar frequency range **1–40 GHz**

### 🚁 Doppler Radar Processing
- FFT-based velocity estimation

### ⚔️ Electronic Warfare
- Noise jamming
- Deception jamming
- Signal-to-Jammer Ratio (SJR)

---

# 🧠 Technologies Used

- Python
- Streamlit
- NumPy
- SciPy
- Plotly

---

# 📂 Project Structure


military-radar-ew-simulator
│
├── radar_simulator_pro.py
├── radar_dsp_ew.py
├── aircraft_models.py
├── requirements.txt
└── README.md


---

# 🚀 How to Run

Clone repository

```bash
git clone https://github.com/eslam-moneer/military-radar-ew-simulator.git

Enter folder

cd military-radar-ew-simulator

Install requirements

pip install -r requirements.txt

Run simulator

streamlit run radar_simulator_pro.py

Application will open at

http://localhost:8501
