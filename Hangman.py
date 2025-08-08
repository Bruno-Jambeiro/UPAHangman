import pickle
import numpy as np


class ThemeError(ValueError):
    pass
class FilterError(ValueError):
    pass
def cosine(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

class HangmanSolver:
    def __init__(self):
        self.working_data_full = None #Todas as palavras com o tamanho certo
        self.negative_chars = None
        #self.working_data_raw = None
        self.chars_guessed = None
        self.theme_vec = None
        self.guess = None
        self.theme = None
        self.working_data = None
        #self.minimum_similarity = 0.15
        with open("AllWordsProcessed.pkl", "rb") as f:
            self.data_full = pickle.load(f) #Todas as palavras de todos os tamanhos


    def new_game(self, theme: str, word_size:int):
        theme = theme.upper()
        working_data_raw = [i for i in self.data_full if len(i[0]) == word_size]
        print(f"Conjunto de palavras com {word_size} letras: {len(working_data_raw)}")
        self.theme = theme
        self.theme_vec = next((t[2] for t in self.data_full if t[1].upper() == theme.upper()), None)
        if self.theme_vec is None:
            import fasttext
            model = fasttext.load_model('cc.pt.300.bin')
            self.theme_vec = model.get_sentence_vector(theme)

        self.guess = "*" * word_size
        self.chars_guessed = np.ones(26, dtype=np.float64)
        self.negative_chars = np.zeros(26, dtype=bool)
        #self.working_data = [(i[0], i[1], cosine(i[2], self.theme_vec), i[3]) for i in working_data_raw if cosine(i[2], self.theme_vec) > self.minimum_similarity]
        self.working_data_full = [(i[0], i[1], cosine(i[2], self.theme_vec), i[3]) for i in working_data_raw]
        self.working_data = self.working_data_full[:]
        self.working_data.sort(key=lambda x: x[2], reverse=True)
        self.working_data = self.working_data[:(len(self.working_data) + 9)//10]

        print(f"Conjunto de palavras após filtragem temática: {len(self.working_data)}")

    def make_guess(self):
        contador_letras = np.zeros(26, dtype=np.float64)
        for word in self.working_data:
            temp = word[3] * word[2]
            contador_letras+= temp
        contador_letras = contador_letras * self.chars_guessed
        self.chars_guessed[np.argmax(contador_letras)] = -1.0
        return chr(ord('A') + np.argmax(contador_letras))

    def __match_word_guess(self, word):
        match = True
        for i, char in enumerate(word):
            if self.guess[i] == '*': continue
            if char != self.guess[i]:
                match = False
                break
        return match

    def __add_more_words(self):
        print("Buscando Possibilidades")
        self.working_data = self.working_data_full
        print("Filtrando Novas possibilidades")
        self.filter_positive(self.guess)
        for i, v in enumerate(self.negative_chars):
            if not v : continue
            self.filter_negative(chr(ord('A') + i))

    def filter_positive(self, new_guess):
        #Ve quais letras ja foram confirmadas e filtra de acordo
        if len(new_guess) != len(self.guess):
            raise FilterError("Tamanho errado")
        self.guess = "".join((e if e != '*' else new_guess[i]) for i, e in enumerate(self.guess))
        self.working_data = [i for i in self.working_data if self.__match_word_guess(i[0])]
        print(f"Palavras restantes: {len(self.working_data)}")

        if len(self.working_data) == 0:
            self.__add_more_words()



    def filter_negative(self, char):
        #Em caso de um chute errado elimina as palavras com a letra char
        index = ord(char) - ord('A')
        self.negative_chars[index] = True
        self.working_data = [i for i in self.working_data if not i[3][index]]
        print(f"Palavras restantes: {len(self.working_data)}")
        if len(self.working_data) == 0:
            self.__add_more_words()
