import os
import datetime
import cv2


def log_event(message: str, log_path: str = "logs/events.log") -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] - {message}"
    print(log_entry)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


class MotionDetector:
    def __init__(
        self,
        threshold: int = 50,
        default_min_area: int = 500,
        window_name: str = "Hareket Algilama Sistemi",
        log_path: str = "logs/events.log",
    ):
        self.window_name = window_name
        self.log_path = log_path
        self.motion_active = False

        # Arka plan cikarici (CLI'dan gelen --threshold degerini kullanir)
        self.back_sub = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=threshold,
            detectShadows=True,
        )

        # Kullanici arayuzu ve canli hassasiyet kaydiricisi
        initial_area = min(max(0, default_min_area), 10000)
        cv2.namedWindow(self.window_name)
        cv2.createTrackbar(
            "Hassasiyet (Min Alan)",
            self.window_name,
            initial_area,
            10000,
            lambda x: None,
        )

    def process(self, frame):
        # Arayuzden guncel hassasiyet degerini al
        min_area = cv2.getTrackbarPos("Hassasiyet (Min Alan)", self.window_name)

        # Hareket algilama maskesi olustur ve gurultuyu temizle
        fg_mask = self.back_sub.apply(frame)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)

        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        current_frame_motion = False

        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue

            current_frame_motion = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if current_frame_motion:
            # main.py icindeki (10, 30) sure/cozunurluk yazisiyla cakismamasi icin (10, 65)
            cv2.putText(
                frame,
                "Hareket Algilandi!",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        # Durum degisikligini logla (Spam'i onlemek icin sadece baslangic/bitiste yazar)
        if current_frame_motion and not self.motion_active:
            log_event("Hareket tespit edildi.", self.log_path)
            self.motion_active = True
        elif not current_frame_motion and self.motion_active:
            log_event("Hareket sona erdi.", self.log_path)
            self.motion_active = False

        return frame, fg_mask
