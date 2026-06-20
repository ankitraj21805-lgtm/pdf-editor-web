import os
from flask import Flask, request, render_template_string, send_file, redirect, session
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = "sbi-true-erase-engine-2026"

# --- LOGIN CREDENTIALS ---
CLIENT_USERNAME = "admin"
CLIENT_PASSWORD = "85807"

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>SBI Professional Document Panel</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #eef2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 25px rgba(0,0,0,0.08); width: 600px; }
        h2 { color: #0284c7; margin-top: 0; text-align: center; border-bottom: 2px solid #bae6fd; padding-bottom: 10px; }
        h3 { color: #0369a1; font-size: 14px; margin-top: 20px; background: #f0f9ff; padding: 6px 12px; border-left: 4px solid #0284c7; font-weight: bold; }
        input[type="text"], input[type="password"], input[type="file"] { width: 100%; padding: 10px; margin: 6px 0 12px 0; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
        .row { display: flex; gap: 12px; }
        .row div { flex: 1; }
        button { width: 100%; padding: 14px; background: #0284c7; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; margin-top: 15px; }
        button:hover { background: #0369a1; }
        label { font-size: 12px; color: #475569; font-weight: 600; display: block; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
"""

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
            error = "Invalid Credentials!"
            
    login_form = f"""
    <h2>SBI Operator System</h2>
    {f'<p style="color:red;text-align:center;">{error}</p>' if error else ''}
    <form method="post">
        <label>Username</label><input type="text" name="username" required>
        <label>Password</label><input type="password" name="password" required>
        <button type="submit">Unlock Editor</button>
    </form>
    """
    return render_template_string(HTML_LAYOUT, content=login_form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect('/')
        
    if request.method == 'POST':
        file = request.files['pdf_file']
        
        if file and file.filename.endswith('.pdf'):
            input_path = "temp_in.pdf"
            output_path = "temp_out.pdf"
            file.save(input_path)
            
            doc = fitz.open(input_path)
            font_name = "helv"  # Standard clean vector matching font
            
            # Pure Dynamic Dictionary Mapping based on statement parameters
            replacements = {
                "Mr. ABHISHEK REKVAR": request.form['acc_name'].strip().upper(),
                "45222567869": request.form['acc_num'].strip(),
                "45,000.00CR": request.form['clear_bal'].strip() + "CR",
                "12193": request.form['branch_code'].strip(),
                "SATI VIDISHA": request.form['branch_name'].strip().upper(),
                "SBIN0012193": request.form['ifsc_code'].strip().upper(),
                "50046100545": request.form['cif_num'].strip(),
                "14-06-2026": request.form['statement_date'].strip(),
                
                # Transaction amounts & balances
                "19,500.00": request.form['t1_amount'].strip(),
                "13,63,259.65": request.form['t1_balance'].strip(),
                "36,000.00": request.form['t2_amount'].strip(),
                "13,99,259.65": request.form['t2_balance'].strip(),
                "18,100.00": request.form['t3_amount'].strip(),
                "13,81,159.65": request.form['t3_balance'].strip(),
                "19,300.00": request.form['t4_amount'].strip(),
                "13,61,859.65": request.form['t4_balance'].strip(),
            }
            
            for page in doc:
                for old_val, new_val in replacements.items():
                    if not old_val or not new_val:
                        continue
                        
                    rects = page.search_for(old_val)
                    for rect in rects:
                        # 1. TEXT ERASE ENGINE (Redaction apply karke backend se raw text permanently remove karein)
                        page.add_redact_annot(rect, text="") 
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                        
                        # 2. SMOOTH REDRAW (Naye text ko fresh layer par automatic correct size me inject karein)
                        page.insert_text(
                            rect.tl, 
                            new_val, 
                            fontsize=9.0,        # Exact standard bank statement sizing
                            fontname=font_name, 
                            color=(0, 0, 0)
                        )
            
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            if os.path.exists(input_path):
                os.remove(input_path)
                
            return send_file(output_path, as_attachment=True, download_name="SBI_Statement_Erase_Done.pdf")

    dashboard_form = """
    <h2>SBI True Erase & Redraw Master Panel</h2>
    <form method="post" enctype="multipart/form-data">
        <label>Upload Target SBI Statement PDF</label>
        <input type="file" name="pdf_file" accept=".pdf" required>
        
        <h3>1. Bank Branch & Profile Metadata</h3>
        <label>Account Holder Full Name</label>
        <input type="text" name="acc_name" value="Mr. ABHISHEK REKVAR" required>
        
        <div class="row">
            <div>
                <label>Account Number</label>
                <input type="text" name="acc_num" value="45222567869" required>
            </div>
            <div>
                <label>Clear Balance Amount</label>
                <input type="text" name="clear_bal" value="45,000.00" required>
            </div>
        </div>

        <div class="row">
            <div>
                <label>Branch Code</label>
                <input type="text" name="branch_code" value="12193" required>
            </div>
            <div>
                <label>Branch Name</label>
                <input type="text" name="branch_name" value="SATI VIDISHA" required>
            </div>
        </div>

        <div class="row">
            <div>
                <label>IFSC Code</label>
                <input type="text" name="ifsc_code" value="SBIN0012193" required>
            </div>
            <div>
                <label>CIF Number</label>
                <input type="text" name="cif_num" value="50046100545" required>
            </div>
        </div>

        <label>Date of Statement / Generation Date</label>
        <input type="text" name="statement_date" value="14-06-2026" required>

        <h3>2. Transaction Records & Financial Ledger</h3>
        
        <label>Transaction Item 1 (SHOBHA Transfer)</label>
        <div class="row">
            <input type="text" name="t1_amount" value="19,500.00" placeholder="Amount">
            <input type="text" name="t1_balance" value="13,63,259.65" placeholder="Running Balance">
        </div>

        <label>Transaction Item 2 (SUMITM Transfer)</label>
        <div class="row">
            <input type="text" name="t2_amount" value="36,000.00" placeholder="Amount">
            <input type="text" name="t2_balance" value="13,99,259.65" placeholder="Running Balance">
        </div>

        <label>Transaction Item 3 (SEEMAS Transfer)</label>
        <div class="row">
            <input type="text" name="t3_amount" value="18,100.00" placeholder="Amount">
            <input type="text" name="t3_balance" value="13,81,159.65" placeholder="Running Balance">
        </div>

        <label>Transaction Item 4 (KOMALS Transfer)</label>
        <div class="row">
            <input type="text" name="t4_amount" value="19,300.00" placeholder="Amount">
            <input type="text" name="t4_balance" value="13,61,859.65" placeholder="Running Balance">
        </div>

        <button type="submit">Execute Absolute Erase & Export</button>
    </form>
    <br><a href="/logout" style="color:#ef4444; text-decoration:none; font-size:13px; float:right; font-weight:bold;">Log out System</a>
    """
    return render_template_string(HTML_LAYOUT, content=dashboard_form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
