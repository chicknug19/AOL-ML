import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

def train_models():
    filepath = "../dataset/LQ45_Clean.csv"
    print(f"Membaca data dari {filepath}...")
    df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)

    # Menghapus 'volume' sesuai keputusan tim
    features = ['open', 'high', 'low', 'close', 
                'EMA_21', 'EMA_99', 'EMA_200', 'RSI_14', 'Stoch_K',
                'MACD', 'Signal_Line', 'Upper_BB', 'Lower_BB', 'Daily_Return']
    
    X = df[features]
    y_clf = df['Target_Direction']    # Hanya menggunakan target arah (klasifikasi)

    # Membelah data tanpa melibatkan y_reg lagi
    X_train, X_test, y_clf_train, y_clf_test = train_test_split(
        X, y_clf, test_size=0.2, shuffle=False
    )

    print("Menormalkan skala data (Scaling)...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    print("\nMencari parameter terbaik untuk SVM (Hyperparameter Tuning)...")
    print("Proses ini akan memakan waktu sedikit lebih lama...")
    
    # GridSearch mencoba kombinasi C dan Gamma secara otomatis
    param_grid = {
        'C': [0.1, 1, 10, 100, 1000],
        'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
        'kernel': ['rbf']
    }
    
    svm_grid = GridSearchCV(
        SVC(probability=True, class_weight='balanced'), 
        param_grid, 
        refit=True, 
        cv=5, 
        verbose=1
    )
    
    svm_grid.fit(X_train_scaled, y_clf_train)
    
    print(f"-> Parameter SVM terbaik yang ditemukan: {svm_grid.best_params_}")
    svm_model = svm_grid.best_estimator_

    print("\nMenyimpan model ke dalam folder 'models'...")
    models_dir = "../models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    # Hanya menyimpan scaler dan svm_model
    joblib.dump(scaler, f"{models_dir}/scaler.pkl")
    joblib.dump(svm_model, f"{models_dir}/svm_model.pkl")

    print("[SUKSES] Model SVM berhasil dilatih dan disimpan!")

if __name__ == "__main__":
    train_models()