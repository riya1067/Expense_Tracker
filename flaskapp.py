from flask import Flask, render_template, request, redirect, flash, session, url_for
import mysql.connector as m
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import pandas as pd
app = Flask(__name__)
app.config['SECRET_KEY'] = "h3ll0_w0rld223991020209292"
db = m.connect(
    host='localhost',
    user='root',
    password='12345678',
    database='expense_tracker'
)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username already exists')
            return render_template('register.html')
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('mainpage'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route("/")
def homepage():
    return render_template('homepage.html')
@app.route("/main")
@login_required
def mainpage():
    cursor = db.cursor(dictionary=True)
    username = session['username']
    cursor.execute("SELECT * FROM posts WHERE username = %s ORDER BY date_added DESC", (username,))
    posts = cursor.fetchall()
    return render_template('mainpage.html', posts=posts)
@app.route("/add_new", methods=['GET', 'POST'])
@login_required
def add_new():
    if request.method == 'POST':
        category = request.form['category']
        content = request.form['content']
        amount = request.form['amount']
        date = request.form['date_added']
        username = session['username']
        errors = []
        if len(category) > 50:
            errors.append("Maximum Length Of The Category Must Be 50 Characters!")
        if len(content) > 50:
            errors.append("Maximum Length Of The Content Must Be 50 Characters!")
        if not amount.replace('.', '').isdigit():
            errors.append("Amount Must Be A Numeric Value!")
        if errors:
            for error in errors:
                flash(error)
            return render_template('add_new.html', category=category, content=content, amount=amount, date=date)

        cursor = db.cursor()
        category = category[0].upper() + category[1:].lower()
        cursor.execute("INSERT INTO posts (category, content, amount, date_added, username) VALUES (%s, %s, %s, %s, %s)",
                       (category, content, amount, date, username))
        db.commit()
        return redirect("/main")

    return render_template('add_new.html')
@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').strip().lower()
    username = session['username']
    cursor = db.cursor(dictionary=True)
    input_query = f"%{query}%"
    sql_query = """
        SELECT * FROM posts
        WHERE username = %s AND (category LIKE %s
    """
    input = [username, input_query]
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    if query in months:
        sql_query += "OR MONTHNAME(date_added) LIKE %s"
        input.append(f"%{query}%")
    elif len(query.split()) == 2 and query.split()[1].isdigit():
        month, day = query.split()
        sql_query += "OR (MONTHNAME(date_added) LIKE %s AND DAY(date_added)=%s)"
        input.extend([f"%{month}%", day])
    elif len(query.split()) == 2 and query.split()[1].isdigit() and len(query.split()[1]) == 4:
        month, year = query.split()
        sql_query += "OR (MONTHNAME(date_added) LIKE %s AND YEAR(date_added)=%s)"
        input.extend([f"%{month}%", year])
    elif len(query.split()) == 3 and query.split()[1].isdigit() and query.split()[2].isdigit() and len(query.split()[2]) == 4:
        month, day, year = query.split()
        sql_query += "OR (MONTHNAME(date_added) LIKE %s AND DAY(date_added)=%s AND YEAR(date_added)=%s)"
        input.extend([f"%{month}%", day, year])
    elif query.isdigit() and len(query) == 4:
        sql_query += "OR YEAR(date_added)=%s"
        input.append(query)
    sql_query += ")"
    cursor.execute(sql_query, tuple(input))
    search_results = cursor.fetchall()
    return render_template('mainpage.html', posts=search_results)
@app.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete_post(id):
    username = session['username']
    cursor = db.cursor()
    cursor.execute("DELETE FROM posts WHERE id=%s AND username=%s", (id, username))
    db.commit()
    if cursor.rowcount == 0:
        flash("Post not found or you don't have permission to delete it.")
        return redirect(url_for('mainpage'))
    return '', 204
@app.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_post(id):
    username = session['username']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts WHERE id=%s AND username=%s", (id, username))
    post = cursor.fetchone()
    if not post:
        flash("Post not found or you don't have permission to update it.")
        return redirect(url_for('mainpage'))
    if request.method == 'POST':
        category = request.form['category']
        content = request.form['content']
        amount = request.form['amount']
        date = request.form['date_added']
        cursor = db.cursor()
        category = category[0].upper() + category[1:].lower()
        cursor.execute("""
            UPDATE posts 
            SET category=%s, content=%s, amount=%s, date_added=%s 
            WHERE id=%s AND username=%s """, (category, content, amount, date, id, username))
        db.commit()
        return redirect(url_for('mainpage'))
    return render_template('update.html', post=post)
@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        username = session['username']
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT category, content, amount, date_added
            FROM posts 
            WHERE username = %s AND date_added BETWEEN %s AND %s
            ORDER BY date_added
        """, (username, start_date, end_date))
        expenses = cursor.fetchall()
        if not expenses:
            return render_template('analyze.html', message="No expenses found for the selected period.")
        category_summary = defaultdict(float)
        detailed_expense_list = []
        total_expense = 0.0
        for expense in expenses:
            category_summary[expense['category']] += float(expense['amount'])
            total_expense += float(expense['amount'])
            detailed_expense_list.append({
                'date': expense['date_added'].strftime('%Y-%m-%d'),
                'category': expense['category'],
                'name': expense['content'],
                'amount': float(expense['amount'])
            })
        labels = list(category_summary.keys())
        sizes = list(category_summary.values())

        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')  
        ax.set_title('Expense Breakdown by Category')
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        pie_chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        expense_df = pd.DataFrame(detailed_expense_list)
        expense_df = expense_df.sort_values('date') 
        expense_df.loc[len(expense_df)] = ['', 'Total', '', total_expense]  
        table_html = expense_df.to_html(index=False, float_format=lambda x: f'{x:.2f}' if isinstance(x, float) else x)
        return render_template('analyze.html', pie_chart_data=pie_chart_data, table_html=table_html)
    return render_template('analyze.html')

    