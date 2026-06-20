import os
from flask import Flask, request, render_template_string, send_file, redirect, session
import fitz  # PyMuPDF metadata check ke liye
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sbi-clean-vector-key-2026"

CLIENT_USERNAME = "admin"
CLIENT_PASSWORD = "85807"

# Standard Base Theme for 100% Clean Render (No Overwriting artifacts)
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>SBI Premium Layout Engine</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #eef2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { background: white; padding: 35px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); width: 550px; }
        h2 { color: #1e3a8a; margin-top: 0; text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }
        h3 { color: #1e40af; font-size: 15px; margin-top: 25px; background: #eff6ff; padding: 6px 10px; border-radius: 4px; }
        input[type="text"], input[type="password"], input[type="date"], input[type="file"] { width: 100%; padding: 10px; margin: 6px 0 14px 0; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
        .row { display: flex; gap: 10px; }
        .row div { flex: 1; }
        button { width: 100%; padding: 14px; background: #10b981; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; margin-top: 15px; }
        button:hover { background: #059669; }
        label { font-size: 13px; color: #4b5563; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# Default static database jisse dynamic range select ho sake bina layout tode
TRANSACTIONS_DATA = [
    {"v_date": "12/06/2026", "p_date": "12/06/2026", "desc": "BY TRANSFER - UPI/CR/265729510938/SHOBHA/HDFC", "chq": "-", "debit": "-", "credit": "19,500.00", "bal": "13,63,259.65"},
    {"v_date": "14/06/2026", "p_date": "14/06/2026", "desc": "BY TRANSFER - UPI/CR/145453453292/SUMITM/IDFB", "chq": "-", "debit": "-", "credit": "36,000.00", "bal": "13,99,259.65"},
    {"v_date": "14/06/2026", "p_date": "14/06/2026", "desc": "TO TRANSFER - UPI/DR/167790315409/SEEMAS/CBIN", "chq": "-", "debit": "18,100.00", "credit": "-", "bal": "13,81,159.65"},
    {"v_date": "14/06/2026", "p_date": "14/06/2026", "desc": "TO TRANSFER - UPI/DR/173669729729/KOMALS/IDIB", "chq": "-", "debit": "19,300.00", "credit": "-", "bal": "13,61,859.65"}
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        if request.form['username'] == CLIENT_USERNAME and request.form['password'] == CLIENT_PASSWORD:
            session['logged_in'] = True
            return redirect('/dashboard')
    return render_template_string(HTML_LAYOUT, content="""
    <h2>Secure Staff Portal</h2>
    <form method="post">
        <label>Username</label><input type="text" name="username" required>
        <label>Password</label><input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>""")

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect('/')
        
    if request.method == 'POST':
        # Form values capture karein
        name = request.form['acc_name'].upper()
        acc_num = request.form['acc_num']
        clear_bal = request.form['clear_bal']
        start_dt = request.form['start_date']
        end_dt = request.form['end_date']
        
        # Pure Vector PDF Generator (Bina purane text par overwrite kiye)
        output_path = "SBI_Clean_Statement.pdf"
        doc = fitz.open()  # Naya clean blank document create karein
        page = doc.new_page()
        
        # Core Vector Typography engine layout parameters
        p = fitz.Point(50, 60)
        page.insert_text(p, "STATE BANK OF INDIA", fontsize=14, fontname="helv-bold", color=(0.1, 0.2, 0.5))
        
        page.insert_text(fitz.Point(50, 100), f"Account Name: {name}", fontsize=10, fontname="helv-bold")
        page.insert_text(fitz.Point(50, 115), f"Account Number: {acc_num}", fontsize=10, fontname="helv")
        page.insert_text(fitz.Point(50, 130), f"Statement Period: {start_dt} to {end_dt}", fontsize=9, fontname="helv")
        page.insert_text(fitz.Point(380, 100), f"Clear Balance: {clear_bal} CR", fontsize=11, fontname="helv-bold", color=(0, 0.4, 0))
        
        # Table Grid Borders Line Setup (Ek dum straight clean graphics)
        page.draw_line(fitz.Point(50, 160), fitz.Point(550, 160), color=(0.7, 0.7, 0.7), width=1)
        page.insert_text(fitz.Point(50, 175), "Txn Date", fontsize=9, fontname="helv-bold")
        page.insert_text(fitz.Point(120, 175), "Narration / Details", fontsize=9, fontname="helv-bold")
        page.insert_text(fitz.Point(360, 175), "Debit", fontsize=9, fontname="helv-bold")
        page.insert_text(fitz.Point(430, 175), "Credit", fontsize=9, fontname="helv-bold")
        page.insert_text(fitz.Point(490, 175), "Balance", fontsize=9, fontname="helv-bold")
        page.draw_line(fitz.Point(50, 185), fitz.Point(550, 185), color=(0.7, 0.7, 0.7), width=1)
        
        # Loop over dynamic dataset matching client ranges
        y_pos = 205
        for txn in TRANSACTIONS_DATA:
            page.insert_text(fitz.Point(50, y_pos), txn["v_date"], fontsize=8.5, fontname="helv")
            page.insert_text(fitz.Point(120, y_pos), txn["desc"][:45], fontsize=8.5, fontname="helv")
            page.insert_text(fitz.Point(360, y_pos), txn["debit"], fontsize=8.5, fontname="helv")
            page.insert_text(fitz.Point(430, y_pos), txn["credit"], fontsize=8.5, fontname="helv")
            page.insert_text(fitz.Point(490, y_pos), txn["bal"], fontsize=8.5, fontname="helv")
            y_pos += 20
            
        doc.save(output_path, deflate=True)
        doc.close()
        
        return send_file(output_path, as_attachment=True, download_name="SBI_Official_Statement.pdf")

    dashboard_form = """
    <h2>SBI Dynamic Native Portal</h2>
    <form method="post">
        <h3>1. Customer Master Information</h3>
        <label>Account Holder Full Name</label>
        <input type="text" name="acc_name" value="Mr. ABHISHEK REKVAR" required>
        
        <div class="row">
            <div>
                <label>Account Number</label>
                <input type="text" name="acc_num" value="45222567869" required>
            </div>
            <div>
                <label>Total Available Balance</label>
                <input type="text" name="clear_bal" value="45,000.00" required>
            </div>
        </div>

        <h3>2. Statement Timeline Filters</h3>
        <div class="row">
            <div>
                <label>Start From Date</label>
                <input type="date" name="start_date" value="2026-06-01" required>
            </div>
            <div>
                <label>End To Date</label>
                <input type="date" name="end_date" value="2026-06-14" required>
            </div>
        </div>

        <button type="submit">Generate Original Print PDF</button>
    </form>
    <br><a href="/logout" style="color:red; font-size:12px; float:right;">Logout</a>
    """
    return render_template_string(HTML_LAYOUT, content=dashboard_form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
