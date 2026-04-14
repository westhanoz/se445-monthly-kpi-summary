"""
HW1 KPI Automation Pipeline (Python / Antigravity Implementation)
This script represents a 5-step automated workflow that completely covers the HW1 checklist requirements.
"""

import csv
import urllib.request
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# You need to install google-generativeai to use the Gemini actual call
# Run in terminal: pip install google-generativeai

# --- CONFIGURATION VARIABLES (FILL THESE IN) ---
GOOGLE_SHEET_ID = '1hUAB_xPaccYO4RACQ1IVbe_Mk8hUi-GVGGfzB-Gsmlg'

# Get this from https://aistudio.google.com/
GEMINI_API_KEY = 'AIzaSyCH87AO8GThMFqF_L50GXwrGVTIv13Oryc'

# Gmail Setup
GMAIL_ADDRESS = 'emirbatuhanozturk@gmail.com'
GMAIL_APP_PASSWORD = 'amdw zzez crtm fjrp' # Needs to be an App Password (16-chars), not your regular password!
RECIPIENT_EMAIL = 'emirbatuhanozturk@gmail.com'
# -----------------------------------------------


# Step 1: Schedule Trigger
# Explanation: For a real deployment, we would use Windows Task Scheduler, Cron, or a loop.
# For homework demonstration, running the script manually acts as our triggered execution.
def step_1_schedule_trigger():
    print("[STEP 1] Schedule Trigger activated. Initiating monthly execution.")

# Step 2: Google Sheets Connection (External API)
def step_2_fetch_sheets_data():
    print("[STEP 2] Fetching KPI data from Google Sheets API...")
    csv_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv"
    try:
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            reader = list(csv.DictReader(lines))
            print(f"         ✅ Data fetched successfully! {len(reader)} months found.")
            return reader
    except Exception as e:
        print(f"         ❌ Error reading Google Sheets: {e}")
        return None

# Step 3: Processing Function
def step_3_process_data(data):
    print("[STEP 3] Formatting data to send to AI...")
    if not data:
        return None
        
    latest_data = data[-1] # Grabbing the most recent month for summarization
    
    formatted_data = {
        "Period": latest_data.get('Month', 'N/A'),
        "Financials": f"${int(latest_data.get('Revenue', 0)):,.0f} Revenue with ${int(latest_data.get('Marketing_Spend', 0)):,.0f} Marketing Spend.",
        "User_Base": f"{latest_data.get('Active_Users', 'N/A')} active users. {latest_data.get('New_Customers', 0)} new acquisitions.",
        "Performance_Metrics": f"Satisfaction: {latest_data.get('Customer_Satisfaction', 'N/A')}/10, Churn Rate: {latest_data.get('Churn_Rate', 'N/A')}%, Conversion Rate: {latest_data.get('Conversion_Rate', 'N/A')}%"
    }
    
    # Converting the dictionary to a nicely readable JSON format for the AI
    return json.dumps(formatted_data, indent=4)

# Step 4: AI Summarization using Gemini API
def step_4_ai_summarization(processed_json):
    print("[STEP 4] Calling Gemini AI for summarization...")
    if GEMINI_API_KEY == 'ENTER_YOUR_GEMINI_API_KEY_HERE':
        print("         ⚠️ [WARNING] Gemini API Key not set! Yielding a mock summary to demonstrate workflow structure.")
        return f"Mock AI Summary: In the period of {json.loads(processed_json)['Period']}, the overall performance was stable with positive growth metrics across active user bases."
        
    try:
        from google import genai
        # Initialize the modern client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Crafting our custom prompt combining the raw values
        prompt = f"Summarize the following KPI data in a short, professional paragraph for company executives. Point out any interesting ratios or takeaways:\n{processed_json}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        print("         ✅ AI generated a successful summary!")
        return response.text.strip()
    except Exception as e:
        print(f"         ❌ Error calling Gemini API: {e}")
        return "Failed to generate AI summary due to API Error."

# Step 5: Email Notification via Gmail
def step_5_send_email(summary_text, period):
    print(f"[STEP 5] Sending AI Summary via Email for {period}...")
    if GMAIL_APP_PASSWORD == 'YOUR_GMAIL_APP_PASSWORD_HERE':
        print("         ⚠️ [WARNING] Gmail credentials not set! Skipping real email delivery.")
        print("         (Please create a Gmail App Password per guide to test live delivery)")
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"📈 Monthly Executive KPI Summary - {period}"
        
        body = f"Hello Team,\n\nPlease find the automated AI summary of our latest KPIs below:\n\n{summary_text}\n\nBest,\nAntigravity Bot"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("         ✅ Email notification sent successfully to recipients!")
    except Exception as e:
        print(f"         ❌ Error sending email: {e}")


# Pipeline Execution
if __name__ == "__main__":
    print("="*60)
    print("🚀 PIPELINE START")
    print("="*60)
    
    step_1_schedule_trigger()
    
    kpi_records = step_2_fetch_sheets_data()
    
    if kpi_records:
        processed_data_json = step_3_process_data(kpi_records)
        
        ai_summary = step_4_ai_summarization(processed_data_json)
        
        print("\n" + "-"*40)
        print(f"  🤖 AI GENERATED SUMMARY FOR EXECUTIVES  ")
        print("-" *40)
        print(ai_summary)
        print("-" * 40 + "\n")
        
        period = json.loads(processed_data_json)['Period']
        step_5_send_email(ai_summary, period)
        
        print("\n🏆 WORKFLOW COMPLETED SUCCESSFULLY.")
    else:
        print("\n❌ WORKFLOW FAILED DUE TO DATA READ ERROR.")
