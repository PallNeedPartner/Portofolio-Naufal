# AGENTS.md

Instruksi untuk AI coding agent (Claude Code, Cursor, dll.) yang mengedit
project portofolio ini.

## Baca dulu

Sebelum mengubah apa pun di `index.html`, baca `DESIGN.md`. Semua keputusan
warna, font, dan layout di file itu **mengikat** — jangan diganti kecuali
user secara eksplisit minta ganti tema.

## Struktur project

```
portfolio/
├── index.html      # satu file, semua CSS & JS inline (tidak ada build step)
├── DESIGN.md        # sistem desain (warna, font, komponen signature)
├── AGENTS.md         # file ini
└── assets/
    ├── profile.jpg              # foto asli — ganti file ini, JANGAN rename
    └── profile-placeholder.svg  # fallback kalau profile.jpg belum ada
```

Ini bukan proyek React/build tool. Jangan tambah `package.json`, bundler, atau
framework kecuali diminta — tujuannya tetap 1 file HTML yang bisa langsung
dibuka di browser atau di-hosting statis (GitHub Pages, Netlify, dsb).

## Aturan saat menambah konten

- **Project baru**: tambah satu `.unit` di dalam `.rack` (section
  `#projects`), ikuti pola yang sudah ada (`unit-tag`, `status-chip`, `h3`,
  `p`, `.stack`, opsional `.unit-links`). Status chip cuma dua varian:
  `deployed` (masih online/bisa diakses publik) atau `completed` (selesai,
  tidak ada link publik).
- **Skill baru**: tambah satu `.port` di section `#skills`, ikuti pola
  `jack` + `name` + `sub`.
- **Jangan** menambah section baru dengan gaya visual yang beda sendiri
  (mis. card rounded besar + gradient) — semua section harus terasa satu
  keluarga dengan yang lain.

## Smooth scroll (Lenis)

Lenis di-load lewat CDN jsDelivr di baris terakhir sebelum `</body>`. Kalau
versi di CDN berubah/rusak:

```html
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.14/dist/lenis.min.js"></script>
```

cek versi terbaru di https://github.com/darkroomengineering/lenis dan ganti
angka versinya saja. Inisialisasi tetap:

```js
const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
function raf(time){ lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);
```

Jangan tambah library smooth-scroll lain (GSAP ScrollSmoother, Locomotive,
dll.) di atas Lenis — cukup satu.

## Sebelum commit/selesai

1. Buka `index.html` di browser, scroll dari atas ke bawah — pastikan tidak
   ada elemen yang "meloncat" atau reveal yang tidak muncul.
2. Cek di lebar layar ~375px (mobile) — nav links disembunyikan by design,
   tapi konten lain harus tetap rapi satu kolom.
3. Kalau menambah animasi baru, tes dengan `prefers-reduced-motion: reduce`
   aktif (DevTools → Rendering → Emulate CSS media) — animasi tambahan itu
   harus ikut nonaktif.
