import numpy as np
import random
import hashlib
from numpy.polynomial import Polynomial
from sympy import symbols, solve

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

# Exemplo de uso
if __name__ == "__main__":
    # Vetor de recursos de exemplo
    feature_vector = np.array([0.1, 0.5, 0.9, -0.4, -0.2])

    # Etapa de quantização
    quantized_vector = quantize(feature_vector)
    print(f"Quantized Vector: {quantized_vector}")

    # Etapa de binarização
    binary_vector = binarize(quantized_vector)
    print(f"Binary Vector: {binary_vector}")

    # Mapeamento para o conjunto de índices de 1s
    feature_set = map_to_feature_set(binary_vector)
    print(f"Feature Set: {feature_set}")

    # Geração do polinômio secreto
    secret_poly = generate_secret_polynomial(3, (-10, 10))
    print(f"Secret Polynomial: {secret_poly}")

    # Hash do polinômio secreto
    secret_hash = hash_polynomial(secret_poly)
    print(f"Secret Hash: {secret_hash}")

    # Criação do Fuzzy Vault
    vault = create_vault(feature_set, secret_poly)
    print(f"Vault: {vault}")

    # Reconstrução do polinômio
    recovered_poly = polynomial_reconstruction(vault, feature_set, 3)
    print(f"Recovered Polynomial: {recovered_poly}")

    # Liberação da chave
    released_key = key_release(recovered_poly)
    print(f"Released Key: {released_key}")
