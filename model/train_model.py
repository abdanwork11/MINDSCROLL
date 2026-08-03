import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# ============================================================
# SESUAIKAN BAGIAN INI
# ============================================================

# Ganti path ke lokasi dataset kamu
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataxdany.csv')

# Ganti dengan nama kolom fitur di CSV kamu (semua kolom kecuali 'label')
# Jalankan dulu: python -c "import pandas as pd; df = pd.read_csv('dataxdany.csv'); print(list(df.columns))"
# lalu ganti col1, col2, dst dengan nama kolom asli dari output perintah di atas
FEATURE_COLUMNS = [
    'x1', 'x2', 'x3', 'x4', 'y5', 'y6', 'y7', 'y8',
    'y9', 'y10', 'y11', 'y12',
]

# Nama kolom target — dari notebook kamu = 'label'
LABEL_COLUMN = 'label'

# ============================================================

def train():
    print("📂 Membaca dataset...")
    df = pd.read_csv(DATASET_PATH)
    print(f"✅ {df.shape[0]} baris, {df.shape[1]} kolom")
    print(f"\nDistribusi label:\n{df['label'].value_counts()}\n")

    X = df.drop(labels='label', axis=1)
    y = df['label']

    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    print(f"Data latih : {x_train.shape}")
    print(f"Data uji   : {x_test.shape}\n")

    # Model persis seperti notebook: criterion='entropy', max_depth=5, random_state=42
    print("🌳 Melatih Decision Tree...")
    clf = DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=42)
    clf.fit(x_train, y_train)

    # Evaluasi
    y_pred = clf.predict(x_test)
    print(f"Akurasi: {accuracy_score(y_test, y_pred)*100:.2f}%")
    print(classification_report(y_test, y_pred))

    # Simpan model
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    joblib.dump(clf, model_path)
    print(f"✅ Model disimpan: {model_path}")

if __name__ == '__main__':
    train()
