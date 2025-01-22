# manager_gui.py

import os
import subprocess
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import shutil  # <--- Adicione este import para mover/deletar arquivos
import webbrowser  # <--- para abrir links no navegador

current_process = None  # Para controlar se temos um processo em execução
root = tk.Tk()
root.title("HunYuan Dataset Creator by leal.cc")
root.configure(bg="#F0F0F0")
root.minsize(650, 500)

style = ttk.Style(root)
style.theme_use("xpnative")
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10), padding=6)

folder_var = tk.StringVar()
snippet_var = tk.IntVar(value=2)
btn_text_var = tk.StringVar(value="Start Processing")

def select_folder():
    folder_selected = filedialog.askdirectory(title="Select Folder for Processing")
    folder_var.set(folder_selected)

def toggle_process():
    global current_process
    if current_process is not None and current_process.poll() is None:
        # Se houver processo em execução, interrompe
        current_process.terminate()
        current_process = None
        btn_text_var.set("Start Processing")
        return

    folder_path = folder_var.get().strip()
    snippet_duration = snippet_var.get()
    prompt_text = caption_text.get("1.0", tk.END).strip()

    if not folder_path:
        messagebox.showerror("Error", "Please select a folder")
        return

    # Armazena prompt para uso no joyCaption (se necessário)
    os.environ["JOY_CAPTION_PROMPT"] = prompt_text if prompt_text else " "

    # Limpa a saída
    output_text.delete('1.0', tk.END)

    btn_text_var.set("Stop Processing")
    start_process(folder_path, snippet_duration)

def start_process(folder_path, snippet_duration):
    global current_process

    env = os.environ.copy()
    python_executable = sys.executable

    current_process = subprocess.Popen(
        [python_executable, "videoSplit.py", folder_path, str(snippet_duration)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    def read_output():
        if current_process is None:
            return

        line = current_process.stdout.readline()
        if line:
            output_text.insert(tk.END, line)
            output_text.see(tk.END)

        if current_process.poll() is None:
            # ainda rodando, continua lendo
            root.after(50, read_output)
        else:
            # processo finalizado
            retcode = current_process.returncode
            if btn_text_var.get() == "Stop Processing":
                btn_text_var.set("Start Processing")

            if retcode == 0:
                # Tudo certo: vamos mover os arquivos e apagar grids
                move_results_and_cleanup(folder_path)
                messagebox.showinfo("Success", "Processing complete. Happy Training!")
            else:
                # Retorno pode ser -15 se o usuário clicou em Stop
                if retcode not in (-15, None):
                    messagebox.showerror("Error", f"An error occurred. Return code: {retcode}")

    read_output()

def move_results_and_cleanup(folder_path):
    """
    Exemplo de função que:
      1) Cria final_outputs dentro de folder_path.
      2) Move .txt (legendas) de grids/ para final_outputs.
      3) Move .mp4 dos snippets/ para final_outputs (opcional).
      4) Remove a pasta grids/.
      5) (Opcional) Remove a pasta snippets/, se desejar.
    """
    final_dir = os.path.join(folder_path, "final_outputs")
    os.makedirs(final_dir, exist_ok=True)

    # 1) Mover arquivos .txt da pasta "grids"
    grids_dir = os.path.join(folder_path, "grids")
    if os.path.isdir(grids_dir):
        for fname in os.listdir(grids_dir):
            if fname.lower().endswith(".txt"):
                src_path = os.path.join(grids_dir, fname)
                dst_path = os.path.join(final_dir, fname)
                shutil.move(src_path, dst_path)
        # Deleta a pasta "grids"
        shutil.rmtree(grids_dir, ignore_errors=True)

    # 2) Mover arquivos .mp4 (snippets) da pasta "snippets"
    snippets_dir = os.path.join(folder_path, "snippets")
    if os.path.isdir(snippets_dir):
        for root_dir, dirs, files in os.walk(snippets_dir):
            for fname in files:
                # Ajuste extensões conforme o que deseja mover
                if fname.lower().endswith(".mp4"):
                    src_path = os.path.join(root_dir, fname)
                    dst_path = os.path.join(final_dir, fname)
                    shutil.move(src_path, dst_path)
        # Se você quiser remover totalmente a pasta 'snippets', descomente:
        shutil.rmtree(snippets_dir, ignore_errors=True)

# ------------------ Layout Tkinter ------------------

frame_top = ttk.LabelFrame(root, text="Select Folder", padding=10)
frame_top.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

ttk.Label(frame_top, text="Folder Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(frame_top, textvariable=folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(frame_top, text="Browse", command=select_folder).grid(row=0, column=2, padx=5, pady=5)

frame_mid = ttk.LabelFrame(root, text="Settings", padding=10)
frame_mid.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")

ttk.Label(frame_mid, text="Caption Prompt (Optional):").grid(row=0, column=0, sticky="nw", padx=5, pady=5)
caption_text = tk.Text(frame_mid, width=60, height=4)
caption_text.grid(row=0, column=1, sticky="w", padx=5, pady=5)

ttk.Label(frame_mid, text="Snippet Duration (seconds):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
ttk.Spinbox(frame_mid, from_=1, to=60, textvariable=snippet_var, width=5).grid(row=1, column=1, sticky="w", padx=5, pady=5)

frame_out = ttk.LabelFrame(root, text="Command Output", padding=10)
frame_out.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

output_text = ScrolledText(frame_out, wrap=tk.WORD, width=70, height=5)
output_text.pack(fill="both", expand=True)

frame_bottom = ttk.Frame(root)
frame_bottom.grid(row=3, column=0, pady=10)

btn_start_stop = ttk.Button(frame_bottom, textvariable=btn_text_var, command=toggle_process, width=18)
btn_start_stop.pack()

# ------- Frame de Agradecimento e Doação -------
def open_donation_link():
    webbrowser.open("https://buymeacoffee.com/leal.cc")  # substitua pela URL real

thank_you_frame = ttk.Frame(root)
thank_you_frame.grid(row=4, column=0, pady=(5,15))

thank_you_label = ttk.Label(
    thank_you_frame,
    text="I need your support to survive! Please consider buying me a coffee."
)
thank_you_label.pack(side="left", padx=5)

donate_button = ttk.Button(
    thank_you_frame,
    text="Donate",
    command=open_donation_link
)
donate_button.pack(side="left", padx=5)

root.mainloop()
