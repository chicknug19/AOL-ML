import { useState } from 'react'

function App() {
  const [formData, setFormData] = useState({
    open: '',
    high: '',
    low: '',
    close: '',
    volume: ''
  })
  
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData({ ...formData, [name]: value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // 1. Mengirim data ke backend Flask
      const response = await fetch('http://127.0.0.1:5000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      // 2. Menerima jawaban dari Flask
      const data = await response.json();

      // 3. Menampilkan hasil ke layar
      if (data.status === 'success') {
        setPrediction(data.prediction);
      } else {
        alert('Terjadi kesalahan dari server: ' + data.message);
      }
    } catch (error) {
      alert('Gagal terhubung ke server. Pastikan terminal Flask Anda sedang menyala!');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8 flex flex-col items-center font-sans">
      <div className="w-full max-w-4xl">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">LQ45 Index Predictor</h1>
        <p className="text-slate-500 mb-8">Masukkan data historis harian untuk memprediksi pergerakan indeks besok.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Bagian Form Input */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-semibold mb-4 text-slate-700">Data Input</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {['open', 'high', 'low', 'close', 'volume'].map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-slate-600 capitalize mb-1">
                    {field} Price {field === 'volume' ? '' : '(IDR)'}
                  </label>
                  <input
                    type="number"
                    step="any"
                    name={field}
                    value={formData[field]}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder={`Masukkan ${field}...`}
                  />
                </div>
              ))}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:bg-blue-300"
              >
                {loading ? 'Memproses Model...' : 'Jalankan Prediksi'}
              </button>
            </form>
          </div>

          {/* Bagian Hasil Prediksi */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-center">
            <h2 className="text-xl font-semibold mb-6 text-slate-700 text-center">Hasil Analisis Model</h2>
            
            {prediction ? (
              <div className="space-y-6">
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                  <p className="text-sm text-blue-600 font-semibold mb-1">Prediksi Arah (SVM)</p>
                  <p className={`text-2xl font-bold ${prediction.direction.includes('Naik') ? 'text-green-600' : 'text-red-600'}`}>
                    {prediction.direction}
                  </p>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-sm text-slate-500 font-semibold mb-1">Estimasi Harga Penutupan (SVR)</p>
                  <p className="text-2xl font-bold text-slate-800">{prediction.predictedPrice}</p>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-sm text-slate-500 font-semibold mb-1">Probabilitas Akurasi</p>
                  <p className="text-2xl font-bold text-slate-800">{prediction.probability}</p>
                </div>
              </div>
            ) : (
              <div className="text-center text-slate-400 py-12">
                <p>Belum ada data yang diproses.</p>
                <p className="text-sm">Silakan masukkan data dan klik tombol prediksi.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App