import fasttext.util
import fasttext
import numpy as np

# 1. Baixa o modelo em português, se ainda não estiver presente
fasttext.util.download_model('pt', if_exists='ignore')
model = fasttext.load_model('cc.pt.300.bin')

# Função de similaridade do cosseno
def cosine(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

# 2. Similaridade entre duas palavras
vec_apple = model.get_word_vector("maçã")
vec_banana = model.get_word_vector("banana")
sim = cosine(vec_apple, vec_banana)
print(f"Similaridade(maçã, banana) = {sim:.4f}")

# 3. Ranking de um vocabulário customizado em português
vocab = ["maçã", "banana", "carro", "caminhão", "fruta", "amor", "Chimpanzé", "mão", "axila"]
target = "Corpo Humano".upper()

target_vec = model.get_sentence_vector(target)

scores = [(w, cosine(target_vec, model.get_word_vector(w))) for w in vocab]
ranked = sorted(scores, key=lambda x: x[1], reverse=True)

print(f"\nPalavras ranqueadas por similaridade com '{target}':")
for word, score in ranked:
    print(f"  {word:7s} → {score:.4f}")
