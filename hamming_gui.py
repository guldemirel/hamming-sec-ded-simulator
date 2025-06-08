import tkinter as tk
from tkinter import messagebox


def calculate_parity_bits(data_bits):
    m = len(data_bits)
    r = 0
    while (2 ** r) < (m + r + 1):
        r += 1
    return r

def insert_parity_bits(data_bits):
    m = len(data_bits)
    r = calculate_parity_bits(data_bits)
    j = 0
    k = 1
    hamming = []
    for i in range(1, m + r + 1):
        if i == 2 ** j:
            hamming.append(0)
            j += 1
        else:
            hamming.append(int(data_bits[-k]))
            k += 1
    return hamming[::-1]

def set_parity_bits(hamming):
    n = len(hamming)
    for i in range(n):
        if (i+1) & i == 0:
            parity_pos = i + 1
            parity = 0
            for j in range(1, n+1):
                if j & parity_pos and j != parity_pos:
                    parity ^= hamming[-j]
            hamming[-(i+1)] = parity
    return hamming

def generate_hamming_code(data_bits):
    bits = insert_parity_bits(data_bits)
    bits = set_parity_bits(bits)
    return bits

def introduce_error(code_bits, error_position):
    code_bits[-error_position] ^= 1
    return code_bits

def detect_error(hamming_bits):
    n = len(hamming_bits)
    error_position = 0
    for i in range(n):
        if (i + 1) & i == 0:
            parity_pos = i + 1
            parity = 0
            for j in range(1, n + 1):
                if j & parity_pos:
                    parity ^= hamming_bits[-j]
            if parity:
                error_position += parity_pos
    return error_position

def correct_error(hamming_bits):
    error_position = detect_error(hamming_bits)
    if error_position:
        hamming_bits[-error_position] ^= 1
    return hamming_bits, error_position

class HammingGUI:
    def __init__(self, root):
        self.root = root
        root.title("Hamming SEC-DED Simülatörü")

        tk.Label(root, text="Veri Girişi (8 / 16 / 32 bit):").grid(row=0, column=0, sticky="w")
        self.data_entry = tk.Entry(root, width=40)
        self.data_entry.grid(row=0, column=1)

        tk.Button(root, text="Kodla", command=self.encode_data).grid(row=1, column=0, pady=5)
        tk.Button(root, text="Hata Ekle", command=self.inject_error).grid(row=1, column=1)
        tk.Button(root, text="Hata Düzelt", command=self.fix_error).grid(row=1, column=2)

        self.output_text = tk.Text(root, width=80, height=10)
        self.output_text.grid(row=2, column=0, columnspan=3)

        tk.Label(root, text="Hata konumu (1'den başlayarak):").grid(row=3, column=0, sticky="w")
        self.error_entry = tk.Entry(root, width=10)
        self.error_entry.grid(row=3, column=1, sticky="w")

        self.hamming_code = []

    def encode_data(self):
        data = self.data_entry.get().strip()
        if not all(bit in "01" for bit in data):
            messagebox.showerror("Hata", "Sadece 0 ve 1 girmelisiniz.")
            return
        if len(data) not in (8, 16, 32):
            messagebox.showerror("Hata", "Veri uzunluğu 8, 16 veya 32 bit olmalı.")
            return

        self.hamming_code = generate_hamming_code(data)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Hamming Kodlu Veri:\n{''.join(map(str, self.hamming_code))}\n")

    def inject_error(self):
        if not self.hamming_code:
            messagebox.showerror("Hata", "Önce veri kodlayın.")
            return
        try:
            pos = int(self.error_entry.get())
            if pos < 1 or pos > len(self.hamming_code):
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir hata konumu girin.")
            return

        self.hamming_code = introduce_error(self.hamming_code, pos)
        self.output_text.insert(tk.END, f"\nHata eklendi (konum {pos}):\n{''.join(map(str, self.hamming_code))}\n")

    def fix_error(self):
        if not self.hamming_code:
            messagebox.showerror("Hata", "Önce veri kodlayın.")
            return

        corrected, pos = correct_error(self.hamming_code.copy())
        if pos == 0:
            self.output_text.insert(tk.END, "\nHata bulunamadı.\n")
        else:
            self.output_text.insert(tk.END, f"\nHata bulundu ve düzeltildi! (konum {pos})\n")
            self.output_text.insert(tk.END, f"Düzeltilmiş Veri:\n{''.join(map(str, corrected))}\n")
            self.hamming_code = corrected


if __name__ == "__main__":
    root = tk.Tk()
    app = HammingGUI(root)
    root.mainloop()
