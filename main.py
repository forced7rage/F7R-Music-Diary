import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import logging
from statistics import mean

#НАСТРОЙКА ПАПОК
DATA_DIR = "data"
LOGS_DIR = "logs"
DATA_FILE = os.path.join(DATA_DIR, "tracks.json")
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

#ЛОГИРОВАНИЕ
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

#ИНИЦИАЛИЗАЦИЯ ФАЙЛА 
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)


def load_tracks():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки данных: {e}")
        return []


def save_tracks(tracks):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tracks, f, ensure_ascii=False, indent=4)
        logging.info("Данные успешно сохранены")
    except Exception as e:
        logging.error(f"Ошибка сохранения данных: {e}")


class MusicDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Музыкальный дневник")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        title = tk.Label(
            root,
            text="Музыкальный дневник",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)

        desc = tk.Label(
            root,
            text="Выберите действие:",
            font=("Arial", 12)
        )
        desc.pack(pady=10)

        btn_add = tk.Button(root, text="Добавить трек", width=25, command=self.open_add_window)
        btn_add.pack(pady=8)

        btn_playlist = tk.Button(root, text="Основной плейлист", width=25, command=self.open_playlist_window)
        btn_playlist.pack(pady=8)

        btn_log = tk.Button(root, text="Общий лог", width=25, command=self.open_log_window)
        btn_log.pack(pady=8)

        btn_stats = tk.Button(root, text="Статистика", width=25, command=self.open_stats_window)
        btn_stats.pack(pady=8)

        btn_exit = tk.Button(root, text="Выход", width=25, command=root.destroy)
        btn_exit.pack(pady=20)

        logging.info("Программа запущена")

    def open_add_window(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить трек")
        window.geometry("500x500")
        window.resizable(False, False)

        tk.Label(window, text="Название трека:").pack(pady=5)
        entry_title = tk.Entry(window, width=40)
        entry_title.pack()

        tk.Label(window, text="Исполнитель:").pack(pady=5)
        entry_artist = tk.Entry(window, width=40)
        entry_artist.pack()

        tk.Label(window, text="Жанр:").pack(pady=5)
        entry_genre = tk.Entry(window, width=40)
        entry_genre.pack()

        tk.Label(window, text="Настроение:").pack(pady=5)
        combo_mood = ttk.Combobox(
            window,
            values=["Весёлое", "Грустное", "Спокойное", "Энергичное", "Романтичное"],
            state="readonly",
            width=37
        )
        combo_mood.pack()

        tk.Label(window, text="Оценка (1-5):").pack(pady=5)
        combo_rating = ttk.Combobox(
            window,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            width=37
        )
        combo_rating.pack()

        tk.Label(window, text="Комментарий:").pack(pady=5)
        text_comment = tk.Text(window, width=40, height=6)
        text_comment.pack()

        def save_track():
            title = entry_title.get().strip()
            artist = entry_artist.get().strip()
            genre = entry_genre.get().strip()
            mood = combo_mood.get().strip()
            rating = combo_rating.get().strip()
            comment = text_comment.get("1.0", tk.END).strip()

            if not title:
                messagebox.showerror("Ошибка", "Введите название трека")
                logging.warning("Не введено название трека")
                return

            if not artist:
                messagebox.showerror("Ошибка", "Введите исполнителя")
                logging.warning("Не введён исполнитель")
                return

            if not rating:
                messagebox.showerror("Ошибка", "Выберите оценку")
                logging.warning("Не выбрана оценка")
                return

            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Оценка должна быть от 1 до 5")
                logging.warning("Некорректная оценка")
                return

            category = "Основной плейлист" if rating == 5 else "Лог дневника"

            new_track = {
                "title": title,
                "artist": artist,
                "genre": genre,
                "mood": mood,
                "rating": rating,
                "comment": comment,
                "category": category
            }

            tracks = load_tracks()
            tracks.append(new_track)
            save_tracks(tracks)

            logging.info(f"Добавлен трек: {title} - {artist}, оценка {rating}, категория: {category}")
            messagebox.showinfo("Успех", f"Трек сохранён!\nКатегория: {category}")

            entry_title.delete(0, tk.END)
            entry_artist.delete(0, tk.END)
            entry_genre.delete(0, tk.END)
            combo_mood.set("")
            combo_rating.set("")
            text_comment.delete("1.0", tk.END)

        tk.Button(window, text="Сохранить", width=20, command=save_track).pack(pady=15)

    def open_playlist_window(self):
        window = tk.Toplevel(self.root)
        window.title("Основной плейлист")
        window.geometry("700x400")

        text = tk.Text(window, wrap="word")
        text.pack(fill="both", expand=True)

        tracks = load_tracks()
        playlist_tracks = [track for track in tracks if track["category"] == "Основной плейлист"]

        if not playlist_tracks:
            text.insert(tk.END, "В основном плейлисте пока нет треков.")
        else:
            for i, track in enumerate(playlist_tracks, start=1):
                text.insert(
                    tk.END,
                    f"{i}. {track['title']} — {track['artist']}\n"
                    f"   Жанр: {track['genre']}\n"
                    f"   Настроение: {track['mood']}\n"
                    f"   Оценка: {track['rating']}\n"
                    f"   Комментарий: {track['comment']}\n\n"
                )

        logging.info("Открыто окно основного плейлиста")

    def open_log_window(self):
        window = tk.Toplevel(self.root)
        window.title("Общий лог")
        window.geometry("700x400")

        text = tk.Text(window, wrap="word")
        text.pack(fill="both", expand=True)

        tracks = load_tracks()
        log_tracks = [track for track in tracks if track["category"] == "Лог дневника"]

        if not log_tracks:
            text.insert(tk.END, "В общем логе пока нет записей.")
        else:
            for i, track in enumerate(log_tracks, start=1):
                text.insert(
                    tk.END,
                    f"{i}. {track['title']} — {track['artist']}\n"
                    f"   Жанр: {track['genre']}\n"
                    f"   Настроение: {track['mood']}\n"
                    f"   Оценка: {track['rating']}\n"
                    f"   Комментарий: {track['comment']}\n\n"
                )

        logging.info("Открыто окно общего лога")

    def open_stats_window(self):
        window = tk.Toplevel(self.root)
        window.title("Статистика")
        window.geometry("500x300")
        window.resizable(False, False)

        tracks = load_tracks()

        if not tracks:
            stats_text = "Пока нет данных для подсчёта статистики."
        else:
            all_count = len(tracks)
            playlist_count = len([t for t in tracks if t["category"] == "Основной плейлист"])
            log_count = len([t for t in tracks if t["category"] == "Лог дневника"])
            avg_rating = round(mean([t["rating"] for t in tracks]), 2)

            stats_text = (
                f"Всего треков: {all_count}\n\n"
                f"В основном плейлисте: {playlist_count}\n\n"
                f"В логе дневника: {log_count}\n\n"
                f"Средняя оценка: {avg_rating}"
            )

        label = tk.Label(window, text=stats_text, font=("Arial", 12), justify="left")
        label.pack(pady=40)

        logging.info("Открыто окно статистики")


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicDiaryApp(root)
    root.mainloop()
