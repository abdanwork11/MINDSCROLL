from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import (LoginManager, login_user, login_required,
                          logout_user, current_user)
import joblib
import numpy as np
import os
from datetime import timezone, timedelta

from models import db, User, HasilKlasifikasi

app = Flask(__name__)

# ============================================================
# KONFIGURASI
# ============================================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ganti-dengan-string-rahasia-kamu-sendiri')
database_url = os.environ.get('MYSQL_URL', os.environ.get('DATABASE_URL', 'sqlite:///mindscroll.db'))
if database_url.startswith('mysql://'):
    database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login dulu untuk mengakses halaman ini.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load model Decision Tree
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'model.pkl')
model = joblib.load(MODEL_PATH)


FEATURE_yUMNS = [
    'x1', 'x2', 'x3', 'x4', 'y5', 'y6', 'y7', 'y8',
    'y9', 'y10', 'y11', 'y12'
]

QUESTIONS = [
    {"id": "f1",  "type": "menit", "text": "Berapa lama rata-rata Anda menggunakan aplikasi TikTok dalam satu kali membuka? (dalam satuan menit)"},
    {"id": "f2",  "type": "likert", "text": "Saya sering membuka TikTok dalam sehari."},
    {"id": "f3",  "type": "likert", "text": "Saya sering menggunakan TikTok lebih lama dari yang saya rencanakan."},
    {"id": "f4",  "type": "likert", "text": "Saya sering menggunakan TikTok pada malam hingga larut malam."},
    {"id": "f5",  "type": "likert", "text": "Saya bisa mempertahankan fokus saya dalam jangka waktu lama ketika sedang menonton konten di TikTok."},
    {"id": "f6",  "type": "likert", "text": "Saya dapat menangkap dengan baik informasi dari setiap konten di TikTok yang saya lihat."},
    {"id": "f7",  "type": "likert", "text": "Saya sering tidak menyadari bahwa tangan saya terus melakukan scrolling FYP di TikTok."},
    {"id": "f8",  "type": "likert", "text": "Ketika scrolling TikTok, saya hanya fokus pada konten yang saya lihat dan sulit memikirkan hal lain."},
    {"id": "f9",  "type": "likert", "text": "Saya merasa waktu berjalan sangat cepat ketika saya sedang scrolling di TikTok."},
    {"id": "f10", "type": "likert", "text": "Saya sering menghabiskan waktu di TikTok melebihi batas waktu yang sudah saya tetapkan."},
    {"id": "f11", "type": "likert", "text": "Saya dapat menyelesaikan tugas dengan cepat setelah terlalu lama scrolling TikTok."},
    {"id": "f12", "type": "likert", "text": "Saya sering merasakan mata lelah setelah terlalu lama scrolling TikTok."},
    {"id": "f13", "type": "likert", "text": "Saya sering menyimpan (save) konten penting di TikTok namun jarang membukanya kembali."},
    {"id": "f14", "type": "likert", "text": "Saya sering tidak menyadari kapan saya beralih dari satu konten TikTok ke konten berikutnya."},
    {"id": "f15", "type": "likert", "text": "Saya tidak pernah menunda kewajiban atau pekerjaan ketika sedang scrolling TikTok."},
    {"id": "f16", "type": "likert", "text": "Saya mudah mengingat informasi penting dari konten TikTok dalam waktu yang lama."},
]

LIKERT_OPTIONS = [
    {"value": 1, "label": "Sangat Tidak Setuju"},
    {"value": 2, "label": "Tidak Setuju"},
    {"value": 3, "label": "Netral"},
    {"value": 4, "label": "Setuju"},
    {"value": 5, "label": "Sangat Setuju"},
]

LABEL_INFO = {
    "Rendah": {
        "color": "green",
        "desc": "Penggunaan TikTok kamu masih terkendali. Kamu sadar dan mampu membatasi diri dengan baik. Pertahankan kebiasaan digital yang sehat ini!"
    },
    "Sedang": {
        "color": "yellow",
        "desc": "Ada tanda-tanda kamu mulai kehilangan kendali saat menggunakan TikTok. Perlu sedikit lebih waspada dan mulai atur waktu penggunaan."
    },
    "Tinggi": {
        "color": "red",
        "desc": "Kamu menunjukkan tingkat mindless scrolling yang tinggi. Disarankan untuk mengatur ulang kebiasaan penggunaan TikTok secara lebih serius."
    },
}

def menit_to_skor(menit):
    if menit <= 5:
        return 1
    elif menit <= 15:
        return 2
    elif menit <= 30:
        return 3
    elif menit <= 60:
        return 4
    else:
        return 5


# ============================================================
# AUTH ROUTES
# ============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not password:
            return render_template('register.html', error="Username dan password wajib diisi.")
        if len(password) < 6:
            return render_template('register.html', error="Password minimal 6 karakter.")
        if password != confirm:
            return render_template('register.html', error="Konfirmasi password tidak cocok.")
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username sudah digunakan, pilih yang lain.")

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))

        return render_template('login.html', error="Username atau password salah.")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ============================================================
# MAIN ROUTES
# ============================================================

WIB = timezone(timedelta(hours=7))

@app.template_filter('wib')
def to_wib(dt):
    if dt is None:
        return '-'
    return dt.replace(tzinfo=timezone.utc).astimezone(WIB).strftime('%d %b %Y, %H:%M') + ' WIB'

@app.route('/')
@login_required
def index():
    return render_template('index.html', questions=QUESTIONS, options=LIKERT_OPTIONS)


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        answers = []
        answers_display = []
        menit_asli = None

        for q in QUESTIONS:
            val = request.form.get(q['id'])

            if val is None or val.strip() == '':
                return render_template('index.html',
                                       questions=QUESTIONS,
                                       options=LIKERT_OPTIONS,
                                       error="Harap jawab semua pertanyaan sebelum mengirim.")

            if q['type'] == 'menit':
                menit = int(val)
                if menit <= 0:
                    return render_template('index.html',
                                           questions=QUESTIONS,
                                           options=LIKERT_OPTIONS,
                                           error="Durasi penggunaan TikTok harus lebih dari 0 menit.")
                skor = menit_to_skor(menit)
                menit_asli = menit
                answers.append(skor)
                answers_display.append(f"{menit} menit (skor: {skor})")
            else:
                answers.append(int(val))
                answers_display.append(str(val))

        features = np.array(answers).reshape(1, -1)
        prediction = model.predict(features)[0]
        total = sum(answers)
        max_score = len(QUESTIONS) * 5

        info = LABEL_INFO.get(str(prediction), {
            "yor": "yellow",
            "desc": "Hasil tidak dikenali."
        })

        # Simpan ke database
        hasil = HasilKlasifikasi(
            user_id=current_user.id,
            f1=answers[0], f2=answers[1], f3=answers[2], f4=answers[3],
            f5=answers[4], f6=answers[5], f7=answers[6], f8=answers[7],
            f9=answers[8], f10=answers[9], f11=answers[10], f12=answers[11],
            f13=answers[12], f14=answers[13], f15=answers[14], f16=answers[15],
            menit_asli=menit_asli,
            label=str(prediction),
            total_skor=total,
        )
        db.session.add(hasil)
        db.session.commit()

        return render_template('result.html',
                               label=prediction,
                               color=info['color'],
                               desc=info['desc'],
                               answers=answers,
                               answers_display=answers_display,
                               questions=QUESTIONS,
                               total=total,
                               max_score=max_score)
    except ValueError:
        return render_template('index.html',
                               questions=QUESTIONS,
                               options=LIKERT_OPTIONS,
                               error="Pastikan semua jawaban diisi dengan benar.")
    except Exception as e:
        return render_template('index.html',
                               questions=QUESTIONS,
                               options=LIKERT_OPTIONS,
                               error=f"Terjadi kesalahan: {str(e)}")


@app.route('/riwayat')
@login_required
def riwayat():
    history = (HasilKlasifikasi.query
               .filter_by(user_id=current_user.id)
               .order_by(HasilKlasifikasi.created_at.desc())
               .all())
    return render_template('riwayat.html', history=history, label_info=LABEL_INFO)


with app.app_context():
    db.create_all()  # otomatis buat file/tabel database jika belum ada


@app.route('/export')
@login_required
def export():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    from models import User
    import csv, io
    from datetime import timezone, timedelta
    WIB = timezone(timedelta(hours=7))

    data = HasilKlasifikasi.query.order_by(HasilKlasifikasi.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['No', 'Username', 'Label', 'Total Skor', 'Menit Asli',
                     'f1','f2','f3','f4','f5','f6','f7','f8',
                     'f9','f10','f11','f12','f13','f14','f15','f16',
                     'Waktu (WIB)'])
    for i, d in enumerate(data, 1):
        user = User.query.get(d.user_id)
        username = user.username if user else 'unknown'
        waktu = d.created_at.replace(tzinfo=timezone.utc).astimezone(WIB).strftime('%d/%m/%Y %H:%M') if d.created_at else '-'
        writer.writerow([i, username, d.label, d.total_skor, d.menit_asli or '-',
                         d.f1,d.f2,d.f3,d.f4,d.f5,d.f6,d.f7,d.f8,
                         d.f9,d.f10,d.f11,d.f12,d.f13,d.f14,d.f15,d.f16,
                         waktu])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=data_mindscroll.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return response

if __name__ == '__main__':
    app.run(debug=True)
