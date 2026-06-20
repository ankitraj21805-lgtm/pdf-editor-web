import os
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, send_file, redirect, session
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = "sbi-randomizer-clean-engine-2026"

# --- ACCESS MANAGEMENT ---
CLIENT_USERNAME = "admin"
CLIENT_PASSWORD = "clientpassword123"

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>SBI Automation & Structural Editor</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #eef2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 25px rgba(0,0,0,0.08); width: 650px; }
        h2 { color: #0284c7; margin-top: 0; text-align: center; border-bottom: 2px solid #bae6fd; padding-bottom: 10px; }
        h3 { color: #0369a1; font-size: 14px; margin-top: 20px; background: #f0f9ff; padding: 6px 12px; border-left: 4px solid #0284c7; font-weight: bold; }
        input[type="text"], input[type="password"], input[type="file"] { width: 100%; padding: 10px; margin: 6px 0 12px 0; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
        .row { display: flex; gap: 12px; }
        .row div { flex: 1; }
        button { width: 100%; padding: 14px; background: #0284c7; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; margin-top: 15px; }
        button:hover { background: #0369a1; }
        label { font-size: 12px; color: #475569; font-weight: 600; display: block; margin-top: 4px; }
        .info-box { background: #f8fafc; border: 1px dashed #cbd5e1; padding: 12px; margin: 10px 0; border-radius: 6px; font-size: 12px; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# Helper function to generate realistic Indian banking transaction entries automatically
def generate_random_transactions(start_date_str, end_date_str, initial_balance):
    try:
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y")
    except:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
    names = ["SHOBHA", "SUMITM", "SEEMAS", "KOMALS", "RAHULK", "AMANS", "DEEPAKR", "VIKRAMS", "PRIYAM"]
    banks = ["HDFC", "IDFB", "CBIN", "IDIB", "ICICI", "AXIS", "PUNB", "BARB"]
    
    current_bal = initial_balance
    txns = []
    
    # Generate automatic iterations over days
    delta_days = (end_date - start_date).days
    if delta_days <= 0:
        delta_days = 14
        
    for i in range(min(delta_days, 6)): # Restrict row mapping size to avoid multiline overflow
        txn_date = (start_date + timedelta(days=random.randint(0, delta_days))).strftime("%d/%m/%Y")
        is_credit = random.choice([True, False])
        amt = random.randint(5000, 45000)
        
        name = random.choice(names)
        bank = random.choice(banks)
        ref_num = "".join([str(random.randint(0, 9)) for _ in range(12)])
        
        if is_credit:
            current_bal += amt
            desc = f"BY TRANSFER - UPI/CR/{ref_num}/{name}/{bank}"
            debit_str, credit_str = "-", f"{amt:,.2f}"
        else:
            current_bal -= amt
            desc = f"TO TRANSFER - UPI/DR/{ref_num}/{name}/{bank}"
            debit_str, credit_str = f"{amt:,.2f}", "-"
            
        txns.append({
            "date": txn_date,
            "desc": desc,
            "debit": debit_str,
            "credit": credit_str,
            "bal": f"{current_bal:,.2f}"
        })
    return txns

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect('/dashboard')
    error = ""
    if request.method == 'POST':
        if request.form['username'] == CLIENT_USERNAME and request.form['password'] == CLIENT_PASSWORD:
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            error = "Invalid Credentials Entry!"
    return render_template_string(HTML_LAYOUT, content=f"""
    <h2>Access Controlled Gateway</h2>
    {f'<p style="color:red;text-align:center;">{error}</p>' if error else ''}
    <form method="post">
        <label>Operator Username</label><input type="text" name="username" required>
        <label>System Password</label><input type="password" name="password" required>
        <button type="submit">Initialize Dashboard</button>
    </form>
    """)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect('/')
        
    if request.method == 'POST':
        file = request.files['pdf_file']
        if file and file.filename.endswith('.pdf'):
            input_path = "raw_input.pdf"
            output_path = "clean_output.pdf"
            file.save(input_path)
            
            # Form values capture for absolute tracking
            acc_name = request.form['acc_name'].strip().upper()
            acc_num = request.form['acc_num'].strip()
            clear_bal = request.form['clear_bal'].strip()
            branch_code = request.form['branch_code'].strip()
            branch_name = request.form['branch_name'].strip().upper()
            ifsc_code = request.form['ifsc_code'].strip().upper()
            cif_num = request.form['cif_num'].strip()
            start_date = request.form['start_date'].strip()
            end_date = request.form['end_date'].strip()
            
            try:
                base_bal = float(clear_bal.replace(',', ''))
            except:
                base_bal = 1300000.00
                
            # Random dataset engine processing
            generated_ledger = generate_random_transactions(start_date, end_date, base_bal)
            
            doc = fitz.open(input_path)
            font_name = "helv"
            
            # Structural Static Mapping Rules (As highlighted in statement layout)
            static_replacements = {
                "Mr. ABHISHEK REKVAR": acc_name,
                "45222567869": acc_num,
                "45,000.00CR": clear_bal + "CR",
                "12193": branch_code,
                "SATI VIDISHA": branch_name,
                "SBIN0012193": ifsc_code,
                "50046100545": cif_num,
                "14-06-2026": end_date
            }
            
            # Core Text Redaction Execution Loop (Erase & Redraw)
            for page in doc:
                # 1. Clear & Overwrite Static Structural Identifiers
                for old_val, new_val in static_replacements.items():
                    rects = page.search_for(old_val)
                    for rect in rects:
                        page.add_redact_annot(rect, text="")
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                        page.insert_text(rect.tl, new_val, fontsize=9.0, fontname=font_name, color=(0, 0, 0))
                
                # 2. Dynamic History Clean Mapping Logic
                # Original transactional values are systematically erased
                old_row_amounts = ["19,500.00", "13,63,259.65", "36,000.00", "13,99,259.65", "18,100.00", "13,81,159.65", "19,300.00", "13,61,859.65"]
                for old_amt in old_row_amounts:
                    rects = page.search_for(old_amt)
                    for rect in rects:
                        page.add_redact_annot(rect, text="")
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                
                # Wipe the specific description instances
                desc_anchors = ["SHOBHA", "SUMITM", "SEEMAS", "KOMALS"]
                for anchor in desc_anchors:
                    for block in page.get_text("blocks"):
                        if anchor in block[4]:
                            block_rect = fitz.Rect(block[0], block[1], block[2], block[3])
                            page.add_redact_annot(block_rect, text="")
                            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                            
                # 3. Dynamic Random Allocation Redraw Engine 
                # Targets exact transaction layout lines on page 1
                y_cursor = 635  # Anchored base pixel baseline matching original layout parameters
                for txn in generated_ledger:
                    if y_cursor > 750: # Restrict vertical stack footprint
                        break
                    page.insert_text(fitz.Point(50, y_cursor), txn["date"], fontsize=8.5, fontname=font_name)
                    page.insert_text(fitz.Point(120, y_cursor), txn["desc"][:42], fontsize=7.5, fontname=font_name)
                    page.insert_text(fitz.Point(360, y_cursor), txn["debit"], fontsize=8.5, fontname=font_name)
                    page.insert_text(fitz.Point(430, y_cursor), txn["credit"], fontsize=8.5, fontname=font_name)
                    page.insert_text(fitz.Point(490, y_cursor), txn["bal"], fontsize=8.5, fontname=font_name)
                    y_cursor += 22
                    
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            if os.path.exists(input_path):
                os.remove(input_path)
                
            return send_file(output_path, as_attachment=True, download_name="SBI_Randomized_Statement.pdf")

    return render_template_string(HTML_LAYOUT, content="""
    <h2>SBI Dynamic Editor & Randomizer Panel</h2>
    <div class="info-box">
        <strong>Randomization Feature Active:</strong> Har baar statement generate karne par Ledger Entry Data (Transactions, Descriptions, Ref IDs, running values) auto-generate hoga, jabki aapke dwara badle gaye highlighted fields static rahenge.
    </div>
    <form method="post" enctype="multipart/form-data">
        <label>Select Template Base PDF</label>
        <input type="file" name="pdf_file" accept=".pdf" required>
        
        <h3>1. Editable Master Entities (Marked Fields)</h3>
        <label>Account Holder Full Name</label>
        <input type="text" name="acc_name" value="Mr. ABHISHEK REKVAR" required>
        
        <div class="row">
            <div>
                <label>Account Number</label>
                <input type="text" name="acc_num" value="45222567869" required>
            </div>
            <div>
                <label>Starting Target Balance</label>
                <input type="text" name="clear_bal" value="13,43,759.65" required>
            </div>
        </div>

        <div class="row">
            <div>
                <label>Branch Code</label>
                <input type="text" name="branch_code" value="12193" required>
            </div>
            <div>
                <label>Branch Name Location</label>
                <input type="text" name="branch_name" value="SATI VIDISHA" required>
            </div>
        </div>

        <div class="row">
            <div>
                <label>IFSC Code</label>
                <input type="text" name="ifsc_code" value="SBIN0012193" required>
            </div>
            <div>
                <label>CIF Number String</label>
                <input type="text" name="cif_num" value="50046100545" required>
            </div>
        </div>

        <h3>2. Date-Range Criteria Formulation</h3>
        <div class="row">
            <div>
                <label>Timeline Start Date (DD-MM-YYYY)</label>
                <input type="text" name="start_date" value="01-06-2026" required>
            </div>
            <div>
                <label>Timeline End Date (DD-MM-YYYY)</label>
                <input type="text" name="end_date" value="14-06-2026" required>
            </div>
        </div>

        <button type="submit">Auto-Randomize & Export PDF</button>
    </form>
    <br><a href="/logout" style="color:#ef4444; text-decoration:none; font-size:12px; float:right; font-weight:bold;">Logout Dashboard</a>
    """)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
