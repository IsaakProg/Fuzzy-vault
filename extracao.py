import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
import random
import hashlib
from numpy.polynomial import Polynomial
from deepface import DeepFace
from tkinter import messagebox

# Diretórios para armazenamento de capturas e características
output_directory_cap = 'capturas'
output_directory_feat = 'caracteristicas'

# Crie os diretórios se eles não existirem
os.makedirs(output_directory_cap, exist_ok=True)
os.makedirs(output_directory_feat, exist_ok=True)

# Variáveis globais
ultimo_frame = None
cap = cv2.VideoCapture(0)  # Captura da webcam

# Função para quantizar o vetor de recursos
def quantize(vector):
    return np.round(vector * 100).astype(int)

# Função para binarizar o vetor quantizado
def binarize(vector):
    return np.array([format(v, 'b') for v in vector])

# Função para mapear o vetor binário para um conjunto de índices de 1s
def map_to_feature_set(binary_vector):
    feature_set = set()
    for i, bit_str in enumerate(binary_vector):
        for j, bit in enumerate(bit_str):
            if bit == '1':
                feature_set.add(i * len(bit_str) + j)
    return feature_set

# Função para gerar um polinômio secreto
def generate_secret_polynomial(degree, coef_range):
    return Polynomial([random.randint(*coef_range) for _ in range(degree + 1)])

# Função para calcular o hash do polinômio
def hash_polynomial(poly):
    return hashlib.sha256(str(poly).encode()).hexdigest()

# Função para criar o Fuzzy Vault
def create_vault(feature_set, secret_poly):
    vault = {}
    for x in feature_set:
        y = secret_poly(x)
        vault[x] = y
    return vault

# Função para reconstruir o polinômio usando a estratégia Reed-Solomon
def polynomial_reconstruction(vault, feature_set, degree):
    common_features = set(vault.keys()).intersection(feature_set)
    if len(common_features) < degree + 1:
        return None  # Não é possível recuperar a chave
    x = np.array(list(common_features))
    y = np.array([vault[xx] for xx in x])
    recovered_poly = Polynomial.fit(x, y, degree)
    return recovered_poly

# Função para liberar a chave
def key_release(recovered_poly):
    return hash_polynomial(recovered_poly)

# Função para capturar frames da webcam
def capturar_frame():
    global ultimo_frame
    ret, frame = cap.read()

    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ultimo_frame = Image.fromarray(frame)
        imagem = ImageTk.PhotoImage(ultimo_frame)
        label_cam["image"] = imagem
        label_cam.imagem = imagem  # Evitar coleta de lixo
        label_cam.after(10, capturar_frame)

# Extrair características faciais
def extrair_caracteristicas_faciais(caminho_imagem):
    try:
        embedding = DeepFace.represent(caminho_imagem, model_name='Facenet')[0]["embedding"]
        return embedding
    except Exception as e:
        print(f"Erro ao extrair características: {e}")
        return None
    
def calcular_distancia_euclidiana(vetor1, vetor2):
    return np.sqrt(np.sum((vetor1 - vetor2) ** 2))

# ...
def capturar_imagem_com_nome():
    global ultimo_frame
    nome = pegar_nome()
    
    if nome:
        nome_arquivo_imagem = f"{nome}_comparar.png"
        caminho_imagem = os.path.join(output_directory_cap, nome_arquivo_imagem)
        
        if ultimo_frame is not None:
            ultimo_frame.save(caminho_imagem)
            messagebox.showinfo("Informação", "Imagem capturada com sucesso!")

            caracteristicas = extrair_caracteristicas_faciais(caminho_imagem)
            if caracteristicas is not None:
                nome_arquivo_original = f"{nome}_original.txt"
                caminho_original = os.path.join(output_directory_feat, nome_arquivo_original)

                if os.path.exists(caminho_original):
                    with open(caminho_original, 'r') as arquivo:
                        caracteristicas_originais = np.array([float(linha.strip()) for linha in arquivo.readlines()])
                    distancia = calcular_distancia_euclidiana(caracteristicas_originais, np.array(caracteristicas))
                    messagebox.showinfo("Resultado da Comparação", f"Distância Euclidiana: {distancia}")
                    imprimir_dados_fuzzy_vault(caracteristicas)
                else:
                    with open(caminho_original, 'w') as arquivo:
                        for valor in caracteristicas:
                            arquivo.write(f"{valor}\n")
                    messagebox.showinfo("Informação", "Dados originais salvos.")
            else:
                messagebox.showerror("Erro", "Falha na extração de características.")
            botao_capturar["state"] = tk.DISABLED
        else:
            messagebox.showerror("Erro", "Nenhuma imagem capturada.")

def imprimir_dados_fuzzy_vault(caracteristicas):
    quantized_vector = quantize(np.array(caracteristicas))
    binary_vector = binarize(quantized_vector)
    feature_set = map_to_feature_set(binary_vector)

    secret_poly = generate_secret_polynomial(3, (-10, 10))
    vault = create_vault(feature_set, secret_poly)
    recovered_poly = polynomial_reconstruction(vault, feature_set, 3)
    released_key = key_release(recovered_poly)

    print(f"Quantized Vector: {quantized_vector}")
    print(f"Binary Vector: {binary_vector}")
    print(f"Feature Set: {feature_set}")
    print(f"Secret Polynomial: {secret_poly}")
    print(f"Secret Hash: {hash_polynomial(secret_poly)}")
    print(f"Vault: {vault}")
    print(f"Recovered Polynomial: {recovered_poly}")
    print(f"Released Key: {released_key}")

def comparar_caracteristicas():
    global ultimo_frame
    nome = pegar_nome()

    if nome:
        nome_arquivo_imagem = f"{nome}_comparar.png"
        caminho_imagem = os.path.join(output_directory_cap, nome_arquivo_imagem)

        if ultimo_frame is not None:
            ultimo_frame.save(caminho_imagem)

            caracteristicas = extrair_caracteristicas_faciais(caminho_imagem)
            if caracteristicas is not None:
                nome_arquivo_original = f"{nome}_original.txt"
                caminho_original = os.path.join(output_directory_feat, nome_arquivo_original)

                if os.path.exists(caminho_original):
                    with open(caminho_original, 'r') as arquivo:
                        caracteristicas_originais = np.array([float(linha.strip()) for linha in arquivo.readlines()])
                    distancia = calcular_distancia_euclidiana(caracteristicas_originais, np.array(caracteristicas))
                    messagebox.showinfo("Resultado da Comparação", f"Distância Euclidiana: {distancia}")
                else:
                    messagebox.showerror("Erro", "Dados originais não encontrados. Capture a imagem inicial primeiro.")
            else:
                messagebox.showerror("Erro", "Falha na extração de características.")
        else:
            messagebox.showerror("Erro", "Nenhuma imagem capturada.")


# Pegar nome do usuário
def pegar_nome():
    nome_captura = campo_nome.get()
    if not nome_captura:
        messagebox.showerror("Erro", "Digite um nome de usuário válido.")
    return nome_captura

# Interface gráfica
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

botao_comparar = tk.Button(frame_direita, text="Comparar", command=comparar_caracteristicas)
botao_comparar.grid(row=2, columnspan=2)

capturar_frame()

janela.mainloop()

cap.release()
