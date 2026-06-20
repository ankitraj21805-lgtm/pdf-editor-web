import os
from flask import Flask, request, render_template_string, send_file, redirect, session
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = "super-secret-free-key-123"  # Session secure karne ke liye

# --- CONFIGURATION (LOGIN DETAILS) ---
# Aap yahan apna username aur password badal sakte hain jo client ko dena hai
CLIENT_USERNAME = "admin"
CLIENT_PASSWORD = "85807"

# Minimal Professional HTML Interface (Single file me setup)
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure PDF Editor Portal</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); width: 400px; }
        h2 { color: #333; margin-top: 0; text-align: center; }
        input[type="text"], input[type="password"], input[type="file"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background: #0056b3; }
        .error { color: red; text-align: center; margin-bottom: 10px; }
        label { font-size: 14px; color: #555; font-weight: 600; }
    </style>
</head>
<body>
    <div class="card">
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
            error = "Invalid Credentials! Please try again."
            
    login_form = f"""
    <h2>Client Login Portal</h2>
    {f'<p class="error">{error}</p>' if error else ''}
    <form method="post">
        <label>Username</label>
        <input type="text" name="username" required>
        <label>Password</label>
        <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    """
    return render_template_string(HTML_LAYOUT, content=login_form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect('/')
        
    if request.method == 'POST':
        file = request.files['pdf_file']
        old_text = request.form['old_text']
        new_text = request.form['new_text']
        
        if file and file.filename.endswith('.pdf'):
            input_path = "temp_input.pdf"
            output_path = "temp_output.pdf"
            file.save(input_path)
            
            # PDF Processing Engine (Bina external font file ke)
            doc = fitz.open(input_path)
            font_name = "helv"  # Default Standard Helvetica (Arial matching)
                
            for page in doc:
                # Purane text ki exact location find karein
                text_instances = page.search_for(old_text)
                for rect in text_instances:
                    # 1. Purane text ko hide karne ke liye white box draw karein
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    
                    # 2. Same coordinate par naya text system font se draw karein
                    page.insert_text(
                        rect.tl, 
                        new_text, 
                        fontsize=9.5,      # Default banking statement size
                        fontname=font_name, 
                        color=(0, 0, 0)    # Pure Black color
                    )
                    
            # Compress aur save karein taaki structure intact rahe
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            
            # Purani temp file delete karein clean-up ke liye
            if os.path.exists(input_path):
                os.remove(input_path)
                
            return send_file(output_path, as_attachment=True, download_name="Modified_Statement.pdf")

    dashboard_form = """
    <h2>PDF Smart Modifier</h2>
    <p style="text-align:center; font-size:13px; color:#777;">Upload PDF and details to auto-align</p>
    <form method="post" enctype="multipart/form-data">
        <label>Select Statement PDF</label>
        <input type="file" name="pdf_file" accept=".pdf" required>
        <label>Find Text (e.g., 45,000.00CR)</label>
        <input type="text" name="old_text" placeholder="Exact old value" required>
        <label>Replace With</label>
        <input type="text" name="new_text" placeholder="Exact new value" required>
        <button type="submit">Process & Download</button>
    </form>
    <br>
    <a href="/logout" style="display:block; text-align:center; color:#ff4d4d; text-decoration:none; font-size:14px;">Logout Portal</a>
    """
    return render_template_string(HTML_LAYOUT, content=dashboard_form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
