import pandas as pd
import numpy as np

def clean_indonesian_format(val):
    """Fungsi untuk membersihkan angka dengan format desimal Indonesia"""
    if pd.isna(val) or str(val).strip() == '-':
        return np.nan
    
    val = str(val).strip()
    val = val.replace('%', '')
    
    multiplier = 1
    if 'B' in val:
        val = val.replace('B', '')
        multiplier = 1_000_000_000
    elif 'M' in val:
        val = val.replace('M', '')
        multiplier = 1_000_000
    elif 'K' in val:
        val = val.replace('K', '')
        multiplier = 1_000
        
    val = val.replace('.', '').replace(',', '.')
    return float(val) * multiplier

def load_and_clean_data(filepath):
    """Membaca CSV dari Investing.com dan membersihkan formatnya"""
    df = pd.read_csv(filepath)
    
    df.rename(columns={
        'Tanggal': 'timestamp',
        'Terakhir': 'close',
        'Pembukaan': 'open',
        'Tertinggi': 'high',
        'Terendah': 'low',
        'Vol.': 'volume',
        'Perubahan%': 'change_pct'
    }, inplace=True)
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y')
    df.sort_values('timestamp', inplace=True)
    df.set_index('timestamp', inplace=True)
    
    for col in ['close', 'open', 'high', 'low', 'volume', 'change_pct']:
        if col in df.columns:
            df[col] = df[col].apply(clean_indonesian_format)
    
    df['volume'] = df['volume'].replace(0, np.nan)
    
    # MEMPERBAIKI WARNING: Menggunakan df.ffill() menggantikan fillna(method='ffill')
    df.ffill(inplace=True) 
    
    return df

def add_technical_indicators(df):
    """Menambahkan fitur analisis teknikal untuk model ML"""
    # 1. EMA
    df['EMA_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['EMA_99'] = df['close'].ewm(span=99, adjust=False).mean()
    df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
    
    # 2. RSI 14
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 3. Stochastic
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['Stoch_K'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    
    # ==========================================
    # FITUR BARU UNTUK MENDONGKRAK AKURASI SVM
    # ==========================================
    # 4. MACD & Signal Line
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # 5. Bollinger Bands (20-hari)
    sma_20 = df['close'].rolling(window=20).mean()
    std_20 = df['close'].rolling(window=20).std()
    df['Upper_BB'] = sma_20 + (std_20 * 2)
    df['Lower_BB'] = sma_20 - (std_20 * 2)
    
    # 6. Daily Return (Momentum harga harian)
    df['Daily_Return'] = df['close'].pct_change()
    
    # Target
    df['Target_Price'] = df['close'].shift(-1)
    df['Target_Direction'] = np.where(df['Target_Price'] > df['close'], 1, 0)
    
    df.dropna(inplace=True)
    return df

if __name__ == "__main__":
    input_filepath = "backend_ML/dataset/LQ45_Historical.csv" 
    output_filepath = "backend_ML/dataset/LQ45_Clean.csv"  # File baru hasil pembersihan
    
    try:
        print("Memproses data LQ45 dari Investing.com...")
        clean_df = load_and_clean_data(input_filepath)
        final_df = add_technical_indicators(clean_df)
        
        # MENYIMPAN HASIL PREPROCESSING KE FILE BARU
        final_df.to_csv(output_filepath)
        print(f"\n[SUKSES] Data bersih berhasil disimpan ke: {output_filepath}")
        
        print("\n=== VERIFIKASI FORMAT DATA ===")
        print(final_df[['close', 'volume', 'EMA_21', 'Target_Direction', 'Target_Price']].tail())
        
    except Exception as e:
        print(f"Terjadi error: {e}")