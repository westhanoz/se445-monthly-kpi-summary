# SE445 - Monthly KPI Summary Pipeline

This repository contains the logic for **HW1: Custom Automated KPI Reporting Workflow** built using pure Python to emulate workflow nodes without relying on 3rd party visual builders like n8n. 

## 🚀 Workflow Architecture

This workflow operates through a 5-step pipelined process completely matching the HW1 grading criteria:

1. **Schedule Trigger (`step_1_schedule_trigger`)**: Acts as a monthly schedule execution initialization. For grading demo purposes, you can trigger this script manually on your terminal.
2. **Google Sheets Connection (`step_2_fetch_sheets_data`)**: Reads data directly from a public Google Sheet using Python's `urllib` to pull the latest Key Performance Indicators (Revenue, Churn Rate, Conversions, etc.) without downloading local files.
3. **Processing Function (`step_3_process_data`)**: Restructures and cleans the raw CSV data into an easily digestible JSON formatted structure.
4. **AI Summarization (`step_4_ai_summarization`)**: Pushes the formatted metrics to the Google **Gemini AI API**, requesting a professional, managerial paragraph summarizing the data health.
5. **Email Delivery (`step_5_send_email`)**: Consumes the generated AI summary and dispatches an automated notification email via Python `smtplib` using Google's SMTP servers to the defined recipient team.

## 🛠 Prerequisites

To run this pipeline locally, you will need the following installed:
- Python 3.8+
- The `google-generativeai` package. Install it via `pip install google-generativeai`

## 🔑 Setup & Configuration

To score the full 100 points via Live Demo, you will need to replace the placeholders in `main_logic.py`:

```python
GOOGLE_SHEET_ID = '1hUAB_xPaccYO4RACQ1IVbe_Mk8hUi-GVGGfzB-Gsmlg' # Already configured
GEMINI_API_KEY = 'ENTER_YOUR_GEMINI_API_KEY_HERE' 
GMAIL_ADDRESS = 'YOUR_EMAIL@gmail.com'
GMAIL_APP_PASSWORD = 'YOUR_GMAIL_APP_PASSWORD_HERE' 
RECIPIENT_EMAIL = 'RECIPIENT_EMAIL@gmail.com'
```

* **Gemini API Key:** You can generate a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
* **Gmail App Password:** You cannot use your standard Google password. Go to your Google Account -> Security -> 2-Step Verification -> App Passwords and create a new 16-character password specifically for this script.

## 🏃 Running the Workflow

Simply run the logic payload through the terminal:
```bash
python main_logic.py
```
