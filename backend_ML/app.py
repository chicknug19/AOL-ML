import pandas as pd
import numpy as np
import joblib
import yfinance as yf
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

try:
    scaler = joblib.load('models/scaler.pkl')
    svm_model = joblib.load('models/svm_model.pkl')
    print("Model berhasil dimuat!")
except Exception as e:
    print(f"Error memuat model: {e}")

@app.route('/api/predict', methods=['POST', 'GET'])
def predict():
    try:
        # 1. Menarik Data Langsung dari Yahoo Finance (GRATIS)
        # ^JKLQ45 adalah kode ticker resmi untuk Indeks LQ45
        print("Mengunduh data LQ45 dari Yahoo Finance...")
        lq45 = yf.download('^JKLQ45', period='1y')
        
        if lq45.empty:
            return jsonify({'status': 'error', 'message': 'Gagal mengambil data dari Yahoo Finance'})

        # 2. Merapikan Kolom agar cocok dengan model kita
        df = pd.DataFrame()
        # Menggunakan .squeeze() agar aman dari perubahan versi yfinance terbaru
        df['open'] = lq45['Open'].squeeze()
        df['high'] = lq45['High'].squeeze()
        df['low'] = lq45['Low'].squeeze()
        df['close'] = lq45['Close'].squeeze()
        df['volume'] = lq45['Volume'].squeeze()

        # 3. Menghitung Indikator Teknikal (Dihitung On-The-Fly)
        df['EMA_21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['EMA_99'] = df['close'].ewm(span=99, adjust=False).mean()
        df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))
        
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['Stoch_K'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        df['Upper_BB'] = sma_20 + (std_20 * 2)
        df['Lower_BB'] = sma_20 - (std_20 * 2)
        
        df['Daily_Return'] = df['close'].pct_change()

        df.dropna(inplace=True)

        # 4. Ambil HANYA baris pasar paling terakhir (Hari Ini)
        latest_data = df.iloc[-1:]
        
        features = ['open', 'high', 'low', 'close', 'volume', 
                    'EMA_21', 'EMA_99', 'EMA_200', 'RSI_14', 'Stoch_K',
                    'MACD', 'Signal_Line', 'Upper_BB', 'Lower_BB', 'Daily_Return']
        
        X_latest = latest_data[features]
        X_scaled = scaler.transform(X_latest)
        
        # 5. Eksekusi Prediksi
        pred_class = svm_model.predict(X_scaled)[0] 
        probabilities = svm_model.predict_proba(X_scaled)[0]
        
        prob_turun = probabilities[0]
        prob_naik = probabilities[1]
        arah = "🟢 NAIK" if pred_class == 1 else "🔴 TURUN"
        confidence = max(prob_naik, prob_turun) * 100
        
        # 6. Kirim Prediksi SEKALIGUS Data Angka Hari Ini ke React
        return jsonify({
            'status': 'success',
            'arah': arah,
            'confidence': f"{confidence:.1f}%",
            'prob_naik': round(prob_naik, 3),
            'prob_turun': round(prob_turun, 3),
            'market_data': {
                'open': round(float(latest_data['open'].iloc[0]), 2),
                'high': round(float(latest_data['high'].iloc[0]), 2),
                'low': round(float(latest_data['low'].iloc[0]), 2),
                'close': round(float(latest_data['close'].iloc[0]), 2),
                'volume': int(latest_data['volume'].iloc[0])
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)