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

    alfabeto = set(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.lower()))
    dicts = ['br-utf8.txt', 'palavras.txt']
    set_words = set()
    for n, dict_file in enumerate(dicts):
        with open(dict_file, 'r', encoding='utf-8') as file:
            dict_words = file.read().split()
        print(f"Palavras Brutas {n}:", len(dict_words))
        dict_words = [i.lower() for i in dict_words if len(alfabeto.union(remover_acentos(i.lower()))) == 26]
        print(f"Palavras Filtradas {n}:", len(dict_words))
        set_words.update(dict_words)
        print(f"Conjunto total {n}:", len(set_words))
    words = list(set_words)
    new_file = []
    print('\n\r')
    for word_count, word in enumerate(words):
        print("Processando palavra", word_count, "de", len(words), end='\r', flush=True)
        vec = model.get_word_vector(word)
        clean_word = remover_acentos(word).lower() #Torna letras maiúsculas o padrão
        tem_letra = np.zeros(26, dtype=np.float64)
        for char in clean_word:
            try:
                index = ord(char)-ord('a')
                if index < 0:
                    raise IndexError("Caractere negativo")
                tem_letra[index] = 1.0
            except IndexError:
                print("\n", char, word, clean_word)
                raise ValueError("Caracter não alfabético encontrado")
        new_file.append((clean_word, word, vec, tem_letra))

    with open("AllWordsProcessed.pkl", "wb") as f:
        print("Salvando Arquivo")
        pickle.dump(new_file, f)
        print("Arquivo Salvo")
    # if __name__ == '__main__':
    #     print(new_file)

if __name__ == '__main__':
    main()