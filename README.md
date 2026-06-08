# Forza Vertikal - Street Racing with Computer Vision Control


## Identitas pria yang mengerjakan repo ini
- **Nama**: Rahmat Maulana Ansori
- **NRP**: 5024241011
- **Tugas**: Merestorasi foto Lena yang rusak oleh salt&pepper, low contrast, blur, dan gaussian noise menggunakan teknik pengolahan citra manual 

---


Game balapan arcade interaktif yang dibuat menggunakan Pygame, di mana pergerakan mobil dikendalikan sepenuhnya tanpa keyboard, melainkan menggunakan masking OpenCV berbasis deteksi warna kulit/objek coklat lewat kamera.

---

## Demo Game
Berikut adalah rekaman pendek mekanik gameplay dan visualisasi kontroler berbasis kamera:

![Demo Game](demo-game.mp4)

---

## 🛠️ Fitur Utama
* **CV-Based Virtual Joystick:** Kontrol pergerakan mobil menggunakan zona WASD virtual pada tangkapan kamera.
* **Dual-Window Debugging:** Menampilkan visualisasi pelacakan objek asli ber-zona sekaligus hasil masking hitam-putih dalam satu jendela OpenCV yang ringkas.
* **Anti-Tumpuk Spawn Logic:** Algoritma cerdas yang mendeteksi jarak antar mobil di jalur yang sama agar mobil raksasa tidak saling tumpang tindih saat muncul.
* **Custom Pixel-Perfect Hitbox:** Menggunakan fitur *inflation* Pygame untuk menyusutkan bounding box gambar PNG asli agar deteksi tabrakan lebih adil dan akurat.

---

## 📂 Struktur Direktori
```text
.
├── assets/
│   ├── car1.png        # Mobil Utama (Player)
│   ├── car2.png        # Mobil Rintangan 1
│   ├── car3.png        # Mobil Rintangan 2
│   ├── car4.png        # Mobil Rintangan 3
│   ├── car5.png        # Mobil Rintangan 4
│   ├── car6.png        # Mobil Rintangan 5
│   └── jalanan.png     # Gambar Latar Belakang Jalan Raya
├── demo-game.mp4       # Video Demo Gameplay
├── README.md           # Dokumentasi Proyek
└── src/
    ├── carimask.py     # Script Eksperimen Kalibrasi Warna
    ├── coba.py         # Script Uji Coba Komponen
    ├── game.py         # SCRIPT UTAMA GAME (Pygame + OpenCV)
    ├── input.py        # Logika Pemrosesan Input
    └── obj_det.py      # Prototipe Deteksi Objek Awal