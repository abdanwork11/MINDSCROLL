from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
    # Relasi ke riwayat hasil klasifikasi milik user ini
    hasil_list = db.relationship('HasilKlasifikasi', backref='user', lazy=True,
                                  cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class HasilKlasifikasi(db.Model):
    __tablename__ = 'hasil_klasifikasi'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 16 jawaban kuesioner (skor 1-5, f1 sudah dikonversi dari menit)
    f1 = db.Column(db.Integer, nullable=False)
    f2 = db.Column(db.Integer, nullable=False)
    f3 = db.Column(db.Integer, nullable=False)
    f4 = db.Column(db.Integer, nullable=False)
    f5 = db.Column(db.Integer, nullable=False)
    f6 = db.Column(db.Integer, nullable=False)
    f7 = db.Column(db.Integer, nullable=False)
    f8 = db.Column(db.Integer, nullable=False)
    f9 = db.Column(db.Integer, nullable=False)
    f10 = db.Column(db.Integer, nullable=False)
    f11 = db.Column(db.Integer, nullable=False)
    f12 = db.Column(db.Integer, nullable=False)
    f13 = db.Column(db.Integer, nullable=False)
    f14 = db.Column(db.Integer, nullable=False)
    f15 = db.Column(db.Integer, nullable=False)
    f16 = db.Column(db.Integer, nullable=False)

    menit_asli = db.Column(db.Integer, nullable=True)  # durasi menit asli sebelum dikonversi (f1)
    label = db.Column(db.String(20), nullable=False)   # Rendah / Sedang / Tinggi
    total_skor = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_answers_list(self):
        """Kembalikan 16 jawaban sebagai list, sesuai urutan f1-f16."""
        return [self.f1, self.f2, self.f3, self.f4, self.f5, self.f6, self.f7, self.f8,
                self.f9, self.f10, self.f11, self.f12, self.f13, self.f14, self.f15, self.f16]
