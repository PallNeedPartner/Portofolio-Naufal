# DESIGN.md — Sistem Desain Portofolio Naufal

Dokumen ini nyatet keputusan desain biar kalau nanti diedit lagi (oleh Naufal
sendiri atau oleh AI/agent lain), style-nya tetap konsisten dan **tidak balik
ke tampilan "AI generik"**.

## Konsep

Tema: **ruang server / patch panel jaringan** — bukan landing page SaaS.
Setiap elemen struktural (port, rack unit, id card, terminal) literally
merepresentasikan sesuatu yang nyata di dunia IT support/networking, bukan
sekadar dekorasi.

Kenapa ini penting: kalau kembali ke "background gelap + 1 warna cyan terang
+ kartu rounded generik", itu persis pola default yang biasa dihasilkan AI
(gampang dikenali reviewer/dosen/HR sebagai template AI).

## Token warna

| Token | Hex | Peran |
|---|---|---|
| `--bg` | `#14100c` | Background utama (near-black **hangat**, bukan navy) |
| `--bg-panel` | `#1c1712` | Panel/card |
| `--bg-panel-2` | `#211b15` | Panel level 2 (nested, terminal bar) |
| `--ink` | `#f2ede2` | Teks utama (ivory, bukan putih murni) |
| `--ink-dim` | `#b8ae9e` | Teks sekunder |
| `--ink-faint` | `#7a7266` | Label/metadata |
| `--amber` | `#f2a93b` | Aksen utama — warna "status LED aktif" |
| `--teal` | `#5fa89f` | Aksen kedua — dipakai biar tidak cuma 1 warna terang |
| `--led` | `#6bcb77` | Indikator "online/deployed" |
| `--line` | `#372f26` | Border/hairline |

**Aturan:** jangan ganti `--amber` jadi cyan/sky-blue (`#38bdf8` dkk) atau
`--bg` jadi navy/slate (`#0f172a` dkk) — itu kombinasi default yang mau
dihindari.

## Tipografi

- **IBM Plex Mono** — untuk heading, label, angka, elemen "teknis" (terminal,
  port, tag rack). Ini yang bikin nuansa "system/CLI".
- **IBM Plex Sans** — untuk body text, supaya tetap enak dibaca panjang.

Jangan ganti ke Poppins/Inter generik + gradient text — itu yang dipakai versi
lama dan yang bikin kesan template.

## Layout / elemen signature

1. **Terminal boot sequence** di hero — satu-satunya tempat animasi "ramai"
   (typewriter). Jangan tambah animasi serupa di section lain, biar efeknya
   tetap terasa spesial.
2. **ID/Access Card** untuk foto profil — bukan foto bulat polos dengan ring
   gradient. Placeholder ada di `assets/profile-placeholder.svg`; ganti
   `assets/profile.jpg` dengan foto asli (rasio 1:1, minimal 500x500px).
3. **Patch panel ports** di section Skills — nomor/label port itu literal
   (representasi port jaringan), bukan numbering dekoratif 01/02/03 yang
   dipaksakan.
4. **Rack units** di section Projects — setiap project = 1 unit rack dengan
   status chip (`deployed` / `completed`).
5. **Ticket panel** di Contact — grid info kontak gaya "tiket support".

## Motion

- Smooth scroll pakai **Lenis** (lihat `AGENTS.md` untuk cara pasang ulang
  kalau CDN berubah).
- Scroll-reveal pelan (`IntersectionObserver` + fade/slide 28px) — dipakai di
  semua section secara konsisten, tidak berlebihan.
- Semua animasi menghormati `prefers-reduced-motion`.

## Yang harus dihindari saat mengedit

- Background krem hangat + font serif kontras + aksen terracotta.
- Background gelap + satu aksen hijau-neon/vermillion tunggal.
- Layout broadsheet dengan garis tipis dan zero border-radius di semua tempat.
- Numbered marker (01/02/03) dekoratif tanpa makna urutan yang nyata.
- Card `border-radius` besar (16px+) dengan bayangan lembut generik ala
  dashboard SaaS — pertahankan radius kecil (3–8px) sesuai tema hardware.
