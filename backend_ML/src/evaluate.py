import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, mean_absolute_error, mean_squared_error,
                             mean_absolute_percentage_error)

def evaluate_models():
    print("Memuat data dan model...")
    # 1. Load Data Bersih
    filepath = "../dataset/LQ45_Clean.csv"
    df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)

    # 2. Setup Fitur & Target (Harus sama persis dengan train.py)
    features = ['open', 'high', 'low', 'close', 'volume', 
                'EMA_21', 'EMA_99', 'EMA_200', 'RSI_14', 'Stoch_K',
                'MACD', 'Signal_Line', 'Upper_BB', 'Lower_BB', 'Daily_Return']
    
    X = df[features]
    y_reg = df['Target_Price']        
    y_clf = df['Target_Direction']    

    # 3. Belah Data (Kita hanya ambil data X_test dan y_test untuk ujian)
    _, X_test, _, y_reg_test, _, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, shuffle=False
    )

    # 4. Load Models & Scaler yang sudah di-training
    try:
        scaler = joblib.load("../models/scaler.pkl")
        svr_model = joblib.load("../models/svr_model.pkl")
        svm_model = joblib.load("../models/svm_model.pkl")
    except FileNotFoundError:
        print("Error: File model tidak ditemukan. Pastikan Anda sudah menjalankan train.py!")
        return

    # 5. Transformasi skala data ujian agar sesuai dengan standar model
    X_test_scaled = scaler.transform(X_test)

    # ==========================================
    # EVALUASI SVM (KLASIFIKASI ARAH)
    # ==========================================
    print("\n" + "="*45)
    print("HASIL EVALUASI SVM (Prediksi Arah)")
    print("="*45)
    
    # Model menebak arah dari data ujian
    y_clf_pred = svm_model.predict(X_test_scaled)

    # zero_division=0 digunakan agar tidak error jika model kebetulan tidak pernah menebak 1 atau 0 sama sekali
    print(f"Accuracy  : {accuracy_score(y_clf_test, y_clf_pred):.4f}")
    print(f"Precision : {precision_score(y_clf_test, y_clf_pred, zero_division=0):.4f}")
    print(f"Recall    : {recall_score(y_clf_test, y_clf_pred, zero_division=0):.4f}")
    print(f"F1-Score  : {f1_score(y_clf_test, y_clf_pred, zero_division=0):.4f}")

    cm = confusion_matrix(y_clf_test, y_clf_pred)
    print("\nConfusion Matrix:")
    print(f"- True Negative  (Benar tebak Turun) : {cm[0][0]}")
    print(f"- False Positive (Salah tebak Naik)  : {cm[0][1]}")
    print(f"- False Negative (Salah tebak Turun) : {cm[1][0]}")
    print(f"- True Positive  (Benar tebak Naik)  : {cm[1][1]}")

    # ==========================================
    # EVALUASI SVR (REGRESI HARGA)
    # ==========================================
    print("\n" + "="*45)
    print("HASIL EVALUASI SVR (Prediksi Harga)")
    print("="*45)
    
    # Model menebak harga dari data ujian
    y_reg_pred = svr_model.predict(X_test_scaled)

    mae = mean_absolute_error(y_reg_test, y_reg_pred)
    rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))
    mape = mean_absolute_percentage_error(y_reg_test, y_reg_pred) * 100

    print(f"MAE  (Rata-rata meleset harga)       : Rp {mae:.2f}")
    print(f"RMSE (Penalti meleset ekstrem)       : Rp {rmse:.2f}")
    print(f"MAPE (Persentase meleset rata-rata)  : {mape:.2f}%")
    print("="*45)

if __name__ == "__main__":
    evaluate_models()