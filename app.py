from flask import Flask, render_template, request, redirect, session
import psycopg2
import bcrypt

app = Flask(__name__)

conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='1234',
    host='localhost'
)
app.secret_key = 'kunal@1234'

def create_user_table():
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE,
        password VARCHAR(100)
    );
    """
    with conn.cursor() as cursor:
        cursor.execute(create_table_query)
    conn.commit()

create_user_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        conn.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                session['email'] = user[2]
                return redirect('http://localhost:5001/dashboard',code=302)
            else:
                return render_template('login.html',error='Invalid user')

    return render_template('login.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'email' in session:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (session['email'],))
            user = cursor.fetchone()
        return render_template('dashboard.html', user=user)

    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')



if __name__ == '__main__':
    app.run(debug=True,port=5002) 