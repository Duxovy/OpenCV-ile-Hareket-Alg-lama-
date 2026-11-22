import cv2
import argparse
import datetime
import os

def parse_args():
    parser = argparse.ArgumentParser(description="OpenCV Hareket Algılama Sistemi")
    parser.add_argument("--input", default="0", help="Kamera ID'si (örneğin 0) veya video dosya yolu (örneğin video.mp4)")
    parser.add_argument("--width", type=int, default=640, help="Çözünürlük genişliği (Genişlik)")
    parser.add_argument("--height", type=int, default=480, help="Çözünürlük yüksekliği (Yükseklik)")
    return parser.parse_args()

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] - {message}"
    print(log_entry)
    with open("events_log.txt", "a") as f:
        f.write(log_entry + "\n")

def main():
    args = parse_args()
    
    # Girdi tipini belirle (Kamera ID'si mi yoksa dosya mı?)
    if args.input.isdigit():
        video_source = int(args.input)
    else:
        video_source = args.input

    cap = cv2.VideoCapture(video_source)
    
    # Hata Senaryosu: Kamera/Video açılamazsa toparlanma
    if not cap.isOpened():
        log_event(f"HATA: '{video_source}' kaynağına erişilemedi veya dosya bulunamadı.")
        print("Sistem güvenli bir şekilde kapatılıyor. Lütfen bağlantıları kontrol edin.")
        return

    # Çözünürlük ayarları
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    # Arka plan çıkarıcı (Hareketi tespit etmek için)
    back_sub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

    # Kullanıcı Arayüzü ve Hassasiyet Ayarı
    window_name = "Hareket Algilama Sistemi"
    cv2.namedWindow(window_name)
    
    # Kullanıcı tarafından değiştirilebilen hassasiyet (Alan büyüklüğü eşiği)
    cv2.createTrackbar("Hassasiyet (Min Alan)", window_name, 1000, 10000, lambda x: None)

    log_event(f"Sistem başlatıldı. Kaynak: {video_source}, Çözünürlük: {args.width}x{args.height}")
    
    motion_active = False

    while True:
        ret, frame = cap.read()
        if not ret:
            log_event("UYARI: Video akışı bitti veya kesildi.")
            break

        # Arayüzden güncel hassasiyet değerini al
        min_area = cv2.getTrackbarPos("Hassasiyet (Min Alan)", window_name)
        
        # Hareket algılama maskesi oluştur
        fg_mask = back_sub.apply(frame)
        
        # Gürültüyü azaltmak için maskeyi temizle
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        current_frame_motion = False

        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue # Hassasiyet eşiğinin altındaki küçük hareketleri yoksay
            
            current_frame_motion = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Hareket Algilandi!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Durum değişikliğini logla (Spam'i önlemek için sadece hareket başladığında/bittiğinde log atar)
        if current_frame_motion and not motion_active:
            log_event("Hareket tespit edildi.")
            motion_active = True
        elif not current_frame_motion and motion_active:
            log_event("Hareket sona erdi.")
            motion_active = False

        cv2.imshow(window_name, frame)
        cv2.imshow("Maske (Hata Ayiklama)", fg_mask)

        # 'q' tuşu ile güvenli çıkış (Toparlanma / Geri yükleme senaryosu)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            log_event("Kullanıcı tarafından çıkış yapıldı.")
            break

    cap.release()
    cv2.destroyAllWindows()
    log_event("Sistem güvenli bir şekilde kapatıldı.")

if __name__ == "__main__":
    main()
