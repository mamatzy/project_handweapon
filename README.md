# Forza Vertikal - Street Racing with Computer Vision Control


## Identitas 
- **Nama**: Rahmat Maulana Ansori
- **NRP**: 5024241011

---

Game balapan arcade interaktif yang dibuat menggunakan **Pure OpenCV & NumPy** (tanpa dependensi Pygame). Pergerakan mobil dikendalikan sepenuhnya secara real-time tanpa keyboard, melainkan memanfaatkan kamera lewat deteksi warna kulit (HSV Masking) untuk kemudi WASD dan **Hand Gesture Recognition (Convexity Defects)** untuk mengaktifkan Boost Mode.

---

## Demo Game
Berikut adalah rekaman mekanik gameplay sebelum dan sesudah penambahan sistem pengenal gestur tangan:

### Versi 1: Kontrol Dasar (Tanpa Hand Recognition)
Kontrol pergerakan mobil murni menggunakan posisi koordinat tangan di dalam zona WASD.
https://github.com/user-attachments/assets/2ef562bb-561b-4b48-bfb1-c77fcd9b9f19

### Versi 2: Kontrol Lanjut (Dengan Hand Recognition & Boost)
Penambahan fitur deteksi kepalan tangan untuk memicu mode menyerang/boost.
https://github.com/user-attachments/assets/e3edd2f6-a58e-4ade-b0f0-29aa54955c26

---

## Fitur Utama

* **Pure OpenCV Engine:** Seluruh sistem *rendering* grafis, pergerakan *scrolling background* jalanan, animasi mobil, dan manajemen *game loop* dibuat murni menggunakan matriks OpenCV dan NumPy tanpa framework game eksternal.
* **CV-Based Virtual Joystick:** Sistem kontrol intuitif yang memetakan pusat massa tangan ke dalam zona virtual (W, A, S, D) pada *feed* kamera.
* **Hand Gesture Boost Mode (Anti-Flicker):** Mekanik spesial di mana pemain dapat mengepalkan tangan (*fist*) untuk mengaktifkan **Boost Mode selama 3 detik**. Selama mode ini aktif, mobil pemain dapat menabrak hancur rintangan dan mendapatkan bonus skor (+20 poin). Dilengkapi dengan sistem **Cooldown selama 5 detik** yang stabil dan anti-flicker.
* **Dual-Window Debugging:** Menyediakan jendela debug *side-by-side* (kamera asli ber-zona dan hasil masking *binary layout*) untuk mempermudah kalibrasi ambang batas warna kulit (HSV).
* **Anti-Tumpuk Spawn Logic:** Algoritma pemunculan rintangan yang cerdas dengan memeriksa koordinat mobil di jalur (*lane*) yang sama untuk mencegah mobil musuh muncul saling bertumpukan.
* **Manual Bounding Box Collison:** Deteksi tabrakan antar objek (*hitbox*) yang dikalkulasi secara presisi lewat perbandingan irisan koordinat matriks piksel secara manual.

---

## Struktur Direktori

```text
.
├── assets/
│   ├── car1.png        # Mobil Utama (Player)
│   ├── car2.png        # Mobil Rintangan 1 (Rotated)
│   ├── car3.png        # Mobil Rintangan 2
│   ├── car4.png        # Mobil Rintangan 3
│   ├── car5.png        # Mobil Rintangan 4 (Rotated)
│   ├── car6.png        # Mobil Rintangan 5
│   └── jalanan.png     # Gambar Latar Belakang Jalan Raya
├── demo-game.mp4       # Video Demo Gameplay
├── README.md           # Dokumentasi Proyek
└── src/
    ├── carimask.py     # Script Eksperimen Kalibrasi Warna (HSV)
    ├── coba.py         # Script Uji Coba Komponen
    ├── game.py         # SCRIPT UTAMA GAME (Pure OpenCV + Gesture Recognition)
    ├── input.py        # Logika Pemrosesan Input Kamera
    └── obj_det.py      # Prototipe Deteksi Objek Awal
