import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
from tkinter import messagebox
from deepface import DeepFace

output_directory_cap = 'capturas'
output_directory_feat = 'caracteristicas'

# Crie os diretórios se eles não existirem
os.makedirs(output_directory_cap, exist_ok=True)
os.makedirs(output_directory_feat, exist_ok=True)

# Variáveis globais
ultimo_frame = None
cap = cv2.VideoCapture(0)  # Captura da webcam

# Função para capturar frames da webcam
def capturar_frame():
    global ultimo_frame
    ret, frame = cap.read()

    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ultimo_frame = Image.fromarray(frame)
        imagem = ImageTk.PhotoImage(ultimo_frame)
        label_cam["image"] = imagem
        label_cam.imagem = imagem
        label_cam.after(10, capturar_frame)

# Extrair características faciais
def extrair_caracteristicas_faciais(caminho_imagem):
    try:
        embedding = DeepFace.represent(caminho_imagem, model_name='Facenet')[0]["embedding"]
        return embedding
    except Exception as e:
        print(f"Erro ao extrair características: {e}")
        return None

# Salvar características em um arquivo
def salvar_caracteristicas(nome_arquivo, caracteristicas):
    caminho_completo = os.path.join(output_directory_feat, nome_arquivo)
    with open(caminho_completo, 'w') as arquivo:
        for valor in caracteristicas:
            arquivo.write(f"{valor}\n")
    print(f"Características salvas em {caminho_completo}")

# Pegar nome do usuário e capturar imagem
def capturar_imagem_com_nome():
    global ultimo_frame
    nome = pegar_nome()
    
    if nome:
        nome_arquivo_imagem = f"{nome}_comparar.png"
        nome_arquivo_caracteristicas = f"{nome}_caracteristicas.txt"
        caminho_imagem = os.path.join(output_directory_cap, nome_arquivo_imagem)
        
        if ultimo_frame is not None:
            ultimo_frame.save(caminho_imagem)

            # Extrair características faciais
            caracteristicas = extrair_caracteristicas_faciais(caminho_imagem)
            if caracteristicas is not None:
                salvar_caracteristicas(nome_arquivo_caracteristicas, caracteristicas)
                messagebox.showinfo("Sucesso", f"Imagem e características salvas para {nome}")
            else:
                messagebox.showerror("Erro", "Falha na extração de características.")
            botao_capturar["state"] = tk.DISABLED
        else:
            messagebox.showerror("Erro", "Nenhuma imagem capturada.")

#Pegar nome do usuario
def pegar_nome():
    nome_captura = campo_nome.get()
    if not nome_captura:
        messagebox.showerror("Erro", "Digite um nome de usuário válido.")
    return nome_captura

'''Interface gráfica'''

janela = tk.Tk()
janela.title("Captura de Webcam")

janela.columnconfigure(0, weight=1)
janela.rowconfigure(0, weight=1)

label_cam = tk.Label(janela)
label_cam.grid(row=0, column=0, sticky="nsew")

frame_direita = tk.Frame(janela)
frame_direita.grid(row=0, column=1, padx=10, pady=10)

label_nome = tk.Label(frame_direita, text="Nome:")
label_nome.grid(row=0, column=0)

campo_nome = tk.Entry(frame_direita)
campo_nome.grid(row=0, column=1)

botao_capturar = tk.Button(frame_direita, text="Capturar Imagem", command=capturar_imagem_com_nome)
botao_capturar.grid(row=1, columnspan=2)

capturar_frame()

janela.mainloop()

cap.release()
