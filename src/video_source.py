import os
import sys
import time
import cv2

class VideoSourceError(Exception): pass

class VideoSource:
	def __init__(self, source, target_resolution=(640, 480), target_fps=30):
		self.source = source
		self.target_resolution = target_resolution
		self.target_fps = target_fps
		self.is_camera = isinstance(self.source, int) and not isinstance(self.source, bool)
		self.need_software_resize = False
		self.cap = None
		self._validate_source()

	def _validate_source(self):
		if self.is_camera:
			self._validate_camera()
		elif isinstance(self.source, str):
			self._validate_file()
		else:
			raise VideoSourceError(f"Beklenmeyen veri: '{self.source}'")

	def _validate_camera(self):
		if sys.platform.startswith("linux"):
			device_path = f"/dev/video{self.source}"
			if not os.path.exists(device_path):
				raise VideoSourceError(f"Kamera bulunamadi: '{device_path}'")

	def _validate_file(self):
		if not os.path.exists(self.source):
			raise VideoSourceError(f"Video dosyasi bulunamadi: '{self.source}'")

		if not os.access(self.source, os.R_OK):
			raise VideoSourceError(f"Video dosyasi icin okuma izni yok: '{self.source}'")

	def open(self):
		if self.is_camera and sys.platform.startswith("linux"):
			self.cap = cv2.VideoCapture(self.source, cv2.CAP_V4L2)
		else:
			self.cap = cv2.VideoCapture(self.source)

		if not self.cap.isOpened():
			raise VideoSourceError(f"Kaynak acilamadi: '{self.source}'")

		if self.is_camera:
			fourcc = cv2.VideoWriter_fourcc(*"MJPG")
			self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[0])
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[1])
			self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

		ret, frame = self.cap.read()
		if not ret or frame is None:
			self.close()
			raise VideoSourceError(f"Kaynak acildi ama okunabilen kare yok: '{self.source}'")

		actual_height, actual_width = frame.shape[:2]
		if not self.is_camera:
			self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

		if (actual_width, actual_height) != self.target_resolution:
			self.need_software_resize = True
		else:
			self.need_software_resize = False

	def read_frame(self):
		if self.cap is None or not self.cap.isOpened():
			return False, None, time.time()

		ret, frame = self.cap.read()
		timestamp = time.time()
		if not ret or frame is None:
			if self.is_camera:
				print("[BİLGİ] Kamera bağlantısı koptu.")
			else:
				print("[BİLGİ] Video akışı sona erdi.")

			return False, None, timestamp
		if self.need_software_resize:
			frame = cv2.resize(frame, self.target_resolution, interpolation=cv2.INTER_AREA)

		return True, frame, timestamp

	def close(self):
		if self.cap is not None:
			self.cap.release()
			self.cap = None
	
	def __enter__(self):
		self.open()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()
		return False

