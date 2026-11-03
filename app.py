import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

st.set_page_config(page_title="Portal Psikotes IST - PT Bumi Mas Wahyu", page_icon="🧠", layout="wide")

RESULTS_FILE = "rekap_ist_lengkap.csv"
ADMIN_PASSWORD = "adminbmw"

SUBTESTS_CONFIG = {
    1: {"code": "SE", "title": "01. Melengkapi Kalimat (SE)", "time": 360, "type": "pg"},
    2: {"code": "WA", "title": "02. Mencari Kata Berbeda (WA)", "time": 360, "type": "pg"},
    3: {"code": "AN", "title": "03. Analogi Kata (AN)", "time": 420, "type": "pg"},
    4: {"code": "GE", "title": "04. Persamaan Kata (GE)", "time": 480, "type": "isian_ge"},
    5: {"code": "RA", "title": "05. Hitungan Matematika (RA)", "time": 600, "type": "isian_num"},
    6: {"code": "ZR", "title": "06. Deret Angka (ZR)", "time": 600, "type": "isian_num"},
    7: {"code": "FA", "title": "07. Potongan Gambar (FA)", "time": 420, "type": "pg_spasial"},
    8: {"code": "WU", "title": "08. Rotasi Kubus (WU)", "time": 540, "type": "pg_spasial"},
    9: {"code": "ME", "title": "09. Daya Mengingat (ME)", "time_memorize": 180, "time_test": 360, "type": "pg_me"}
}

for k in ["page", "current_subtest", "subtest_9_phase", "user_info", "answers", "start_time", "admin_logged_in"]:
    if k not in st.session_state:
        st.session_state[k] = "register" if k == "page" else (1 if k == "current_subtest" else ("memorize" if k == "subtest_9_phase" else ({} if k in ["user_info", "answers"] else False)))

fa_k = ["a","c","d","b","d","e","c","e","e","d","d","b","d","c","b","e","b","d","a","c"]
wu_k = ["a","e","b","c","d","a","e","c","b","a","e","d","b","c","d","a","e","c","b","d"]
me_d = [("r","a) bunga"),("f","d) kesenian"),("b","e) binatang"),("f","c) burung"),("m","d) kesenian"),("g","a) bunga"),("h","e) binatang"),("a","c) burung"),("s","b) perkakas"),("d","a) bunga"),("j","c) burung"),("e","d) kesenian"),("k","b) perkakas"),("c","b) perkakas"),("z","e) binatang"),("p","d) kesenian"),("t","c) burung"),("l","a) bunga"),("w","b) perkakas"),("o","e) binatang")]

QUESTIONS_DATA = {
    1: [
        {"id": 1, "no": "01", "q": "Pengaruh seseorang terhadap orang lain seharusnya bergantung pada .....", "options": ["a) kekuasaan", "b) bujukan", "c) kekayaan", "d) keberanian", "e) kewibawaan"], "key": "e) kewibawaan"},
        {"id": 2, "no": "02", "q": "Lawannya 'hemat' ialah ...............", "options": ["a) murah", "b) kikir", "c) boros", "d) bernilai", "e) kaya"], "key": "c) boros"},
        {"id": 3, "no": "03", "q": ".......... tidak termasuk cuaca", "options": ["a) angin puyuh", "b) halilintar", "c) salju", "d) gempa bumi", "e) kabut"], "key": "d) gempa bumi"},
        {"id": 4, "no": "04", "q": "Lawannya 'setia' ialah ...............", "options": ["a) cinta", "b) benci", "c) persahabatan", "d) khianat", "e) permusuhan"], "key": "d) khianat"},
        {"id": 5, "no": "05", "q": "Seekor kuda selalu mempunyai ...............", "options": ["a) kandang", "b) ladam", "c) pelana", "d) kuku", "e) surai"], "key": "d) kuku"},
        {"id": 6, "no": "06", "q": "Seorang paman ............... lebih tua dari kemenakannya.", "options": ["a) jarang", "b) biasanya", "c) selalu", "d) tidak pernah", "e) kadang-kadang"], "key": "b) biasanya"},
        {"id": 7, "no": "07", "q": "Pada jumlah yang sama, nilai kalori yang tertinggi terdapat pada ...............", "options": ["a) ikan", "b) daging", "c) lemak", "d) tahu", "e) sayuran"], "key": "c) lemak"},
        {"id": 8, "no": "08", "q": "Pada suatu pertandingan selalu terdapat ...............", "options": ["a) lawan", "b) wasit", "c) penonton", "d) sorak", "e) kemenangan"], "key": "a) lawan"},
        {"id": 9, "no": "09", "q": "Suatu pernyataan yang belum dipastikan dikatakan sebagai pernyataan yang .....", "options": ["a) paradoks", "b) tergesa-gesa", "c) mempunyai arti rangkap", "d) menyesatkan", "e) hipotesis"], "key": "e) hipotesis"},
        {"id": 10, "no": "10", "q": "Pada sepatu selalu terdapat ...............", "options": ["a) kulit", "b) sol", "c) tali sepatu", "d) gesper", "e) lidah"], "key": "b) sol"},
        {"id": 11, "no": "11", "q": "Suatu ............... tidak menyangkut persoalan pencegahan kecelakaan.", "options": ["a) lampu lalu lintas", "b) kacamata pelindung", "c) kotak PPPK", "d) tanda peringatan", "e) palang kereta api"], "key": "c) kotak PPPK"},
        {"id": 12, "no": "12", "q": "Mata uang logam Rp 50,- tahun 1991, garis tengahnya ialah ............... mm.", "options": ["a) 17", "b) 29", "c) 25", "d) 20", "e) 15"], "key": "d) 20"},
        {"id": 13, "no": "13", "q": "Seseorang yang bersikap menyangsikan setiap kemajuan ialah seorang yang .....", "options": ["a) demokratis", "b) radikal", "c) liberal", "d) konservatif", "e) anarkis"], "key": "d) konservatif"},
        {"id": 14, "no": "14", "q": "Lawannya 'tidak pernah' ialah ...............", "options": ["a) sering", "b) kadang-kadang", "c) jarang", "d) kerap kali", "e) selalu"], "key": "e) selalu"},
        {"id": 15, "no": "15", "q": "Jarak antara Jakarta - Surabaya kira-kira ............... Km", "options": ["a) 650", "b) 1000", "c) 800", "d) 600", "e) 950"], "key": "c) 800"},
        {"id": 16, "no": "16", "q": "Untuk dapat membuat nada yang rendah dan mendalam, kita memerlukan banyak ....", "options": ["a) kekuatan", "b) peranan", "c) ayunan", "d) berat", "e) suara"], "key": "a) kekuatan"},
        {"id": 17, "no": "17", "q": "Ayah ............... lebih berpengalaman dari pada anaknya", "options": ["a) selalu", "b) biasanya", "c) jauh", "d) jarang", "e) pada dasarnya"], "key": "b) biasanya"},
        {"id": 18, "no": "18", "q": "Diantara kota-kota berikut ini, maka kota ..... letaknya paling selatan.", "options": ["a) Jakarta", "b) Bandung", "c) Cirebon", "d) Semarang", "e) Surabaya"], "key": "b) Bandung"},
        {"id": 19, "no": "19", "q": "Jika kita mengetahui jumlah presentase nomor-nomor lotere yang tidak menang, maka kita dapat menghitung .....", "options": ["a) jumlah nomor yang menang", "b) pajak lotere", "c) kemungkinan menang", "d) jumlah pengikut", "e) tinggi keuntungan"], "key": "c) kemungkinan menang"},
        {"id": 20, "no": "20", "q": "Seorang anak yang berumur 10 tahun tingginya rata-rata ............... cm", "options": ["a) 150", "b) 130", "c) 110", "d) 105", "e) 115"], "key": "b) 130"}
    ],
    2: [{"id": 20+i, "no": str(20+i), "q": "Pilihlah kata yang tidak memiliki kesamaan:", "options": ["a","b","c","d","e"], "key": k} for i, k in enumerate(["b","b","d","c","c","c","c","d","d","a","e","a","a","b","c","a","d","e","b","c"], 1)],
    3: [{"id": 40+i, "no": str(40+i), "q": f"Soal Analogi No. {40+i}", "options": ["a","b","c","d","e"], "key": k} for i, k in enumerate(["c","e","d","d","d","a","d","b","e","d","c","c","c","c","d","c","c","d","e","e"], 1)],
    4: [
        {"id": 61, "no": "61", "q": "Mawar – Melati", "skor_2": ["bunga", "kembang", "perdu"], "skor_1": ["tumbuh-tumbuhan", "tumbuhan", "tangkai", "harum"]},
        {"id": 62, "no": "62", "q": "Mata – Telinga", "skor_2": ["alat indera", "indera", "panca indera"], "skor_1": ["organ", "alat tubuh"]},
        {"id": 63, "no": "63", "q": "Gula – Intan", "skor_2": ["hablur", "kristal", "zat arang"], "skor_1": ["berkilauan", "mengkilat", "bening"]},
        {"id": 64, "no": "64", "q": "Salju – Hujan", "skor_2": ["musim", "cuaca"], "skor_1": ["iklim"]},
        {"id": 65, "no": "65", "q": "Pengantar Surat – Telepon", "skor_2": ["pembawa berita", "alat perhubungan"], "skor_1": ["telekomunikasi", "perhubungan", "komunikasi"]},
        {"id": 66, "no": "66", "q": "Kamera – Kacamata", "skor_2": ["alat optik", "optik"], "skor_1": ["lensa"]},
        {"id": 67, "no": "67", "q": "Lambung – Usus", "skor_2": ["alat pencernaan", "perut"], "skor_1": ["jalan makanan", "isi perut", "pencernaan makanan"]},
        {"id": 68, "no": "68", "q": "Banyak – Sedikit", "skor_2": ["jumlah", "kuantitas", "penyebut jumlah"], "skor_1": ["mengukur", "ukuran"]},
        {"id": 69, "no": "69", "q": "Telur – Benih", "skor_2": ["bibit", "bakal", "embrio", "alat pembiak"], "skor_1": ["sel", "pembiakan"]},
        {"id": 70, "no": "70", "q": "Bendera – Lencana", "skor_2": ["simbol", "lambang", "tanda"], "skor_1": ["nama", "tanda pengenal"]},
        {"id": 71, "no": "71", "q": "Rumput – Gajah", "skor_2": ["makhluk", "organisme", "makhluk hidup"], "skor_1": ["tumbuh", "ilmu hayat", "biologi"]},
        {"id": 72, "no": "72", "q": "Ember – Kantong", "skor_2": ["wadah", "tempat pengisi", "tempat penyimpan"], "skor_1": ["alat", "tempat sesuatu"]},
        {"id": 73, "no": "73", "q": "Awal – Akhir", "skor_2": ["pengertian waktu", "batas"], "skor_1": ["waktu", "lamanya", "masa"]},
        {"id": 74, "no": "74", "q": "Kikir – Boros", "skor_2": ["kata sifat", "watak", "sifat karakter"], "skor_1": ["sifat"]},
        {"id": 75, "no": "75", "q": "Penawaran – Permintaan", "skor_2": ["regulator harga", "pengertian ekonomi"], "skor_1": ["dagang", "pembelian", "penjualan"]},
        {"id": 76, "no": "76", "q": "Atas – Bawah", "skor_2": ["pengertian ruang", "penyebut ruang"], "skor_1": ["arah", "tempat", "ruang", "letak"]}
    ],
    5: [{"id": 76+i, "no": str(76+i), "q": f"Soal Hitungan RA No. {76+i}", "key": k} for i, k in enumerate(["35","280","205","26","30","70","45","50","84","78","19","6","75","90","120","17","24","5","48","1"], 1)],
    6: [{"id": 96+i, "no": str(96+i), "q": f"Soal Deret ZR No. {96+i}", "key": k} for i, k in enumerate(["27","25","27","15","46","10","42","7","5","14","8","14","45","63","12","80","14","12","63","10"], 1)],
    7: [{"id": 116+i, "no": str(116+i), "q": f"Potongan Gambar No. {116+i}", "options": ["a","b","c","d","e"], "key": fa_k[i-1]} for i in range(1, 21)],
    8: [{"id": 136+i, "no": str(136+i), "q": f"Rotasi Kubus No. {136+i}", "options": ["a","b","c","d","e"], "key": wu_k[i-1]} for i in range(1, 21)],
    9: [{"id": 156+i, "no": str(156+i), "q": f"Kata dengan huruf permulaan '{me_d[i-1][0]}' adalah sebuah .....", "options": ["a) bunga", "b) perkakas", "c) burung", "d) kesenian", "e) binatang"], "key": me_d[i-1][1]} for i in range(1, 21)]
}

def calculate_scores():
    subtest_results = {}
    total_raw = 0
    for st_id, code in [(1, "SE"), (2, "WA"), (3, "AN"), (7, "FA"), (8, "WU"), (9, "ME")]:
        score = sum(1 for q in QUESTIONS_DATA.get(st_id, []) if st.session_state.answers.get(q['id']) == q['key'])
        subtest_results[f"{code}_Score"] = score
        total_raw += score

    ge_score = 0
    for q in QUESTIONS_DATA.get(4, []):
        user_ans = str(st.session_state.answers.get(q['id'], "")).strip().lower()
        if any(k in user_ans for k in q.get("skor_2", [])): ge_score += 2
        elif any(k in user_ans for k in q.get("skor_1", [])): ge_score += 1
    subtest_results["GE_Score"] = ge_score
    total_raw += ge_score

    for st_id, code in [(5, "RA"), (6, "ZR")]:
        score = sum(1 for q in QUESTIONS_DATA.get(st_id, []) if str(st.session_state.answers.get(q['id'], "")).strip() == q['key'])
        subtest_results[f"{code}_Score"] = score
        total_raw += score

    subtest_results["Total_Raw_Score"] = total_raw
    return subtest_results

st.sidebar.title("📌 Navigasi Sistem")
mode = st.sidebar.radio("Pilih Akses:", ["Portal Tes Pelamar", "Dashboard Admin HR"])

if mode == "Portal Tes Pelamar":
    if st.session_state.page == "register":
        st.title("🏛️ PT Bumi Mas Wahyu")
        st.subheader("Portal Psikotes Online - Intelligenz-Struktur-Test (IST)")
        with st.form("form_registrasi"):
            nama = st.text_input("Nama Lengkap")
            email = st.text_input("Email")
            no_hp = st.text_input("Nomor WhatsApp/HP")
            posisi = st.selectbox("Posisi yang Dilamar", ["Staff Closing (Sales / CS)", "Admin Rekrutmen / HR", "Supervisor Penjualan", "Staff Keuangan / Akuntansi", "Arsitek / Site Engineer", "Posisi Lainnya"])
            if st.form_submit_button("Mulai Tes IST 🚀"):
                if not nama or not no_hp or not email:
                    st.error("Mohon isi seluruh data diri secara lengkap.")
                else:
                    st.session_state.user_info = {"nama": nama, "email": email, "no_hp": no_hp, "posisi": posisi, "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    st.session_state.start_time = time.time()
                    st.session_state.page = "test"
                    st.rerun()

    elif st.session_state.page == "test":
        current_st = st.session_state.current_subtest
        config = SUBTESTS_CONFIG[current_st]
        st.caption(f"Kandidat: **{st.session_state.user_info['nama']}** | Posisi: **{st.session_state.user_info['posisi']}**")

        if current_st == 9:
            if st.session_state.subtest_9_phase == "memorize":
                st.title("🧠 IST Subtes 09: Daya Mengingat (ME) — [Fase Menghafal]")
                st.warning("⏱️ Anda memiliki waktu **3 Menit** untuk menghafal kata-kata di bawah ini!")
                elapsed = int(time.time() - st.session_state.start_time)
                remaining = max(0, config["time_memorize"] - elapsed)
                mins, secs = divmod(remaining, 60)
                st.error(f"⏱️ **SISA WAKTU MENGHAFAL:** {mins:02d}:{secs:02d}")
                st.markdown("""
                ### 📋 KATA-KATA YANG HARUS DIHAFAL:
                * **BUNGA** : Bunga, Dahlia, Melati, Ranunkel, Lilia
                * **PERKAKAS** : Baut, Jarum, Kikir, Cangkul, Wajan
                * **BURUNG** : Itik, Elang, Walet, Tekukur, Luntur
                * **KESENIAN** : Flut, Operet, Quintet, Arca, Ukiran
                * **BINATANG** : Beruang, Zebra, Rusa, Musang, Unta
                """)
                if remaining == 0 or st.button("Selesai Menghafal & Lanjut Ke Soal ➔"):
                    st.session_state.subtest_9_phase = "test"
                    st.session_state.start_time = time.time()
                    st.rerun()

            elif st.session_state.subtest_9_phase == "test":
                st.title("🧠 IST Subtes 09: Daya Mengingat (ME) — [Fase Pengerjaan Soal]")
                elapsed = int(time.time() - st.session_state.start_time)
                remaining = max(0, config["time_test"] - elapsed)
                mins, secs = divmod(remaining, 60)
                st.error(f"⏱️ **SISA WAKTU MENJAWAB SOAL:** {mins:02d}:{secs:02d}")
                if remaining == 0:
                    st.session_state.page = "result"
                    st.rerun()

                with st.form("form_subtest_9_test"):
                    for q in QUESTIONS_DATA.get(9, []):
                        st.markdown(f"**Soal {q['no']}.** {q['q']}")
                        st.session_state.answers[q['id']] = st.radio(f"Pilih jawaban No. {q['no']}:", options=q['options'], key=f"q_{q['id']}")
                        st.markdown("---")
                    if st.form_submit_button("Selesaikan Ujian IST 📤"):
                        st.session_state.page = "result"
                        st.rerun()
        else:
            st.title(f"🧠 IST Subtes: {config['title']}")
            elapsed = int(time.time() - st.session_state.start_time)
            remaining = max(0, config["time"] - elapsed)
            mins, secs = divmod(remaining, 60)
            st.error(f"⏱️ **SISA WAKTU SUBTES INI:** {mins:02d}:{secs:02d}")

            if remaining == 0:
                st.session_state.current_subtest += 1
                st.session_state.start_time = time.time()
                st.rerun()

            with st.form(f"form_subtest_{current_st}"):
                for q in QUESTIONS_DATA.get(current_st, []):
                    st.markdown(f"**Soal {q['no']}.** {q['q']}")
                    if config["type"] in ["pg", "pg_spasial"]:
                        st.session_state.answers[q['id']] = st.radio(f"Pilih jawaban No. {q['no']}:", options=q['options'], key=f"q_{q['id']}")
                    elif config["type"] in ["isian_ge", "isian_num"]:
                        st.session_state.answers[q['id']] = st.text_input(f"Ketik jawaban No. {q['no']}:", key=f"q_{q['id']}")
                    st.markdown("---")

                if st.form_submit_button("Simpan & Lanjut Subtes Berikutnya ➔"):
                    st.session_state.current_subtest += 1
                    st.session_state.start_time = time.time()
                    st.rerun()

    elif st.session_state.page == "result":
        st.title("✅ Seluruh 9 Subtes IST Selesai")
        st.success(f"Terima kasih **{st.session_state.user_info['nama']}**, jawaban Anda telah tersimpan.")
        scores = calculate_scores()
        final_record = {**st.session_state.user_info, **scores}
        df_new = pd.DataFrame([final_record])
        df_final = pd.concat([pd.read_csv(RESULTS_FILE, sep=';'), df_new], ignore_index=True) if os.path.exists(RESULTS_FILE) else df_new
        df_final.to_csv(RESULTS_FILE, index=False, sep=';', encoding='utf-8-sig')
        st.info(" Data hasil ujian disinkronkan dengan database rekrutmen PT Bumi Mas Wahyu.")

elif mode == "Dashboard Admin HR":
    st.title("🔐 Dashboard Rekrutmen HR - PT Bumi Mas Wahyu")
    if not st.session_state.admin_logged_in:
        pwd = st.text_input("Masukkan Kata Sandi Admin HR:", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Kata sandi salah!")
    else:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"admin_logged_in": False}))
        if not os.path.exists(RESULTS_FILE):
            st.warning("Belum ada data kandidat.")
        else:
            df_results = pd.read_csv(RESULTS_FILE, sep=';')
            col1, col2 = st.columns(2)
            col1.metric("Total Kandidat IST", len(df_results))
            if "Total_Raw_Score" in df_results.columns:
                col2.metric("Rata-rata Skor Mentah", f"{df_results['Total_Raw_Score'].mean():.1f}")
            st.markdown("---")
            posisi_filter = st.selectbox("Filter Posisi:", ["Semua Posisi"] + list(df_results["posisi"].unique()))
            df_display = df_results[df_results["posisi"] == posisi_filter] if posisi_filter != "Semua Posisi" else df_results
            st.dataframe(df_display, use_container_width=True)
            csv = df_display.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 Unduh Rekap Hasil Ujian (Format Excel Rapi)", data=csv, file_name=f"rekap_ist_bmw_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')