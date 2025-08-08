import fasttext.util
import fasttext
import unicodedata
import pickle
import numpy as np

def remover_acentos(texto: str) -> str:
    # Normaliza para decompor acentos e depois filtra os combinantes
    nfkd = unicodedata.normalize('NFD', texto)
    return ''.join(
        c for c in nfkd
        if unicodedata.category(c) != 'Mn'
    )

def main():
    # 1. Baixa o modelo em português, se ainda não estiver presente
    fasttext.util.download_model('pt', if_exists='ignore')
    model = fasttext.load_model('cc.pt.300.bin')


    with open('br-utf8.txt', 'r', encoding='utf-8') as file:
        raw_text = file.read()
        words = raw_text.split()
    words = [i.upper() for i in words]
    new_file = []
    for word_count, word in enumerate(words):
        print("Processando palavra", word_count, "de", len(words), end='\r')
        vec = model.get_word_vector(word)
        clean_word = remover_acentos(word).upper() #Torna letras maiúsculas o padrão
        tem_letra = np.zeros(26, dtype=np.float64)
        for char in clean_word:
            try:
                tem_letra[ord(char)-ord('A')] = 1.0
            except IndexError:
                print(char, word, clean_word)
                exit(-1)
        new_file.append((clean_word, word, vec, tem_letra))

    with open("AllWordsProcessed.pkl", "wb") as f:
        pickle.dump(new_file, f)
    if __name__ == '__main__':
        print(new_file)

if __name__ == '__main__':
    main()