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
    e.preventDefault();
    setLoading(true);
    
    try {
      // Ubah bagian ini:
      const response = await fetch('https://chicknug19-aol_ml.hf.space/api/predict');
      const data = await response.json();

      if (data.status === 'success') {
        setPrediction(data); 
        // AJAIB: Baris ini akan otomatis mengisi form input di sebelah kiri!
        setFormData(data.market_data);
      } else {
        alert('Terjadi kesalahan di server: ' + data.message);
      }
    } catch (error) {
      alert('Gagal terhubung ke backend.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8 flex flex-col items-center font-sans">
      <div className="w-full max-w-4xl">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">LQ45 Index Predictor</h1>
        <p className="text-slate-500 mb-8">Tekan tombol prediksi untuk melihat proyeksi pergerakan arah indeks berdasarkan data terbaru.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Bagian Kiri: Form Input (Sekarang sebagai representasi data terupdate) */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-semibold mb-4 text-slate-700">Data Input Simulation</h2>
            <p className="text-xs text-slate-400 mb-4">*Catatan: Saat tombol diklik, backend otomatis mengambil baris pasar terupdate dari dataset bersih.</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              {['open', 'high', 'low', 'close'].map((field) => (
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
                    disabled={true} // Di-disabled karena backend sudah otomatis membaca file CSV
                    className="w-full px-4 py-2 border border-slate-200 bg-slate-50 text-slate-400 rounded-lg outline-none cursor-not-allowed"
                    placeholder="Otomatis ditarik dari database..."
                  />
                </div>
              ))}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:bg-blue-300"
              >
                {loading ? 'Memproses Model...' : '🔄 Predict Hari Ini'}
              </button>
            </form>
          </div>

          {/* Bagian Kanti: Tampilan Hasil Berdasarkan Mockup Baru */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-center">
            <h2 className="text-xl font-semibold mb-6 text-slate-700 text-center">Prediksi LQ45 Besok</h2>
            
            {prediction ? (
              <div className="space-y-6">
                {/* Kotak Utama Arah Pergerakan */}
                <div className={`p-6 rounded-xl border text-center ${
                  prediction.arah.includes('NAIK') 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-red-50 border-red-200'
                }`}>
                  <p className={`text-4xl font-black tracking-wide ${
                    prediction.arah.includes('NAIK') ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {prediction.arah}
                  </p>
                </div>

                {/* Info Metrik Keyakinan */}
                <div className="grid grid-cols-1 gap-3">
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex justify-between items-center">
                    <span className="text-sm text-slate-500 font-medium">Confidence Level</span>
                    <span className="text-lg font-bold text-slate-800">{prediction.confidence}</span>
                  </div>

                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex justify-between items-center">
                    <span className="text-sm text-slate-500 font-medium">Probabilitas Naik</span>
                    <span className="text-lg font-bold text-green-600">{prediction.prob_naik}</span>
                  </div>

                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex justify-between items-center">
                    <span className="text-sm text-slate-500 font-medium">Probabilitas Turun</span>
                    <span className="text-lg font-bold text-red-600">{prediction.prob_turun}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-slate-400 py-12">
                <p className="font-medium">Belum ada data yang diproses.</p>
                <p className="text-sm text-slate-400 mt-1">Silakan klik tombol di sebelah kiri untuk memanggil mesin kecerdasan buatan.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App