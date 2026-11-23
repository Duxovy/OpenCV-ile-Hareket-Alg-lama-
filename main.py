import os
import sys
import time
import argparse

if sys.platform.startswith("linux") and "WAYLAND_DISPLAY" in os.environ:
	os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
import cv2
from src.video_source import VideoSource, VideoSourceError
from src.motion_detector import MotionDetector, log_event

def parse_resolution(value: str) -> tuple[int, int]:
	parts = value.lower().split("x")
	if len(parts) != 2:
		raise argparse.ArgumentTypeError(f"Gecersiz cozunurluk formati: '{value}'. Ornek kullanim: 640x480 veya 1280x720")
	try:
		width, height = int(parts[0]), int(parts[1])
	except ValueError:
		raise argparse.ArgumentTypeError(f"Cozunurluk degeri tam sayi olmalidir: '{value}'")
	if width <= 0 or height <= 0:
		raise argparse.ArgumentTypeError(f"Genislik ve yukseklik 0'dan buyuk olmalidir: '{value}'")
	return (width, height)
def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Gercek Zamanli Video Akisi ve Hareket Algilama Sistemi")
	parser.add_argument("-s", "--source", type=str, default="0", help="Kamera indeksi (orn: 0, 1) veya video dosya yolu (varsayilan: '0')")
	parser.add_argument("-r", "--resolution", type=parse_resolution, default="640x480", help="Hedef video cozunurlugu GENISLIKxYUKSEKLIK formatinda (varsayilan: 640x480)")
	parser.add_argument("-t", "--threshold", type=int, default=25, help="Hareket algilama piksel farki esik degeri (varsayilan: 25)")
	parser.add_argument("-a", "--min-area", type=int, default=500, help="Algilanacak minimum hareket kontur piksel cinsinden (varsayilan: 500)")
	return parser.parse_args()
def main():
	args = parse_args()
	if args.source.isdigit():
		source = int(args.source)
	else:
		source = args.source
	
	width, height = args.resolution
	try:
		with VideoSource(source=source, target_resolution=args.resolution) as video_src:
			detector = MotionDetector(threshold=args.threshold, default_min_area=args.min_area)
			log_event(f"Sistem baslatildi. Kaynak: {source}, Cozunurluk: {width}x{height}")
			while True:
				t_start = time.perf_counter()
				ret, frame, timestamp = video_src.read_frame()
				if not ret:
					if video_src.is_camera:
						sys.stderr.write(f"[HATA] Kamera (index={source}) baglantisi koptu.\n")
						sys.exit(2)
					else:
						print("[BILGI] Video dosyasinin sonuna ulasildi.")
						break
				processed_frame, fg_mask = detector.process(frame)
				elapsed_ms = (time.perf_counter() - t_start) * 1000
				overlay_text = f"Cozunurluk: {width}x{height} | Sure: {elapsed_ms:.2f} ms"
				cv2.putText(processed_frame, overlay_text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
				cv2.imshow(detector.window_name, processed_frame)
				cv2.imshow("Maske", fg_mask)
				if cv2.waitKey(1) & 0xFF == ord("q"):
					print("[BILGI] Kullanici cikis tusuna ('q') basti.")
					break
	except VideoSourceError as err:
		sys.stderr.write(f"[KRITIK HATA] Video kaynagi baslatilamadi: {err}\n")
		sys.exit(1)
	except KeyboardInterrupt:
		print("\n[BILGI] Program kullanici tarafindan (Ctrl+C) durduruldu.")
		sys.exit(0)
	finally:
		cv2.destroyAllWindows()
if __name__ == "__main__":
	main()
