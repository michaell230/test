from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Konfigurasi Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="gebrielrahmawati",
    database="ezzplore"
)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form["username_or_email"]
        password = request.form["password"]
        
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT * FROM pengguna 
            WHERE (EMAIL = %s OR NAMA = %s) AND PASSWORD = %s
        """
        cursor.execute(query, (username_or_email, username_or_email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Debug print untuk melihat struktur data
            print("User data:", user)  # Temporary debug line
            
            # Simpan data user ke session dengan nama kolom yang benar
            session['nama'] = user['NAMA']
            session['nomor_telepon'] = user['NOMOR_TELEPON']
            return redirect(url_for("main_menu"))
        else:
            flash("Nama/email atau password salah, coba lagi.")
    
    return render_template("index.html")

@app.route('/main_menu')
def main_menu():
    try:
        # Ambil data user dari session
        nama = session.get('nama')
        nomor_telepon = session.get('nomor_telepon')
        
        # Ambil data paket wisata dari database
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM PAKET_WISATA ORDER BY HARGA"
        cursor.execute(query)
        packages = cursor.fetchall()
        cursor.close()
        
        # Debug print
        print("Packages retrieved:", packages)  # Untuk melihat data yang diambil
        
        return render_template('main_menu.html', 
                             nama=nama,
                             nomor_telepon=nomor_telepon,
                             packages=packages)
    except Exception as e:
        print("Error in main_menu route:", str(e))  # Debug print untuk error
        return render_template('main_menu.html', 
                             nama=nama,
                             nomor_telepon=nomor_telepon,
                             packages=[])

# # Halaman login
# @app.route("/", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username_or_email = request.form["username_or_email"]
#         password = request.form["password"]
        
#         cursor = db.cursor(dictionary=True)
#         query = """
#             SELECT * FROM pengguna 
#             WHERE (EMAIL = %s OR NAMA = %s) AND PASSWORD = %s
#         """
#         cursor.execute(query, (username_or_email, username_or_email, password))
#         user = cursor.fetchone()
#         cursor.close()
        
#         if user:
#             # Simpan data user ke session
#             session['user_id'] = user['ID']
#             session['nama'] = user['NAMA']
#             session['nomor_telepon'] = user['NOMOR_TELEPON']
#             return redirect(url_for("main_menu"))
#         else:
#             flash("Nama/email atau password salah, coba lagi.")
    
#     return render_template("index.html")

# masukkan tanggal lahir

@app.route('/register1', methods=['GET', 'POST'])
def register1():
    if request.method == 'POST':
        # Ambil data dari form
        dob_str = request.form.get('dob')  # 'dob' adalah name dari input tanggal lahir

        # Validasi format dan usia
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')  # Ubah string menjadi tanggal
            age = (datetime.now() - dob).days // 365  # Hitung usia berdasarkan tanggal lahir
            if age < 18:
                flash('Usia minimal untuk mendaftar adalah 18 tahun.')
                return redirect(url_for('register1'))  # Kembali ke halaman register jika usia tidak valid
        except ValueError:
            flash('Format tanggal lahir tidak valid. Gunakan format yyyy-mm-dd.')
            return redirect(url_for('register1'))

        # Simpan tanggal lahir sementara di sesi (untuk digunakan di register2)
        session['dob'] = dob_str

        return redirect(url_for('register2'))  # Arahkan ke halaman register2 setelah berhasil

    return render_template('p2.html')  # Render halaman register1 (tanggal lahir)

@app.route('/register2', methods=['GET', 'POST'])
def register2():
    if request.method == 'POST':
        # Ambil data dari form
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Ambil tanggal lahir dari sesi
        dob_str = session.get('dob')
        if dob_str:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')  # Ubah string tanggal lahir kembali menjadi datetime

            # Masukkan data ke dalam database
            cursor = db.cursor()
            query = "INSERT INTO pengguna (nama, email, nomor_telepon, password, tanggal_lahir) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, password, dob))
            db.commit()
            cursor.close()

            flash("Akun berhasil dibuat. Silakan login.")
            return redirect(url_for('login'))  # Redirect ke halaman login setelah berhasil
        else:
            flash("Terjadi kesalahan, tanggal lahir tidak ditemukan.")
            return redirect(url_for('register1'))  # Kembali ke halaman register1 jika tidak ada tanggal lahir

    return render_template('p3.html')  # Render halaman register2 (data diri)


# @app.route('/main_menu')
# def main_menu():
#     # Ambil data user dari session
#     nama = session.get('nama')
#     nomor_telepon = session.get('nomor_telepon')
    
#     return render_template('main_menu.html', 
#                          nama=nama,
#                          nomor_telepon=nomor_telepon)

@app.route('/tiket_pesawat')
def tiket_pesawat():
    return render_template('p5.html')

@app.route('/cari_hotel')
def cari_hotel():
    return render_template('p7.html')

@app.route('/daftar_hotel')
def daftar_hotel():
    return render_template('p6.html')

@app.route('/struk')
def struk():
    return render_template('p8.html')


if __name__ == "__main__":
    app.run(debug=True)