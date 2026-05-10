import sqlite3
import string
import random
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---Function to generate a random 5-character code ---
def generate_short_code(length=5):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()
    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('Please enter a URL!')
            return redirect(url_for('index'))

        # Generate the random code
        short_code = generate_short_code()

        # Save the URL and the random code to the database
        conn.execute('INSERT INTO urls (original_url, short_code) VALUES (?, ?)', (url, short_code))
        conn.commit()
        conn.close()

        # Show the new random short link to the user
        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)

    history = conn.execute('SELECT * FROM urls ORDER BY id DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('index.html', history=history)

@app.route('/<string:code>')
def url_redirect(code):
    conn = get_db_connection()
    url_details = conn.execute('SELECT id, original_url, clicks FROM urls WHERE short_code = ?', (code,)).fetchone()
    
    if url_details:
        original_url = url_details['original_url']
        clicks = url_details['clicks'] + 1
        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?', (clicks, url_details['id']))
        conn.commit()
        conn.close()
        return redirect(original_url)
    
    flash('Invalid URL')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)