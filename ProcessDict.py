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
        part_1_words = raw_text.split()
    part_1_words = [i.upper() for i in part_1_words]
    print(f"Primeiro Dicionário: {len(part_1_words)}")
    set_words = set(part_1_words)
    print(f"Primeiro Conjunto: {len(set_words)}")
    with open('palavras.txt', 'r', encoding='utf-8') as file:
        raw_text = file.read()
        part_2_words = raw_text.split()
    part_2_words = [i.upper() for i in part_2_words]
    #set_words.update(set(part_2_words))
    print(f"Segundo Dicionário: {len(part_2_words)}")
    words = list(set_words)
    words.sort()
    print(f"Total Dicionário: {len(words)}")
    new_file = []
    for word_count, word in enumerate(words):
        print("Processando palavra", word_count, "de", len(words), end='\r', flush=True)
        vec = model.get_word_vector(word)
        clean_word = remover_acentos(word).upper() #Torna letras maiúsculas o padrão
        tem_letra = np.zeros(26, dtype=np.float64)
        for char in clean_word:
            try:
                tem_letra[ord(char)-ord('A')] = 1.0
            except IndexError:
                print("\n", char, word, clean_word)
                #exit(-1)
        new_file.append((clean_word, word, vec, tem_letra))

    with open("AllWordsProcessed.pkl", "wb") as f:
        print("Salvando Arquivo")
        pickle.dump(new_file, f)
        print("Arquivo Salvo")
    if __name__ == '__main__':
        print(new_file)

if __name__ == '__main__':
    main()