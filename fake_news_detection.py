"""
=============================================================
  FAKE NEWS DETECTION — NLP / Machine Learning Pipeline
  UAS Project · Sistem dan Teknologi Informasi
=============================================================
  Alur:
    1. Generate / load dataset
    2. Eksplorasi data (EDA)
    3. Preprocessing teks
    4. Feature extraction (TF-IDF)
    5. Training 3 model (LR, NB, RF)
    6. Evaluasi (Accuracy, Precision, Recall, F1, Confusion Matrix)
    7. Visualisasi & simpan semua grafik
    8. Demo prediksi berita baru
=============================================================
"""

import os, re, warnings, random
import numpy  as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from nltk.corpus   import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model            import LogisticRegression
from sklearn.naive_bayes             import MultinomialNB
from sklearn.ensemble                import RandomForestClassifier
from sklearn.model_selection         import train_test_split, learning_curve
from sklearn.metrics                 import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")
np.random.seed(42)
random.seed(42)

OUT = "/home/claude/output"
os.makedirs(OUT, exist_ok=True)

COLORS = {
    "fake"  : "#E24B4A",
    "real"  : "#639922",
    "blue"  : "#378ADD",
    "amber" : "#BA7517",
    "gray"  : "#888780",
    "bg"    : "#F8F8F7",
}
plt.rcParams.update({
    "figure.facecolor" : "white",
    "axes.facecolor"   : COLORS["bg"],
    "axes.spines.top"  : False,
    "axes.spines.right": False,
    "font.family"      : "DejaVu Sans",
    "axes.titlesize"   : 13,
    "axes.titleweight" : "bold",
    "axes.labelsize"   : 11,
})

# ─────────────────────────────────────────────
# 1. GENERATE SYNTHETIC DATASET
# ─────────────────────────────────────────────
print("\n[1/8] Membuat dataset sintetis...")

FAKE_TITLES = [
    "TERBONGKAR: Pemerintah sembunyikan obat kanker dari tanaman lokal",
    "Vaksin COVID mengandung chip microelectronic pengawas warga",
    "Konspirasi global: elit dunia kendalikan ekonomi Indonesia",
    "Ilmuwan NASA akui bumi datar, bukti disembunyikan",
    "Air minum kemasan mengandung zat kimia berbahaya pemicu tumor",
    "Presiden rahasia dijual pulau terluar ke asing tanpa sepengetahuan rakyat",
    "Dokter ungkap: 5G sebabkan kerusakan DNA permanen",
    "VIRAL: Artis terkenal positif gunakan narkoba jenis baru",
    "Bank asing ambil alih semua aset Indonesia secara diam-diam",
    "Alien bantu Indonesia bangun infrastruktur rahasia di Kalimantan",
]

REAL_TITLES = [
    "Bank Indonesia naikkan suku bunga acuan 25 basis poin pada rapat Oktober",
    "WHO umumkan pedoman terbaru penanganan penyakit infeksi saluran napas",
    "Pertumbuhan ekonomi Indonesia Q3 2024 capai 5,1 persen menurut BPS",
    "KPK tetapkan tiga tersangka kasus korupsi pengadaan alat kesehatan",
    "Penelitian LIPI ungkap potensi biodiversitas laut Indonesia timur",
    "Pemerintah alokasikan Rp 48 triliun untuk program beasiswa pendidikan 2025",
    "BPOM setujui vaksin dengue produksi dalam negeri setelah uji klinis tiga fase",
    "Kementerian ESDM rilis roadmap transisi energi terbarukan hingga 2060",
    "Indonesia raih peringkat ke-32 indeks kemudahan berusaha World Bank 2024",
    "Tim peneliti UI kembangkan material baterai dari limbah kelapa sawit",
]

FAKE_BODIES = [
    "Sumber terpercaya mengungkapkan bahwa selama ini {topic} telah disembunyikan dari publik. "
    "Tidak ada lembaga resmi yang berani membenarkan hal ini karena tekanan dari pihak-pihak berkepentingan. "
    "Ribuan orang sudah merasakan dampaknya namun pemerintah tutup mata. "
    "Bagikan sebelum dihapus! Ini fakta yang mereka tidak mau kamu tahu.",

    "BREAKING NEWS! Para ahli independen akhirnya membuktikan bahwa {topic} adalah konspirasi nyata. "
    "Media mainstream memblokir informasi ini agar tidak tersebar luas. "
    "Ilmuwan yang berani bicara diancam dan dibungkam. Sebarkan sebelum terlambat!",

    "Investigasi eksklusif kami menemukan bukti sahih bahwa {topic} merupakan rekayasa sistematis. "
    "Dokumen bocor menunjukkan keterlibatan pihak asing dalam mengendalikan situasi ini. "
    "Rakyat harus tahu kebenaran ini! Share ke semua kontak kamu.",
]

REAL_BODIES = [
    "Berdasarkan data resmi yang dirilis oleh lembaga berwenang, {topic} telah melalui serangkaian "
    "proses verifikasi yang ketat. Para ahli dari berbagai institusi terkemuka menegaskan validitas "
    "temuan ini berdasarkan metodologi penelitian yang terstandarisasi secara internasional.",

    "Menurut laporan resmi yang dipublikasikan dalam jurnal ilmiah terindeks, {topic} "
    "didasarkan pada analisis data empiris dari 12 negara selama periode 2020-2024. "
    "Komite independen telah memverifikasi seluruh temuan sebelum dirilis ke publik.",

    "Juru bicara resmi lembaga terkait menyatakan bahwa {topic} merupakan hasil dari "
    "proses perencanaan jangka panjang yang melibatkan berbagai pemangku kepentingan. "
    "Data menunjukkan dampak positif yang signifikan berdasarkan indikator terukur.",
]

TOPICS_FAKE = [
    "vaksin berbahaya", "chip pengawas", "obat kanker disembunyikan",
    "konspirasi elit global", "bumi datar", "5G berbahaya",
    "pemerintah korup", "alien di Indonesia", "zat kimia berbahaya", "pulau dijual",
]
TOPICS_REAL = [
    "kebijakan moneter terbaru", "penelitian ilmiah terkini", "program pemerintah resmi",
    "data ekonomi nasional", "keputusan lembaga internasional", "hasil uji klinis",
    "laporan kinerja instansi", "roadmap pembangunan", "temuan riset universitas", "regulasi baru",
]

def make_samples(titles, bodies, topics, label, n=2100):
    rows = []
    for i in range(n):
        t  = titles[i % len(titles)]
        b  = random.choice(bodies).format(topic=random.choice(topics))
        noise = " ".join(random.choice(titles + topics.copy()).split()[:random.randint(3,8)])
        rows.append({"title": t, "text": b + " " + noise, "label": label})
    return rows

data = make_samples(FAKE_TITLES, FAKE_BODIES, TOPICS_FAKE, "FAKE") + \
       make_samples(REAL_TITLES, REAL_BODIES, TOPICS_REAL, "REAL")
df = pd.DataFrame(data).sample(frac=1, random_state=42).reset_index(drop=True)
df["content"] = df["title"] + " " + df["text"]

print(f"   ✓ Total sampel: {len(df):,}")
print(f"   ✓ FAKE: {(df.label=='FAKE').sum():,}  |  REAL: {(df.label=='REAL').sum():,}")

# ─────────────────────────────────────────────
# 2. EDA
# ─────────────────────────────────────────────
print("\n[2/8] Eksplorasi data (EDA)...")

df["text_len"]   = df["content"].str.len()
df["word_count"] = df["content"].str.split().str.len()

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
fig.suptitle("Eksplorasi Data (EDA)", fontsize=14, fontweight="bold", y=1.02)

# Distribusi label
counts = df["label"].value_counts()
bars = axes[0].bar(counts.index, counts.values,
                   color=[COLORS["fake"], COLORS["real"]], width=0.5, edgecolor="white")
for bar, val in zip(bars, counts.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                 f"{val:,}", ha="center", va="bottom", fontsize=11, fontweight="bold")
axes[0].set_title("Distribusi Label")
axes[0].set_ylabel("Jumlah artikel")
axes[0].set_facecolor(COLORS["bg"])

# Distribusi panjang teks
for lbl, col in [("FAKE", COLORS["fake"]), ("REAL", COLORS["real"])]:
    subset = df[df.label == lbl]["text_len"]
    axes[1].hist(subset, bins=30, color=col, alpha=0.65, label=lbl, edgecolor="white")
axes[1].set_title("Distribusi Panjang Teks")
axes[1].set_xlabel("Jumlah karakter")
axes[1].set_ylabel("Frekuensi")
axes[1].legend()

# Distribusi jumlah kata
for lbl, col in [("FAKE", COLORS["fake"]), ("REAL", COLORS["real"])]:
    subset = df[df.label == lbl]["word_count"]
    axes[2].hist(subset, bins=30, color=col, alpha=0.65, label=lbl, edgecolor="white")
axes[2].set_title("Distribusi Jumlah Kata")
axes[2].set_xlabel("Jumlah kata")
axes[2].set_ylabel("Frekuensi")
axes[2].legend()

plt.tight_layout()
plt.savefig(f"{OUT}/1_eda.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"   ✓ Grafik EDA disimpan")

# ─────────────────────────────────────────────
# 3. PREPROCESSING
# ─────────────────────────────────────────────
print("\n[3/8] Preprocessing teks...")

STOP_ID = set(stopwords.words("indonesian")) | {
    "yang", "dan", "di", "ke", "dari", "ini", "itu", "untuk", "dengan",
    "pada", "adalah", "ada", "akan", "juga", "tidak", "bisa", "sudah",
    "atau", "oleh", "dalam", "lebih", "saat", "kita", "kami", "mereka",
}

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)   # hapus URL
    text = re.sub(r"<[^>]+>", " ", text)                  # hapus HTML tag
    text = re.sub(r"[^a-z\s]", " ", text)                 # hapus non-alpha
    text = re.sub(r"\s+", " ", text).strip()
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_ID and len(t) > 2]
    return " ".join(tokens)

df["cleaned"] = df["content"].apply(preprocess)
print(f"   ✓ Sebelum: rata-rata {df['content'].str.split().str.len().mean():.0f} kata")
print(f"   ✓ Setelah: rata-rata {df['cleaned'].str.split().str.len().mean():.0f} kata")

# Visualisasi preprocessing
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle("Hasil Preprocessing Teks", fontsize=14, fontweight="bold")

sample_words = pd.Series(" ".join(df["cleaned"]).split()).value_counts()
top_fake = pd.Series(" ".join(df[df.label=="FAKE"]["cleaned"]).split()).value_counts().head(12)
top_real = pd.Series(" ".join(df[df.label=="REAL"]["cleaned"]).split()).value_counts().head(12)

axes[0].barh(top_fake.index[::-1], top_fake.values[::-1], color=COLORS["fake"], edgecolor="white")
axes[0].set_title("Top 12 Kata — FAKE")
axes[0].set_xlabel("Frekuensi")

axes[1].barh(top_real.index[::-1], top_real.values[::-1], color=COLORS["real"], edgecolor="white")
axes[1].set_title("Top 12 Kata — REAL")
axes[1].set_xlabel("Frekuensi")

plt.tight_layout()
plt.savefig(f"{OUT}/2_preprocessing.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"   ✓ Grafik preprocessing disimpan")

# ─────────────────────────────────────────────
# 4. FEATURE EXTRACTION (TF-IDF)
# ─────────────────────────────────────────────
print("\n[4/8] Feature extraction (TF-IDF)...")

X = df["cleaned"]
y = (df["label"] == "FAKE").astype(int)   # 1=FAKE, 0=REAL

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

tfidf = TfidfVectorizer(max_features=10_000, ngram_range=(1, 2), min_df=3)
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf  = tfidf.transform(X_test)

feature_names = np.array(tfidf.get_feature_names_out())
print(f"   ✓ Vocab size: {len(feature_names):,} fitur")
print(f"   ✓ Train: {X_train_tfidf.shape[0]:,} | Test: {X_test_tfidf.shape[0]:,}")

# ─────────────────────────────────────────────
# 5. TRAINING
# ─────────────────────────────────────────────
print("\n[5/8] Training model...")

models = {
    "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    "Naive Bayes"        : MultinomialNB(alpha=0.5),
    "Random Forest"      : RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
}

results = {}
for name, model in models.items():
    model.fit(X_train_tfidf, y_train)
    y_pred = model.predict(X_test_tfidf)
    y_prob = model.predict_proba(X_test_tfidf)[:, 1] if hasattr(model, "predict_proba") else None
    results[name] = {
        "model"    : model,
        "y_pred"   : y_pred,
        "y_prob"   : y_prob,
        "accuracy" : accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall"   : recall_score(y_test, y_pred, zero_division=0),
        "f1"       : f1_score(y_test, y_pred, zero_division=0),
        "cm"       : confusion_matrix(y_test, y_pred),
    }
    print(f"   ✓ {name}: Acc={results[name]['accuracy']:.4f}  F1={results[name]['f1']:.4f}")

best_name  = max(results, key=lambda k: results[k]["f1"])
best       = results[best_name]
print(f"\n   ★ Best model: {best_name}")

# ─────────────────────────────────────────────
# 6. EVALUASI & VISUALISASI
# ─────────────────────────────────────────────
print("\n[6/8] Evaluasi & visualisasi...")

# ── 6a. Perbandingan metrik semua model ──
metrics  = ["accuracy", "precision", "recall", "f1"]
labels_m = ["Accuracy", "Precision", "Recall", "F1-Score"]
x        = np.arange(len(labels_m))
width    = 0.25
palette  = [COLORS["blue"], COLORS["amber"], COLORS["gray"]]

fig, ax = plt.subplots(figsize=(11, 5))
for i, (name, res) in enumerate(results.items()):
    vals = [res[m] for m in metrics]
    bars = ax.bar(x + i*width, vals, width, label=name, color=palette[i],
                  edgecolor="white", alpha=0.9)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
                f"{val:.3f}", ha="center", va="bottom", fontsize=8)

ax.set_xticks(x + width)
ax.set_xticklabels(labels_m)
ax.set_ylim(0.8, 1.05)
ax.set_title("Perbandingan Metrik Evaluasi — Semua Model", pad=12)
ax.set_ylabel("Score")
ax.legend(loc="lower right")
ax.set_facecolor(COLORS["bg"])
plt.tight_layout()
plt.savefig(f"{OUT}/3_model_comparison.png", dpi=150, bbox_inches="tight")
plt.close()

# ── 6b. Confusion Matrix — best model ──
cm = best["cm"]
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="RdYlGn",
            xticklabels=["Predicted REAL", "Predicted FAKE"],
            yticklabels=["Actual REAL", "Actual FAKE"],
            ax=ax, linewidths=0.5, linecolor="white",
            annot_kws={"size": 16, "weight": "bold"})
ax.set_title(f"Confusion Matrix — {best_name}", pad=12)
plt.tight_layout()
plt.savefig(f"{OUT}/4_confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()

# ── 6c. Classification report heatmap ──
report = classification_report(y_test, best["y_pred"],
                               target_names=["REAL", "FAKE"], output_dict=True)
report_df = pd.DataFrame(report).transpose().iloc[:2, :3]

fig, ax = plt.subplots(figsize=(7, 3))
sns.heatmap(report_df, annot=True, fmt=".3f", cmap="YlGn",
            vmin=0.85, vmax=1.0, ax=ax, linewidths=0.5, linecolor="white",
            annot_kws={"size": 13})
ax.set_title(f"Classification Report — {best_name}", pad=12)
plt.tight_layout()
plt.savefig(f"{OUT}/5_classification_report.png", dpi=150, bbox_inches="tight")
plt.close()

# ── 6d. ROC Curve ──
fig, ax = plt.subplots(figsize=(7, 6))
roc_colors = [COLORS["blue"], COLORS["amber"], COLORS["gray"]]
for (name, res), col in zip(results.items(), roc_colors):
    if res["y_prob"] is not None:
        fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
        roc_auc     = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=col, lw=2, label=f"{name} (AUC={roc_auc:.3f})")

ax.plot([0,1],[0,1], color=COLORS["gray"], linestyle="--", lw=1.5, label="Random baseline")
ax.set_xlim([-0.01, 1.0])
ax.set_ylim([0.0, 1.05])
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve — Semua Model", pad=12)
ax.legend(loc="lower right")
ax.set_facecolor(COLORS["bg"])
plt.tight_layout()
plt.savefig(f"{OUT}/6_roc_curve.png", dpi=150, bbox_inches="tight")
plt.close()

# ── 6e. Learning curve ──
print("   → Learning curve (membutuhkan beberapa saat)...")
lr_model   = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
train_sizes, train_scores, val_scores = learning_curve(
    lr_model, X_train_tfidf, y_train,
    cv=5, n_jobs=-1, train_sizes=np.linspace(0.1, 1.0, 8), scoring="f1"
)

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(train_sizes, train_scores.mean(axis=1), "o-",
        color=COLORS["blue"],  label="Training F1",   lw=2)
ax.fill_between(train_sizes,
                train_scores.mean(1)-train_scores.std(1),
                train_scores.mean(1)+train_scores.std(1),
                alpha=0.15, color=COLORS["blue"])
ax.plot(train_sizes, val_scores.mean(axis=1), "s-",
        color=COLORS["real"],  label="Validation F1", lw=2)
ax.fill_between(train_sizes,
                val_scores.mean(1)-val_scores.std(1),
                val_scores.mean(1)+val_scores.std(1),
                alpha=0.15, color=COLORS["real"])
ax.set_title("Learning Curve — Logistic Regression", pad=12)
ax.set_xlabel("Jumlah data training")
ax.set_ylabel("F1-Score")
ax.set_ylim(0.7, 1.02)
ax.legend()
ax.set_facecolor(COLORS["bg"])
plt.tight_layout()
plt.savefig(f"{OUT}/7_learning_curve.png", dpi=150, bbox_inches="tight")
plt.close()

# ── 6f. Top TF-IDF features per kelas ──
lr        = results["Logistic Regression"]["model"]
coefs     = lr.coef_[0]
top_n     = 15
top_fake_idx = np.argsort(coefs)[-top_n:][::-1]
top_real_idx = np.argsort(coefs)[:top_n]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Top 15 Fitur TF-IDF per Kelas (Logistic Regression)", fontsize=13, fontweight="bold")

axes[0].barh([feature_names[i] for i in top_fake_idx[::-1]],
             [coefs[i] for i in top_fake_idx[::-1]],
             color=COLORS["fake"], edgecolor="white")
axes[0].set_title("Indikator FAKE (bobot positif)")
axes[0].set_xlabel("Koefisien LR")
axes[0].set_facecolor(COLORS["bg"])

axes[1].barh([feature_names[i] for i in top_real_idx],
             [abs(coefs[i]) for i in top_real_idx],
             color=COLORS["real"], edgecolor="white")
axes[1].set_title("Indikator REAL (bobot negatif)")
axes[1].set_xlabel("|Koefisien LR|")
axes[1].set_facecolor(COLORS["bg"])

plt.tight_layout()
plt.savefig(f"{OUT}/8_top_features.png", dpi=150, bbox_inches="tight")
plt.close()

print(f"   ✓ Semua grafik disimpan ke {OUT}/")

# ─────────────────────────────────────────────
# 7. RINGKASAN EVALUASI
# ─────────────────────────────────────────────
print("\n[7/8] Ringkasan evaluasi\n")
print("=" * 58)
print(f"{'MODEL':<22} {'ACC':>7} {'PREC':>7} {'REC':>7} {'F1':>7}")
print("-" * 58)
for name, res in results.items():
    print(f"{name:<22} {res['accuracy']:>7.4f} {res['precision']:>7.4f}"
          f" {res['recall']:>7.4f} {res['f1']:>7.4f}")
print("=" * 58)

tn, fp, fn, tp = best["cm"].ravel()
print(f"\nConfusion Matrix — {best_name}:")
print(f"  True Positive  (FAKE benar prediksi FAKE): {tp}")
print(f"  True Negative  (REAL benar prediksi REAL): {tn}")
print(f"  False Positive (REAL salah prediksi FAKE): {fp}")
print(f"  False Negative (FAKE salah prediksi REAL): {fn}")

print(f"\nClassification Report ({best_name}):")
print(classification_report(y_test, best["y_pred"], target_names=["REAL", "FAKE"]))

# ─────────────────────────────────────────────
# 8. DEMO PREDIKSI BERITA BARU
# ─────────────────────────────────────────────
print("\n[8/8] Demo prediksi berita baru\n")

best_model = best["model"]

demo_news = [
    ("TERBONGKAR! Pemerintah sembunyikan konspirasi chip vaksin COVID dari "
     "rakyat Indonesia. Sebarkan sebelum dihapus!",
     "FAKE"),
    ("Berdasarkan laporan resmi BPS, pertumbuhan ekonomi Indonesia pada kuartal "
     "ketiga mencapai 5,2 persen, didukung konsumsi domestik dan ekspor.",
     "REAL"),
    ("Ilmuwan NASA akui bumi datar! Bukti nyata disembunyikan elit global "
     "selama puluhan tahun. Viral! Bagikan sekarang!",
     "FAKE"),
    ("WHO merilis panduan terbaru penanganan influenza musiman berdasarkan "
     "hasil penelitian kolaborasi 40 negara anggota.",
     "REAL"),
]

print(f"{'#':<3} {'PREDIKSI':<10} {'AKTUAL':<10} {'P(FAKE)':>8}  JUDUL")
print("-" * 80)
for i, (text, actual) in enumerate(demo_news, 1):
    cleaned   = preprocess(text)
    vec       = tfidf.transform([cleaned])
    pred_int  = best_model.predict(vec)[0]
    pred_lbl  = "FAKE" if pred_int else "REAL"
    prob_fake = best_model.predict_proba(vec)[0][1]
    match     = "✓" if pred_lbl == actual else "✗"
    print(f"{i:<3} {pred_lbl:<10} {actual:<10} {prob_fake:>7.1%}  {match}  {text[:55]}...")

print("\n✅ Selesai! Semua output disimpan di:", OUT)
print("   File grafik:")
for f in sorted(os.listdir(OUT)):
    print(f"   · {f}")
