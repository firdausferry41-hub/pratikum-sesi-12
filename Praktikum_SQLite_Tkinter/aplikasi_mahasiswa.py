
import sqlite3
import tkinter as tk
from contextlib import contextmanager
from tkinter import ttk, messagebox

DB_NAME = "mahasiswa.db"
DAFTAR_PRODI = ["Informatika", "Sistem Informasi", "Manajemen", "Akuntansi"]


# ==================================================
# 1. FUNGSI KONEKSI DATABASE
# ==================================================
@contextmanager
def koneksi():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================================================
# 2. MEMBUAT TABEL MAHASISWA
# ==================================================
def buat_tabel():
    with koneksi() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                nim TEXT NOT NULL UNIQUE,
                prodi TEXT NOT NULL,
                alamat TEXT,
                angkatan INTEGER
            )
        """)

        # Memeriksa apakah kolom angkatan sudah tersedia
        kolom_db = conn.execute(
            "PRAGMA table_info(mahasiswa)"
        ).fetchall()

        nama_kolom = [kolom[1] for kolom in kolom_db]

        if "angkatan" not in nama_kolom:
            conn.execute(
                "ALTER TABLE mahasiswa ADD COLUMN angkatan INTEGER"
            )


buat_tabel()


# ==================================================
# 3. JENDELA UTAMA
# ==================================================
root = tk.Tk()
root.title("Aplikasi Data Mahasiswa")
root.geometry("1000x650")


# ==================================================
# 4. FORMULIR MAHASISWA
# ==================================================
form = ttk.LabelFrame(root, text="Formulir Mahasiswa", padding=12)
form.pack(fill="x", padx=15, pady=12)

ttk.Label(form, text="Nama").grid(
    row=0, column=0, padx=5, pady=5, sticky="w"
)
entry_nama = ttk.Entry(form, width=30)
entry_nama.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(form, text="NIM").grid(
    row=0, column=2, padx=5, pady=5, sticky="w"
)
entry_nim = ttk.Entry(form, width=30)
entry_nim.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(form, text="Program Studi").grid(
    row=1, column=0, padx=5, pady=5, sticky="w"
)
combo_prodi = ttk.Combobox(
    form,
    values=DAFTAR_PRODI,
    state="readonly",
    width=27
)
combo_prodi.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(form, text="Alamat").grid(
    row=1, column=2, padx=5, pady=5, sticky="w"
)
entry_alamat = ttk.Entry(form, width=30)
entry_alamat.grid(row=1, column=3, padx=5, pady=5)

ttk.Label(form, text="Angkatan").grid(
    row=2, column=0, padx=5, pady=5, sticky="w"
)
entry_angkatan = ttk.Entry(form, width=30)
entry_angkatan.grid(row=2, column=1, padx=5, pady=5)


# ==================================================
# 5. FITUR PENCARIAN
# ==================================================
frame_cari = ttk.LabelFrame(root, text="Pencarian Mahasiswa", padding=10)
frame_cari.pack(fill="x", padx=15, pady=5)

ttk.Label(frame_cari, text="Nama atau NIM").pack(side="left", padx=5)

entry_cari = ttk.Entry(frame_cari, width=35)
entry_cari.pack(side="left", padx=5)


# ==================================================
# 6. TABEL TAMPILAN (TREEVIEW)
# ==================================================
kolom = ("id", "nama", "nim", "prodi", "alamat", "angkatan")

tabel = ttk.Treeview(
    root,
    columns=kolom,
    show="headings"
)

for key, judul in [
    ("id", "ID"),
    ("nama", "Nama"),
    ("nim", "NIM"),
    ("prodi", "Program Studi"),
    ("alamat", "Alamat"),
    ("angkatan", "Angkatan")
]:
    tabel.heading(key, text=judul)

tabel.column("id", width=50, anchor="center")
tabel.column("nama", width=160)
tabel.column("nim", width=120)
tabel.column("prodi", width=160)
tabel.column("alamat", width=250)
tabel.column("angkatan", width=100, anchor="center")

tabel.pack(fill="both", expand=True, padx=15, pady=8)


# ==================================================
# 7. MENAMPILKAN DATA (SELECT)
# ==================================================
def tampilkan_data():
    for item in tabel.get_children():
        tabel.delete(item)

    kata_kunci = entry_cari.get().strip()

    with koneksi() as conn:
        if kata_kunci:
            rows = conn.execute(
                """
                SELECT id, nama, nim, prodi, alamat, angkatan
                FROM mahasiswa
                WHERE nama LIKE ? OR nim LIKE ?
                ORDER BY id DESC
                """,
                (f"%{kata_kunci}%", f"%{kata_kunci}%")
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, nama, nim, prodi, alamat, angkatan
                FROM mahasiswa
                ORDER BY id DESC
                """
            ).fetchall()

    for row in rows:
        tabel.insert("", tk.END, values=row)


# ==================================================
# 8. MEMBERSIHKAN FORMULIR
# ==================================================
def bersihkan_form():
    entry_nama.delete(0, tk.END)
    entry_nim.delete(0, tk.END)
    combo_prodi.set("")
    entry_alamat.delete(0, tk.END)
    entry_angkatan.delete(0, tk.END)
    entry_nama.focus_set()


# ==================================================
# 9. MENYIMPAN DATA (INSERT)
# ==================================================
def simpan_data():
    nama = entry_nama.get().strip()
    nim = entry_nim.get().strip()
    prodi = combo_prodi.get().strip()
    alamat = entry_alamat.get().strip()
    angkatan = entry_angkatan.get().strip()

    if not nama or not nim or not prodi or not angkatan:
        messagebox.showwarning(
            "Validasi",
            "Nama, NIM, Program Studi, dan Angkatan wajib diisi."
        )
        return

    try:
        angkatan = int(angkatan)
    except ValueError:
        messagebox.showwarning(
            "Validasi",
            "Angkatan harus berupa angka."
        )
        return

    try:
        with koneksi() as conn:
            conn.execute(
                """
                INSERT INTO mahasiswa
                (nama, nim, prodi, alamat, angkatan)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nama, nim, prodi, alamat, angkatan)
            )

        messagebox.showinfo("Berhasil", "Data berhasil disimpan.")
        tampilkan_data()
        bersihkan_form()

    except sqlite3.IntegrityError:
        messagebox.showerror("NIM Duplikat", "NIM sudah terdaftar.")

    except sqlite3.Error as error:
        messagebox.showerror("Kesalahan Database", str(error))


# ==================================================
# 10. MENGHAPUS DATA (DELETE)
# ==================================================
def hapus_data():
    pilihan = tabel.selection()

    if not pilihan:
        messagebox.showwarning(
            "Pilih Data",
            "Pilih baris yang akan dihapus."
        )
        return

    data = tabel.item(pilihan[0], "values")
    record_id = int(data[0])

    if not messagebox.askyesno(
        "Konfirmasi",
        f"Hapus data {data[1]}?"
    ):
        return

    try:
        with koneksi() as conn:
            conn.execute(
                "DELETE FROM mahasiswa WHERE id = ?",
                (record_id,)
            )

        tampilkan_data()
        bersihkan_form()

        messagebox.showinfo("Berhasil", "Data berhasil dihapus.")

    except sqlite3.Error as error:
        messagebox.showerror("Kesalahan Database", str(error))


# ==================================================
# 11. MENGISI FORM DARI DATA TABEL
# ==================================================
def isi_form_dari_tabel(event=None):
    pilihan = tabel.selection()

    if not pilihan:
        return

    record_id = int(tabel.item(pilihan[0], "values")[0])

    with koneksi() as conn:
        row = conn.execute(
            """
            SELECT nama, nim, prodi, alamat, angkatan
            FROM mahasiswa
            WHERE id = ?
            """,
            (record_id,)
        ).fetchone()

    if row is None:
        return

    bersihkan_form()

    entry_nama.insert(0, row[0])
    entry_nim.insert(0, row[1])
    combo_prodi.set(row[2])
    entry_alamat.insert(0, row[3] or "")
    entry_angkatan.insert(0, row[4] if row[4] is not None else "")


# ==================================================
# 12. MENGUBAH DATA (UPDATE)
# ==================================================
def ubah_data():
    pilihan = tabel.selection()

    if not pilihan:
        messagebox.showwarning(
            "Pilih Data",
            "Pilih data yang akan diubah."
        )
        return

    record_id = int(tabel.item(pilihan[0], "values")[0])

    nama = entry_nama.get().strip()
    nim = entry_nim.get().strip()
    prodi = combo_prodi.get().strip()
    alamat = entry_alamat.get().strip()
    angkatan = entry_angkatan.get().strip()

    if not nama or not nim or not prodi or not angkatan:
        messagebox.showwarning(
            "Validasi",
            "Nama, NIM, Program Studi, dan Angkatan wajib diisi."
        )
        return

    try:
        angkatan = int(angkatan)
    except ValueError:
        messagebox.showwarning(
            "Validasi",
            "Angkatan harus berupa angka."
        )
        return

    try:
        with koneksi() as conn:
            conn.execute(
                """
                UPDATE mahasiswa
                SET nama = ?, nim = ?, prodi = ?, alamat = ?, angkatan = ?
                WHERE id = ?
                """,
                (nama, nim, prodi, alamat, angkatan, record_id)
            )

        tampilkan_data()
        bersihkan_form()

        messagebox.showinfo("Berhasil", "Data berhasil diperbarui.")

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "NIM Duplikat",
            "NIM sudah digunakan data lain."
        )

    except sqlite3.Error as error:
        messagebox.showerror("Kesalahan Database", str(error))


# ==================================================
# 13. MENGHUBUNGKAN PEMILIHAN TABEL DENGAN FORM
# ==================================================
tabel.bind("<<TreeviewSelect>>", isi_form_dari_tabel)


# ==================================================
# 14. TOMBOL PENCARIAN
# ==================================================
ttk.Button(
    frame_cari,
    text="Cari",
    command=tampilkan_data
).pack(side="left", padx=5)

ttk.Button(
    frame_cari,
    text="Reset Pencarian",
    command=lambda: (
        entry_cari.delete(0, tk.END),
        tampilkan_data()
    )
).pack(side="left", padx=5)


# ==================================================
# 15. TOMBOL APLIKASI
# ==================================================
baris_tombol = ttk.Frame(root)
baris_tombol.pack(fill="x", padx=15, pady=5)

ttk.Button(
    baris_tombol,
    text="Simpan Data",
    command=simpan_data
).pack(side="left", padx=4)

ttk.Button(
    baris_tombol,
    text="Ubah Data",
    command=ubah_data
).pack(side="left", padx=4)

ttk.Button(
    baris_tombol,
    text="Refresh",
    command=tampilkan_data
).pack(side="left", padx=4)

ttk.Button(
    baris_tombol,
    text="Bersihkan Form",
    command=bersihkan_form
).pack(side="left", padx=4)

ttk.Button(
    baris_tombol,
    text="Hapus Data Terpilih",
    command=hapus_data
).pack(side="right", padx=4)


# ==================================================
# 16. MENJALANKAN APLIKASI
# ==================================================
tampilkan_data()
root.mainloop()
