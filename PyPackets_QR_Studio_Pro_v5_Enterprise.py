
"""
PyPackets QR Studio Pro v5.0 Enterprise Edition
Single-file enterprise demo edition
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import qrcode, sqlite3, os, csv
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DB = "enterprise_qr.db"

class EnterpriseQR:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPackets QR Studio Pro v5.0 Enterprise")
        self.root.geometry("1400x850")

        self.preview_file = "preview.png"
        self.init_db()
        self.build_ui()

    def init_db(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qr_type TEXT,
        content TEXT,
        saved_file TEXT,
        created_at TEXT)
        """)
        conn.commit()
        conn.close()

    def build_ui(self):
        left = ctk.CTkFrame(self.root, width=260)
        left.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left, text="PyPackets\nEnterprise", font=("Arial",28,"bold")).pack(pady=20)

        ctk.CTkButton(left,text="Generate QR",command=self.generate_qr).pack(fill="x",padx=10,pady=5)
        ctk.CTkButton(left,text="Save QR",command=self.save_qr).pack(fill="x",padx=10,pady=5)
        ctk.CTkButton(left,text="Bulk Generate CSV",command=self.bulk_generate).pack(fill="x",padx=10,pady=5)
        ctk.CTkButton(left,text="Export History CSV",command=self.export_history).pack(fill="x",padx=10,pady=5)
        ctk.CTkButton(left,text="Search History",command=self.search_history).pack(fill="x",padx=10,pady=5)
        ctk.CTkButton(left,text="Toggle Theme",command=self.toggle_theme).pack(fill="x",padx=10,pady=5)

        main = ctk.CTkFrame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main,text="QR Studio Enterprise Dashboard",font=("Arial",30,"bold")).pack(pady=10)

        self.type_menu = ctk.CTkOptionMenu(main, values=[
            "Website","Text","Email","Phone","WhatsApp"
        ])
        self.type_menu.pack(pady=5)

        self.text = ctk.CTkTextbox(main,height=120)
        self.text.pack(fill="x", padx=20, pady=10)

        self.preview = ctk.CTkLabel(main,text="QR Preview")
        self.preview.pack(pady=20)

        self.stats = ctk.CTkLabel(main,text="Generated: 0")
        self.stats.pack()

        self.status = ctk.CTkLabel(main,text="Ready")
        self.status.pack(side="bottom",pady=10)

        self.update_stats()

    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode=="Dark" else "dark")

    def prepare(self, txt):
        t = self.type_menu.get()
        if t=="Email":
            return "mailto:"+txt
        if t=="Phone":
            return "tel:"+txt
        if t=="WhatsApp":
            return "https://wa.me/"+txt
        return txt

    def generate_qr(self):
        txt = self.text.get("1.0","end").strip()
        if not txt:
            return

        qr = qrcode.make(self.prepare(txt))
        qr.save(self.preview_file)

        img = Image.open(self.preview_file)

        cimg = ctk.CTkImage(light_image=img,dark_image=img,size=(320,320))
        self.preview.configure(image=cimg,text="")
        self.preview.image = cimg

        self.status.configure(text="QR Generated")

    def save_qr(self):
        if not os.path.exists(self.preview_file):
            messagebox.showwarning("Warning","Generate QR first")
            return

        path = filedialog.asksaveasfilename(defaultextension=".png")
        if not path:
            return

        Image.open(self.preview_file).save(path)

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO history(qr_type,content,saved_file,created_at) VALUES(?,?,?,?)",
            (
                self.type_menu.get(),
                self.text.get("1.0","end").strip(),
                path,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        conn.commit()
        conn.close()

        self.update_stats()
        self.status.configure(text="Saved Successfully")

    def update_stats(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM history")
        total = cur.fetchone()[0]
        conn.close()
        self.stats.configure(text=f"Generated & Saved QR Codes: {total}")

    def search_history(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT qr_type,saved_file,created_at FROM history ORDER BY id DESC LIMIT 20")
        rows = cur.fetchall()
        conn.close()

        text = "\n".join([f"{r[2]} | {r[0]} | {r[1]}" for r in rows]) or "No records"
        messagebox.showinfo("History", text)

    def export_history(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT * FROM history")
        rows = cur.fetchall()
        conn.close()

        with open(path,"w",newline="",encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Type","Content","File","Date"])
            writer.writerows(rows)

        messagebox.showinfo("Success","History exported")

    def bulk_generate(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        sample = [
            "https://pypackets.com",
            "https://github.com",
            "https://python.org"
        ]

        for i, item in enumerate(sample, start=1):
            qrcode.make(item).save(os.path.join(folder, f"bulk_qr_{i}.png"))

        messagebox.showinfo("Success","Sample bulk QR generation completed")

root = ctk.CTk()
EnterpriseQR(root)
root.mainloop()
