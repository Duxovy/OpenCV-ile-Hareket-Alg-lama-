# OpenCV ile Gerçek Zamanlı Video Akışı ve Hareket Algılama Sistemi

Linux ortamında V4L2 (Video4Linux2) altyapısını kullanarak USB kameralardan veya yerel video dosyalarından gerçek zamanlı görüntü okuyan, arka plan çıkarımı (MOG2) ile hareket algılayan, olayları zaman damgasıyla kaydeden ve donanım/kaynak hatalarını kontrollü çıkış kodlarıyla yöneten modüler Python uygulaması.

---

## Proje Dizin Yapısı

```text
OpenCV-ile-Hareket-Alg-lama-/
├── main.py                  # Uygulama giriş noktası, CLI argümanları ve ana çalışma döngüsü
├── setup.sh                 # Dağıtım bağımsız kurulum, sanal ortam ve donanım izin betiği
├── requirements.txt         # Python bağımlılık listesi (opencv-python, numpy)
├── .gitignore               # Sanal ortam (.venv) ve geçici dosyalar için Git hariç tutma kuralları
├── src/
│   ├── video_source.py      # V4L2 kamera/video soyutlama, ölçekleme ve VideoSourceError yönetimi
│   └── motion_detector.py   # MOG2 hareket algılama, Trackbar hassasiyet ayarı ve olay loglama
├── logs/
│   └── events.log           # Durum değişimlerinin zaman damgalı kayıt dosyası (çalışma anında oluşur)
└── docs/                    # V4L2 analizleri, hata senaryosu ekran görüntüleri ve test raporları
