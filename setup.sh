#!/usr/bin/env bash
set -e
mkdir -p logs docs src

if command -v pacman >/dev/null 2>&1; then
	sudo pacman -S --needed --noconfirm python python-pip v4l-utils
elif command -v dnf >/dev/null 2>&1; then
	sudo dnf install -y python3 python3-pip v4l-utils
elif command -v apt-get >/dev/null 2>&1; then
	sudo apt-get update
	sudo apt-get install -y python3 python3-pip python3-venv v4l-utils libgl1 libglib2.0-0
elif [ -f /etc/NIXOS ]; then
	mkdir -p logs docs src
	if ! groups "$USER" | grep -qw "video"; then
        	echo -e "\033[1;33m[UYARI]\033[0m Kamera erisimi icin configuration.nix icinde extraGroups'a 'video' eklemelisiniz."
   	fi
	if ls /dev/video* >/dev/null 2>&1; then
       		nix-shell -p v4l-utils --run "v4l2-ctl --list-devices"
   	else
		echo -e "\033[1;33m[UYARI]\033[0m Fiziksel kamera bulunamadi, uygulamayi video dosyasi ile calistirabilirsiniz."
    	fi
	nix-shell -p python3 python3Packages.opencv4 python3Packages.numpy v4l-utils --run "python3 -c 'import cv2, numpy'"
	echo "[BILGI] Kurulum tamamlandi. Uygulamayi baslatmak icin su komutu calistirin:"
   	echo "nix-shell -p python3 python3Packages.opencv4 python3Packages.numpy v4l-utils --run 'python3 main.py'"
   	exit 0
fi

if ! groups "$USER" | grep -qw "video"; then
	sudo usermod -aG video "$USER"
	echo "$USER , 'video' grubuna eklendi."
fi

if ls /dev/video* >/dev/null 2>&1; then
	v4l2-ctl --list-devices
else
	echo -e "\033[1;33m [UYARI] :\033[0m Fiziksel kamera bulunamadı, uygulamayı video dosyası ile çalıştırabilirsiniz. "
fi

if [ ! -d ".venv" ]; then
	python3 -m venv .venv;
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "[BILGI] Kurulum tamamlandi. Uygulamayi baslatmak icin su komutu calistirin:"
echo "source .venv/bin/activate"
