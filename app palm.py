import cv2
import numpy as np
from keras.models import load_model
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

model = load_model("palm_detect_mnist_style.keras")

class_names = ["Chỉ tay Người Bình Thường", "Chỉ tay Người Giàu", "Chỉ tay Người Nghèo",]

palm_info = {
    "Chỉ tay Người Bình Thường": [
        "Đặc điểm: đường tài lộc có nhưng không đậm, không quá dài.",
        "Đường sinh đạo và trí đạo rõ nhưng không nổi bật.",
        "Ý nghĩa: cuộc sống ổn định ở mức trung bình, đủ ăn đủ mặc, ít biến động lớn."
    ],
    "Chỉ tay Người Giàu": [
        "Đặc điểm: đường tài lộc rõ ràng, đậm nét, kéo dài đến gò Mộc tinh.",
        "Thường có thêm các đường may mắn song song hoặc cắt chéo đẹp.",
        "Ý nghĩa: người có sự nghiệp thăng tiến, tài chính ổn định, nhiều cơ hội làm giàu."
    ],
    "Chỉ tay Người Nghèo": [
        "Đặc điểm: đường tài lộc mờ, đứt đoạn, khó nhìn thấy.",
        "Đường sinh đạo và trí đạo thường giao nhau hỗn loạn, thiếu mạch lạc.",
        "Ý nghĩa: cuộc sống vất vả, tài chính khó khăn, ít cơ hội tích lũy."
    ]
}

class PalmRecognitionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Nhận Diện Chỉ Tay")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        self.image_path = None
        self.original_image = None
        self.photo = None

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('Title.TLabel', background='#f0f0f0', font=('Arial', 20, 'bold'), foreground='#2c3e50')
        style.configure('TButton', font=('Arial', 12), padding=8)

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="HỆ THỐNG NHẬN DIỆN CHỈ TAY", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 20))

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        select_frame = ttk.Frame(left_frame)
        select_frame.grid(row=0, column=0, pady=(0, 20), sticky=(tk.W, tk.E))

        self.select_btn = ttk.Button(select_frame, text="📁 CHỌN ẢNH VÀ NHẬN DIỆN",
                                     command=self.select_and_recognize, width=30)
        self.select_btn.grid(row=0, column=0, padx=(0, 10))

        self.path_label = ttk.Label(select_frame, text="Chưa chọn ảnh nào",
                                    foreground="#7f8c8d", font=('Arial', 11))
        self.path_label.grid(row=1, column=0, pady=(10, 0), sticky=tk.W)

        result_frame = ttk.LabelFrame(left_frame, text="KẾT QUẢ NHẬN DIỆN", padding="15")
        result_frame.grid(row=1, column=0, pady=(0, 20), sticky=(tk.W, tk.E))

        self.result_var = tk.StringVar(value="🔄 Chưa có kết quả")
        result_display = tk.Label(result_frame, textvariable=self.result_var,
                                  font=('Arial', 18, 'bold'), foreground="#2c3e50",
                                  background='#ecf0f1', justify=tk.CENTER,
                                  wraplength=400, padx=20, pady=20,
                                  relief=tk.RIDGE, borderwidth=2)
        result_display.grid(row=0, column=0, pady=10)

        info_frame = ttk.LabelFrame(left_frame, text="THÔNG TIN CHI TIẾT", padding="15")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.info_text = tk.Text(info_frame, width=60, height=15, font=('Arial', 11),
                                 wrap=tk.WORD, state=tk.DISABLED, bg='#ffffff',
                                 relief=tk.FLAT, borderwidth=1, padx=15, pady=15)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        v_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=v_scrollbar.set)

        display_frame = ttk.LabelFrame(right_frame, text="XEM TRƯỚC ẢNH", padding="10")
        display_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.image_label = tk.Label(display_frame, bg="#2c3e50", width=50, height=30,
                                    relief=tk.SUNKEN, text="Chưa có ảnh")
        self.image_label.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

    def display_image(self, image):
        if image is None:
            return
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_resized = img_pil.resize((400, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo

    def select_and_recognize(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh bàn tay",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if self.original_image is None:
                messagebox.showerror("Lỗi", "Không thể đọc ảnh!")
                return
            self.display_image(self.original_image)
            self.path_label.configure(text=f"Đã chọn: {os.path.basename(file_path)}")
            self.recognize_palm(self.original_image)

    def recognize_palm(self, image):
        if image is None:
            messagebox.showwarning("Cảnh báo", "Không có ảnh để nhận diện!")
            return
        try:
            img_processed = cv2.resize(image, (60, 60))
            img_processed = img_processed.astype("float32") / 255.0
            img_processed = img_processed.reshape(1, 60 * 60)

            predictions = model.predict(img_processed, verbose=0)
            class_idx = np.argmax(predictions)
            predicted_name = class_names[class_idx]
            confidence = predictions[0][class_idx] * 100

            self.result_var.set(
                f"✅ NHẬN DIỆN THÀNH CÔNG!\n\nKết quả: {predicted_name}\nĐộ chính xác: {confidence:.2f}%")

            self.show_palm_info(predicted_name)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi nhận diện: {str(e)}")

    def show_palm_info(self, palm_name):
        info = palm_info.get(palm_name, [])
        self.info_text.configure(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"THÔNG TIN CHI TIẾT - {palm_name.upper()}\n\n", "title")
        self.info_text.tag_configure("title", font=('Arial', 14, 'bold'), foreground='#2980b9')
        for line in info:
            self.info_text.insert(tk.END, f"• {line}\n\n")
        self.info_text.configure(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = PalmRecognitionUI(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
