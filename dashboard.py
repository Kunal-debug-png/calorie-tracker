from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'kunal@1234'

conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='1234',
    host='localhost'
)

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

def create_health_data_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS health_data (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        weight FLOAT,
        height FLOAT,
        calorie_mon FLOAT,
        calorie_tue FLOAT,
        calorie_wed FLOAT,
        calorie_thu FLOAT,
        calorie_fri FLOAT,
        calorie_sat FLOAT,
        calorie_sun FLOAT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    with conn.cursor() as cursor:
        cursor.execute(create_table_query)
    conn.commit()

create_user_table()
create_health_data_table()

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'email' in session:
        if request.method == 'POST':
            weight = request.form['weight']
            height = request.form['height']
            calorie_mon = request.form['calorie_mon']
            calorie_tue = request.form['calorie_tue']
            calorie_wed = request.form['calorie_wed']
            calorie_thu = request.form['calorie_thu']
            calorie_fri = request.form['calorie_fri']
            calorie_sat = request.form['calorie_sat']
            calorie_sun = request.form['calorie_sun']

            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM users WHERE email = %s", (session['email'],))
                    user_id = cursor.fetchone()[0]
                    cursor.execute("""
                        INSERT INTO health_data (user_id, weight, height, calorie_mon, calorie_tue, calorie_wed, 
                                                 calorie_thu, calorie_fri, calorie_sat, calorie_sun) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, weight, height, calorie_mon, calorie_tue, calorie_wed, calorie_thu, calorie_fri, calorie_sat, calorie_sun))
                conn.commit()
                return redirect('/dashboard')
            except Exception as e:
                conn.rollback()
                print("Error:", e)

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (session['email'],))
            user = cursor.fetchone()
        return render_template('dashboard.html', user=user)

    return redirect('/login')

@app.route('/submit', methods=['POST'])
def submit():
    if 'email' in session:
        if request.method == 'POST':
            
            weight = float(request.form['weight'])
            height = float(request.form['height']) / 100  
            bmi = weight / (height ** 2)
            bmr = 66.47 + ((13.75 * weight) + (5.003 * height) - (6.755 * 30 ))
            little=bmr*1.375
            moderate=bmr*1.55
            active=bmr*1.725
            very_active=bmr*1.9
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (session['email'],))
                user = cursor.fetchone()
                
                cursor.execute("SELECT * FROM health_data WHERE user_id = %s", (user[0],))
                weekly_calories = cursor.fetchone() 

               
                return render_template('userinfo.html', user=user, bmi=bmi, bmr=bmr, little=little, moderate=moderate, active=active, very_active=very_active, weekly_calories=weekly_calories)

    return redirect('/login')




if __name__ == '__main__':
    app.run(debug=True,port=5001)
