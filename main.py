import customtkinter as ctk
from Hangman import HangmanSolver  # Importa a classe HangmanSolver

ctk.set_appearance_mode("Dark")  # Modo de aparência: "dark" ou "light"
class HangmanAdivinhadorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Adivinhador de Forca")
        self.geometry(f"{1100}x{580}")

        # Configure grid columns to expand and center widgets
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Larger widget and JetBrains Mono font sizes
        entry_width = 350
        button_width = 200
        label_font = ("JetBrains Mono", 28)
        entry_font = ("JetBrains Mono", 24)
        button_font = ("JetBrains Mono", 24)
        mensagem_font = ("JetBrains Mono", 22)

        # Nova label de instrução
        self.instrucao_label = ctk.CTkLabel(self, text="Pense em uma palavra", font=label_font)
        self.instrucao_label.grid(row=0, column=0, columnspan=2, pady=(30, 10))

        self.tema_label = ctk.CTkLabel(self, text="Tema:", font=label_font)
        self.tema_entry = ctk.CTkEntry(self, width=entry_width, font=entry_font)
        self.tamanho_label = ctk.CTkLabel(self, text="Tamanho da palavra:", font=label_font)
        self.tamanho_entry = ctk.CTkEntry(self, width=entry_width, font=entry_font)
        self.iniciar_button = ctk.CTkButton(self, text="Iniciar", command=self.iniciar_jogo, width=button_width, height=60, font=button_font)
        self.novo_jogo_button = ctk.CTkButton(self, text="Novo Jogo", command=self.novo_jogo, width=button_width, height=60, font=button_font)
        self.novo_jogo_button.grid(row=8, column=0, columnspan=2, pady=20)
        self.novo_jogo_button.grid_remove()  # Hide initially

        self.suposicao_label = ctk.CTkLabel(self, text="", font=label_font)
        self.letra_label = ctk.CTkLabel(self, text="", font=label_font)

        # Frame and list for individual letter entries
        self.letra_entries_frame = ctk.CTkFrame(self)
        self.letra_entries = []

        self.submeter_button = ctk.CTkButton(self, text="Submeter", command=self.processar_resposta, width=button_width, height=60, font=button_font)
        self.nao_tem_button = ctk.CTkButton(self, text="Não tem", command=self.processar_nao_tem, width=button_width, height=60, font=button_font)

        self.mensagem_label = ctk.CTkLabel(self, text="", font=mensagem_font)

        # Canvas for stick figure
        self.hangman_canvas = ctk.CTkCanvas(self, width=220, height=320, bg="#242424", highlightthickness=0)
        self.hangman_canvas.grid(row=0, column=2, rowspan=8, padx=30, pady=30)
        self.erros = 0

        # Layout (atualize os índices das linhas para acomodar a nova label)
        self.tema_label.grid(row=1, column=0, padx=20, pady=20)
        self.tema_entry.grid(row=1, column=1, padx=20, pady=20)
        self.tamanho_label.grid(row=2, column=0, padx=20, pady=20)
        self.tamanho_entry.grid(row=2, column=1, padx=20, pady=20)
        self.iniciar_button.grid(row=3, column=0, columnspan=2, pady=20)
        self.instrucao_label.grid()  # Always show with theme/size

        self.suposicao_label.grid(row=4, column=0, columnspan=2, pady=20)
        self.letra_label.grid(row=5, column=0, columnspan=2, pady=20)
        self.letra_entries_frame.grid(row=6, column=0, columnspan=2, pady=20)
        self.letra_entries_frame.grid_remove()
        self.submeter_button.grid(row=7, column=0, pady=20)
        self.submeter_button.grid_remove()
        self.nao_tem_button.grid(row=7, column=1, pady=20)
        self.nao_tem_button.grid_remove()
        self.mensagem_label.grid(row=8, column=0, columnspan=2, pady=20)
        self.novo_jogo_button.grid(row=9, column=0, columnspan=2, pady=20)
        self.novo_jogo_button.grid_remove()  # Hide initially

        # Variáveis do jogo
        self.solver = None
        self.suposicao_atual = []
        self.letra_atual = ""

    def iniciar_jogo(self):
        """Inicia o jogo com o tema e tamanho fornecidos pelo jogador."""
        tema = self.tema_entry.get().strip().upper()
        try:
            tamanho = int(self.tamanho_entry.get().strip())
        except ValueError:
            self.mensagem_label.configure(text="Tamanho deve ser um número.")
            return

        # Hide theme, size, and iniciar button together
        self.instrucao_label.grid_remove()
        self.tema_label.grid_remove()
        self.tema_entry.grid_remove()
        self.tamanho_label.grid_remove()
        self.tamanho_entry.grid_remove()
        self.iniciar_button.grid_remove()
        self.novo_jogo_button.grid()  # Show "Novo Jogo" button

        # Show submeter button and posicoes_entry
        self.submeter_button.grid()
        self.nao_tem_button.grid()
        self.letra_entries_frame.grid()
        self.criar_letra_entries(tamanho)

        self.solver = HangmanSolver()
        self.solver.new_game(tema, tamanho)  # Inicializa o solver com tema e tamanho
        self.suposicao_atual = ["*"] * tamanho  # Suposição inicial com asteriscos
        self.suposicao_label.configure(text=" ".join(self.suposicao_atual))
        self.fazer_suposicao()
        self.erros = 0
        self.hangman_canvas.delete("all")
        self.desenhar_forca()

    def criar_letra_entries(self, tamanho):
        # Remove previous entries
        for widget in self.letra_entries_frame.winfo_children():
            widget.destroy()
        self.letra_entries = []
        for i in range(tamanho):
            entry = ctk.CTkEntry(self.letra_entries_frame, width=60, font=("JetBrains Mono", 24), justify="center")
            entry.grid(row=0, column=i, padx=5)
            self.letra_entries.append(entry)

    def fazer_suposicao(self):
        """Faz a próxima suposição de letra usando o HangmanSolver."""
        if self.solver:
            self.letra_atual = self.solver.make_guess()  # Obtém a próxima letra
            self.letra_label.configure(text=f"Adivinhando a letra: {self.letra_atual}")
            # Não apague os campos, mantenha o conteúdo para o usuário ver o progresso
            self.mensagem_label.configure(text="Digite a letra sugerida nas posições corretas ou deixe vazio.")

    def processar_resposta(self):
        """Processa a resposta do jogador e atualiza o jogo."""
        posicoes = []
        for idx, entry in enumerate(self.letra_entries):
            valor = entry.get().strip().upper()
            # Só verifica campos que ainda não foram preenchidos
            if self.suposicao_atual[idx] == "*":
                if valor == self.letra_atual:
                    posicoes.append(idx)
                elif valor != "":
                    self.mensagem_label.configure(text="Só insira a letra sugerida ou deixe vazio nos campos vazios.")
                    return
            # Se já preenchido, ignora o campo

        if posicoes:
            for pos in posicoes:
                self.suposicao_atual[pos] = self.letra_atual
                self.letra_entries[pos].delete(0, "end")
                self.letra_entries[pos].insert(0, self.letra_atual)
            self.solver.filter_positive("".join(self.suposicao_atual))
        else:
            self.solver.filter_negative(self.letra_atual)
            self.erros += 1
            self.atualizar_desenho_forca()

        self.suposicao_label.configure(text=" ".join(self.suposicao_atual))
        if "*" not in self.suposicao_atual:
            self.mensagem_label.configure(text="Adivinhei a palavra!")
            self.submeter_button.configure(state="disabled")
            self.nao_tem_button.configure(state="disabled")
        else:
            self.fazer_suposicao()

    def processar_nao_tem(self):
        """Processa o caso em que a letra não está na palavra."""
        self.solver.filter_negative(self.letra_atual)
        self.erros += 1
        self.atualizar_desenho_forca()
        self.suposicao_label.configure(text=" ".join(self.suposicao_atual))
        if "*" not in self.suposicao_atual:
            self.mensagem_label.configure(text="Adivinhei a palavra!")
            self.submeter_button.configure(state="disabled")
            self.nao_tem_button.configure(state="disabled")
        else:
            self.fazer_suposicao()

    def novo_jogo(self):
        """Reseta o estado e mostra opções de tema/tamanho."""
        # Show theme, size, and iniciar button together
        self.instrucao_label.grid()
        self.tema_label.grid()
        self.tema_entry.grid()
        self.tamanho_label.grid()
        self.tamanho_entry.grid()
        self.iniciar_button.grid()
        self.novo_jogo_button.grid_remove()
        self.submeter_button.grid_remove()
        self.nao_tem_button.grid_remove()
        self.letra_entries_frame.grid_remove()
        self.suposicao_label.configure(text="")
        self.letra_label.configure(text="")
        for entry in self.letra_entries:
            entry.delete(0, "end")
        self.mensagem_label.configure(text="")
        self.submeter_button.configure(state="normal")
        self.nao_tem_button.configure(state="normal")
        self.solver = None
        self.suposicao_atual = []
        self.letra_atual = ""
        self.letra_entries = []
        self.erros = 0
        self.hangman_canvas.delete("all")
        self.instrucao_label.grid()  # Show instruction label again

    def desenhar_forca(self):
        """Desenha a estrutura da forca."""
        c = self.hangman_canvas
        # Base
        c.create_line(20, 300, 200, 300, width=6, fill="#eee")
        # Poste
        c.create_line(60, 300, 60, 40, width=6, fill="#eee")
        # Viga superior
        c.create_line(60, 40, 160, 40, width=6, fill="#eee")
        # Corda
        c.create_line(160, 40, 160, 80, width=4, fill="#eee")

    def atualizar_desenho_forca(self):
        """Desenha partes do boneco conforme o número de erros."""
        self.desenhar_forca()
        c = self.hangman_canvas
        # Cabeça
        if self.erros >= 1:
            c.create_oval(135, 80, 185, 130, width=4, outline="#eee")
        # Corpo
        if self.erros >= 2:
            c.create_line(160, 130, 160, 210, width=4, fill="#eee")
        # Braço esquerdo
        if self.erros >= 3:
            c.create_line(160, 150, 120, 180, width=4, fill="#eee")
        # Braço direito
        if self.erros >= 4:
            c.create_line(160, 150, 200, 180, width=4, fill="#eee")
        # Perna esquerda
        if self.erros >= 5:
            c.create_line(160, 210, 130, 260, width=4, fill="#eee")
        # Perna direita
        if self.erros >= 6:
            c.create_line(160, 210, 190, 260, width=4, fill="#eee")
        # Olhos (game over)
        if self.erros >= 7:
            c.create_line(145, 95, 155, 105, width=2, fill="#eee")
            c.create_line(155, 95, 145, 105, width=2, fill="#eee")
            c.create_line(165, 95, 175, 105, width=2, fill="#eee")
            c.create_line(175, 95, 165, 105, width=2, fill="#eee")
            self.mensagem_label.configure(text="Você perdeu! Tente novamente.")
            self.submeter_button.configure(state="disabled")
            self.nao_tem_button.configure(state="disabled")

if __name__ == "__main__":
    app = HangmanAdivinhadorUI()
    app.mainloop()