"""
HW3 & Final Project: Complete KPI Workflow
Task: Fetch current & previous metrics, compute deltas, use AI to generate an executive summary, 
highlights, and 3 actionable recommendations tailored to a specific persona. Finally, send an HTML email.
"""

import csv
import urllib.request
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION VARIABLES ---
GOOGLE_SHEET_ID = '1hUAB_xPaccYO4RACQ1IVbe_Mk8hUi-GVGGfzB-Gsmlg'
GEMINI_API_KEY = 'AIzaSyCWdzPy662fk5gCQroEKi0mOduWv7rIWgU'

GMAIL_ADDRESS = 'emirbatuhanozturk@gmail.com'
GMAIL_APP_PASSWORD = 'ahcg dyri ixlx aenm'
RECIPIENT_EMAIL = 'emirbatuhanozturk@gmail.com'

# ==========================================
# 🎯 TARGET PERSONA CONFIGURATION
# ==========================================
# This variable allows you to switch the "Tone" and "Style" of the AI.
# Options:
# "Executive" -> Formal, very concise, focus on high-level strategic impact.
# "Team"      -> Motivational, slightly more detailed, focus on operational execution.
#
# -> Change this value to "Team" if you want the AI to act like a team leader.
TARGET_PERSONA = "Executive"
# ==========================================

def step_1_fetch_and_calculate_deltas():
    """
    Connects to Google Sheets, extracts the last two months, and calculates the delta (growth/decline).
    """
    print(f"[STEP 1] Fetching data and calculating deltas...")
    csv_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv"
    
    try:
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            reader = list(csv.DictReader(lines))
            
            if len(reader) < 2:
                print("      ❌ Need at least 2 months of data to calculate deltas.")
                return None
                
            prev_month = reader[-2]
            curr_month = reader[-1]
            
            # Helper function to calculate percentage change
            def calc_delta(curr, prev):
                try:
                    c, p = float(curr), float(prev)
                    if p == 0: return 0.0
                    return ((c - p) / p) * 100
                except ValueError:
                    return 0.0

            # Calculate Deltas for key metrics
            rev_delta = calc_delta(curr_month.get('Revenue', 0), prev_month.get('Revenue', 0))
            users_delta = calc_delta(curr_month.get('Active_Users', 0), prev_month.get('Active_Users', 0))
            churn_diff = float(curr_month.get('Churn_Rate', 0)) - float(prev_month.get('Churn_Rate', 0)) # Churn is already a %, so we find the absolute difference

            structured_data = {
                "Period": curr_month.get('Month', 'Unknown'),
                "Previous_Period": prev_month.get('Month', 'Unknown'),
                "Current_Metrics": {
                    "Revenue": f"${int(float(curr_month.get('Revenue', 0))):,}",
                    "Active_Users": curr_month.get('Active_Users'),
                    "New_Customers": curr_month.get('New_Customers'),
                    "Churn_Rate": f"{curr_month.get('Churn_Rate')}%"
                },
                "Growth_Deltas": {
                    "Revenue_Change": f"{rev_delta:+.1f}%",
                    "Active_Users_Change": f"{users_delta:+.1f}%",
                    "Churn_Rate_Change": f"{churn_diff:+.1f}% points"
                }
            }
            
            print("      ✅ Data fetched and deltas computed successfully!")
            return structured_data
            
    except Exception as e:
        print(f"      ❌ Error reading Google Sheets: {e}")
        return None

def step_2_generate_ai_analysis(structured_data):
    """
    Uses Gemini AI to generate a narrative summary, highlights, and recommendations based on the persona.
    """
    print(f"[STEP 2] Calling Gemini AI as a Data Analyst (Persona: {TARGET_PERSONA})...")
    
    data_json = json.dumps(structured_data, indent=2)
    
    # Customize instructions based on the chosen Persona
    persona_instructions = ""
    if TARGET_PERSONA == "Executive":
        persona_instructions = "Adopt a highly formal, C-level executive tone. Be concise, skip the fluff, and focus strictly on high-level strategic impact and bottom-line figures."
    elif TARGET_PERSONA == "Team":
        persona_instructions = "Adopt an encouraging, operational team-leader tone. Celebrate wins, be motivational, and focus on day-to-day execution and customer impact."
    else:
        persona_instructions = "Adopt a professional, neutral business tone."

    prompt = f"""
You are an expert Data Analyst reporting to the company.
{persona_instructions}

Based on the structured KPI data (including current numbers and growth deltas over the previous month) provided below, write a report formatted EXACTLY as follows:

1. A short narrative Executive Summary (1 paragraph).
2. Key Highlights (3-4 concise bullet points focusing on the deltas).
3. Actionable Recommendations (Exactly 3 numbered recommendations on what the company should do next based on this data).

Ensure you use proper HTML tags (`<p>`, `<ul>`, `<li>`, `<h3>`, `<ol>`) so the output can be injected directly into an HTML email. Do NOT include ````html` or ```` markdown codeblocks, just return the raw HTML structure.

DATA:
{data_json}
"""

    if GEMINI_API_KEY == 'ENTER_YOUR_GEMINI_API_KEY_HERE':
        print("      ⚠️ [WARNING] Gemini API Key not set! Yielding a mock HTML summary.")
        mock_html = f"""
        <h3>Executive Summary</h3>
        <p>In {structured_data['Period']}, the company showed solid momentum with Revenue growing by {structured_data['Growth_Deltas']['Revenue_Change']} compared to {structured_data['Previous_Period']}. Active users expanded steadily, though attention is required to sustain this trajectory.</p>
        <h3>Key Highlights</h3>
        <ul>
            <li>Revenue hit {structured_data['Current_Metrics']['Revenue']}, marking a {structured_data['Growth_Deltas']['Revenue_Change']} change.</li>
            <li>Active user base shifted by {structured_data['Growth_Deltas']['Active_Users_Change']}.</li>
            <li>Churn rate changed by {structured_data['Growth_Deltas']['Churn_Rate_Change']}.</li>
        </ul>
        <h3>Actionable Recommendations</h3>
        <ol>
            <li><strong>Optimize Onboarding:</strong> Investigate user acquisition channels to maximize the active users growth rate.</li>
            <li><strong>Retention Campaigns:</strong> Deploy targeted re-engagement emails to stabilize the churn rate.</li>
            <li><strong>Upsell Features:</strong> Capitalize on the revenue growth momentum by offering premium tiers to the new {structured_data['Current_Metrics']['New_Customers']} customers.</li>
        </ol>
        """
        return mock_html

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        print("      ✅ AI generated the analysis successfully!")
        return response.text.strip()
    except Exception as e:
        print(f"      ❌ Error calling Gemini API: {e}")
        return "<p>Failed to generate AI summary due to API Error.</p>"

def step_3_send_email(html_report, period):
    """
    Wraps the AI-generated HTML content into a professional email template and sends it.
    """
    print(f"[STEP 3] Dispatching Final Report via Email...")
    
    if GMAIL_APP_PASSWORD == 'YOUR_GMAIL_APP_PASSWORD_HERE':
        print("      ⚠️ [WARNING] Gmail credentials not set! Skipping real email delivery.")
        return

    # Wrap the AI output in a nice layout
    full_html = f"""
    <html>
      <head>
        <style>
          body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; }}
          .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px; }}
          .header {{ background-color: #2c3e50; color: #ffffff; padding: 15px; border-radius: 6px 6px 0 0; text-align: center; }}
          .content {{ padding: 20px; background-color: #fcfcfc; }}
          h3 {{ color: #2980b9; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; }}
          .footer {{ margin-top: 20px; font-size: 12px; color: #7f8c8d; text-align: center; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h2>📊 Final KPI Workflow Report ({period})</h2>
            <p style="margin:0; font-size:14px;">Audience Persona: {TARGET_PERSONA}</p>
          </div>
          <div class="content">
            {html_report}
          </div>
          <div class="footer">
            <p>Generated autonomously by the Antigravity AI Pipeline.</p>
          </div>
        </div>
      </body>
    </html>
    """
    
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"🚀 AI Analyst KPI Report - {period} ({TARGET_PERSONA})"
        
        msg.attach(MIMEText(full_html, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"      ✅ Email dispatched successfully to {RECIPIENT_EMAIL}!")
    except Exception as e:
        print(f"      ❌ Error sending email: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🚀 PIPELINE START: HW3 & FINAL PROJECT (FULL WORKFLOW)")
    print("="*60)
    
    data = step_1_fetch_and_calculate_deltas()
    
    if data:
        report_html = step_2_generate_ai_analysis(data)
        step_3_send_email(report_html, data['Period'])
        print("\n🏆 FULL WORKFLOW COMPLETED SUCCESSFULLY.")
    else:
        print("\n❌ WORKFLOW FAILED.")
