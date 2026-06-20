import os
from flask import Flask, request, render_template_string, send_file, redirect, session
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = "sbi-panel-secure-key-2026"

# --- LOGIN CREDENTIALS ---
CLIENT_USERNAME = "admin"
CLIENT_PASSWORD = "85807"

# Clean Dashboard UI Layout
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>SBI PDF Core Layout Editor</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #eef2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { background: white; padding: 35px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); width: 500px; }
        h2 { color: #1e3a8a; margin-top: 0; text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }
        h3 { color: #4b5563; font-size: 16px; margin-top: 20px; border-left: 4px solid #10b981; padding-left: 8px; }
        input[type="text"], input[type="password"], input[type="file"] { width: 100%; padding: 10px; margin: 8px 0 15px 0; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
        .row { display: flex; gap: 10px; }
        .row input { flex: 1; }
        button { width: 100%; padding: 14px; background: #1e40af; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; margin-top: 15px; }
        button:hover { background: #1d4ed8; }
        .error { color: #dc2626; text-align: center; font-weight: bold; }
        label { font-size: 13px; color: #374151; font-weight: 600; display: block; margin-top: 5px; }
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
    <h2>Secure Client Portal</h2>
    {f'<p class="error">{error}</p>' if error else ''}
    <form method="post">
        <label>Username</label>
        <input type="text" name="username" required>
        <label>Password</label>
        <input type="password" name="password" required>
        <button type="submit">Login Portal</button>
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
            font_name = "helv"  # Precise Helvetica vector alignment
            
            # Map values from Form Input Fields
            replacements = {
                # Account Details Section
                "Mr. ABHISHEK REKVAR": request.form['acc_name'].strip(),
                "45222567869": request.form['acc_num'].strip(),
                "45,000.00CR": request.form['clear_bal'].strip() + "CR",
                
                # Dynamic Transaction Items Mapped from Images
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
                    
                    # Target exact bounding box positions
                    rects = page.search_for(old_val)
                    for rect in rects:
                        # Draw masking box to preserve document vectors
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        # Apply layout matching text overwrite
                        page.insert_text(
                            rect.tl, 
                            new_val, 
                            fontsize=9.5, 
                            fontname=font_name, 
                            color=(0, 0, 0)
                        )
            
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            
            if os.path.exists(input_path):
                os.remove(input_path)
                
            return send_file(output_path, as_attachment=True, download_name="SBI_Statement_Fixed.pdf")

    dashboard_form = """
    <h2>SBI Layout Smart Panel</h2>
    <form method="post" enctype="multipart/form-data">
        <label>Upload Original SBI Statement PDF</label>
        <input type="file" name="pdf_file" accept=".pdf" required>
        
        <h3>1. Primary Account Metadata</h3>
        <label>Account Holder Name</label>
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

        <h3>2. Transaction Details (As Seen In Images)</h3>
        
        <label>Transaction 1 (Transfer - SHOBHA)</label>
        <div class="row">
            <input type="text" name="t1_amount" value="19,500.00" placeholder="Amount">
            <input type="text" name="t1_balance" value="13,63,259.65" placeholder="Running Balance">
        </div>

        <label>Transaction 2 (Transfer - SUMITM)</label>
        <div class="row">
            <input type="text" name="t2_amount" value="36,000.00" placeholder="Amount">
            <input type="text" name="t2_balance" value="13,99,259.65" placeholder="Running Balance">
        </div>

        <label>Transaction 3 (Transfer - SEEMAS)</label>
        <div class="row">
            <input type="text" name="t3_amount" value="18,100.00" placeholder="Amount">
            <input type="text" name="t3_balance" value="13,81,159.65" placeholder="Running Balance">
        </div>

        <label>Transaction 4 (Transfer - KOMALS)</label>
        <div class="row">
            <input type="text" name="t4_amount" value="19,300.00" placeholder="Amount">
            <input type="text" name="t4_balance" value="13,61,859.65" placeholder="Running Balance">
        </div>

        <button type="submit">Modify Layout & Download PDF</button>
    </form>
    <br>
    <a href="/logout" style="display:block; text-align:center; color:#ef4444; text-decoration:none; font-size:13px; font-weight:bold;">Secure Logout</a>
    """
    return render_template_string(HTML_LAYOUT, content=dashboard_form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
