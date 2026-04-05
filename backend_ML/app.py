from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Mengizinkan frontend React untuk mengakses API ini
CORS(app)

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # 1. Menangkap data JSON yang dikirim dari React
        data = request.json
        
        # Ekstrak data harga dan volume
        open_price = float(data.get('open', 0))
        high_price = float(data.get('high', 0))
        low_price = float(data.get('low', 0))
        close_price = float(data.get('close', 0))
        volume = float(data.get('volume', 0))

        # ==========================================
        # 2. AREA INTEGRASI MACHINE LEARNING (SVM & SVR)
        # Nanti Anda akan memuat model .pkl di sini (misal: joblib.load('model_svm.pkl'))
        # ==========================================
        
        # Untuk sementara, kita buat logika simulasi agar API bisa dites nyala
        simulated_direction = "Naik (Up)" if close_price > open_price else "Turun (Down)"
        simulated_next_price = close_price * 1.015 if simulated_direction == "Naik (Up)" else close_price * 0.985
        
        # 3. Mengembalikan hasil prediksi ke React dalam format JSON
        return jsonify({
            'status': 'success',
            'prediction': {
                'direction': simulated_direction,
                'predictedPrice': f"{simulated_next_price:.2f}",
                'probability': '85.5%' # Ini juga nanti diganti dengan hasil probabilitas model (predict_proba)
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    # Server berjalan di port 5000 dengan mode debug aktif
    app.run(debug=True, port=5000)