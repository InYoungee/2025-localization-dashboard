# 2025 Localization Project Dashboard

An interactive Streamlit dashboard for analyzing localization project performance in the gaming industry. Built with Python, Pandas, Plotly, Matplotlib, and Seaborn.

## 🔗 Live Demo 

[View Dashboard](https://2025-localization-dashboard-npw82kyv5mmsauwrs43egu.streamlit.app/) 

## Features

- **Word Count Trends**: Monthly and quarterly volume analysis
- **Game Performance**: Project counts, word counts, and LQA intensity by game
- **Linguist Workload**: Distribution analysis for in-house translators vs. vendors
- **Bubble Chart**: Project volume vs. word count with average WC per project
- **Interactive Filters**: Game selection and toggle views for deeper insights

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Matplotlib
- Seaborn

## Local Setup
```bash
git clone https://github.com/yourusername/2025-localization-dashboard.git
cd 2025-localization-dashboard
pip install -r requirements.txt
streamlit run l10n_dashboard.py
```

## Data

The CSV contains anonymized localization project data including game titles, request types (Translation/LQA), word counts, linguist assignments, and project dates.

![Web Interface Dashboard](https://github.com/InYoungee/2025-localization-dashboard/blob/main/images/dashboard.gif)
---

© 2025 Inyoung Kim | Built with Python & Streamlit
