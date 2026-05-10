import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()
    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('Please enter a URL!')
            return redirect(url_for('index'))

        url_data = conn.execute('INSERT INTO urls (original_url) VALUES (?)', (url,))
        conn.commit()
        url_id = url_data.lastrowid
        conn.close()

        # Generate short link
        short_url = request.host_url + str(url_id)
        return render_template('index.html', short_url=short_url)

    # Fetch recent URLs to show on the dashboard
    history = conn.execute('SELECT * FROM urls ORDER BY id DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('index.html', history=history)

@app.route('/<int:id>')
def url_redirect(id):
    conn = get_db_connection()
    url_details = conn.execute('SELECT original_url, clicks FROM urls WHERE id = ?', (id,)).fetchone()
    
    if url_details:
        original_url = url_details['original_url']
        clicks = url_details['clicks'] + 1
        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?', (clicks, id))
        conn.commit()
        conn.close()
        return redirect(original_url)
    
    flash('Invalid URL')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)