import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR, SVC

def train_models():
    filepath = "../dataset/LQ45_Clean.csv"
    print(f"Membaca data dari {filepath}...")
    df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)

    features = ['open', 'high', 'low', 'close', 'volume', 
                'EMA_21', 'EMA_99', 'EMA_200', 'RSI_14', 'Stoch_K',
                'MACD', 'Signal_Line', 'Upper_BB', 'Lower_BB', 'Daily_Return']
    
    X = df[features]
    y_reg = df['Target_Price']        
    y_clf = df['Target_Direction']    

    X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, shuffle=False
    )

    print("Menormalkan skala data (Scaling)...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    print("\nMelatih model SVR (Prediksi Harga)...")
    # SVR kita biarkan seperti sebelumnya karena hasilnya (MAPE 3.32%) sudah sangat bagus
    svr_model = SVR(kernel='rbf', C=100, gamma=0.1) 
    svr_model.fit(X_train_scaled, y_reg_train)

    print("\nMencari parameter terbaik untuk SVM (Hyperparameter Tuning)...")
    print("Proses ini akan memakan waktu sedikit lebih lama...")
    
    # GridSearch akan mencoba kombinasi C dan Gamma ini satu per satu
    param_grid = {
        'C': [0.1, 1, 10, 100, 1000],
        'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
        'kernel': ['rbf']
    }
    
    # class_weight='balanced' ditambahkan agar model lebih peka terhadap hari 'Naik'
    svm_grid = GridSearchCV(
        SVC(probability=True, class_weight='balanced'), 
        param_grid, 
        refit=True, 
        cv=5, # Cross-validation 5 kali lipat
        verbose=1
    )
    
    svm_grid.fit(X_train_scaled, y_clf_train)
    
    print(f"-> Parameter SVM terbaik yang ditemukan: {svm_grid.best_params_}")
    svm_model = svm_grid.best_estimator_ # Mengambil model yang sudah optimal

    print("\nMenyimpan model ke dalam folder 'models'...")
    models_dir = "../models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    joblib.dump(scaler, f"{models_dir}/scaler.pkl")
    joblib.dump(svr_model, f"{models_dir}/svr_model.pkl")
    joblib.dump(svm_model, f"{models_dir}/svm_model.pkl")

    print("[SUKSES] Semua model berhasil dilatih dan disimpan!")

if __name__ == "__main__":
    train_models()