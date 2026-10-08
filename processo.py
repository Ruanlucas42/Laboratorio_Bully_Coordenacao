import socket
import threading
import sys
import time
from datetime import datetime

from config import PROCESSOS


class Processo:
    def __init__(self, id_processo):
        self.id = id_processo
        self.host, self.porta = PROCESSOS[self.id]
        self.coordenador = None
        self.ativo = True
        self.elegivel = True
        self.eleicao_em_andamento = False
        self.eventos_eleicao = []
        self.iniciador_eleicao = None
        self.montando_diagrama = False
        self.lock_diagrama = threading.RLock()

    def log(self, mensagem):
        horario = datetime.now().strftime("%H:%M:%S")
        print(f"[{horario}] {mensagem}")
        with self.lock_diagrama:
            if self.iniciador_eleicao is not None:
                self.eventos_eleicao.append(f"[{horario}] {mensagem}")

    def apresentar_diagrama(self):
        with self.lock_diagrama:
            if not self.eventos_eleicao:
                return
            linhas = [
                "\n+--- DIAGRAMA TEXTUAL DA ELEIÇÃO ---",
                f"| Visão local do processo P{self.id}",
                f"| Iniciador desta eleição local: P{self.iniciador_eleicao}",
                "|",
            ]
            for evento in self.eventos_eleicao:
                linhas.extend([f"|  {evento}", "|    |", "|    v"])
            if self.coordenador is None:
                linhas.append("| Aguardando anúncio do vencedor (COORDINATOR)")
            else:
                linhas.append(f"| Vencedor: P{self.coordenador}")
            linhas.append("+---------------------------------\n")
            print("\n".join(linhas))

    def iniciar_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((self.host, self.porta))
        servidor.listen()

        print(f"[P{self.id}] aguardando conexões na porta {self.porta}")

        while self.ativo:
            try:
                conexao, endereco = servidor.accept()
                thread = threading.Thread(target=self.atender, args=(conexao,))
                thread.start()
            except OSError:
                break

    def atender(self, conexao):
        try:
            mensagem = conexao.recv(1024).decode()
            print(f"[P{self.id}] recebeu: {mensagem}")

            if mensagem == "PING":
                conexao.sendall(b"PONG")

            elif mensagem == "ELECTION":
                self.receber_eleicao(conexao)

            elif mensagem.startswith("COORDINATOR"):
                partes = mensagem.split(":")
                with self.lock_diagrama:
                    self.coordenador = int(partes[1])
                    print(f"[P{self.id}] novo coordenador: P{self.coordenador}")
                    if self.iniciador_eleicao is not None:
                        self.log(f"P{self.coordenador} venceu a eleição")
                        self.log(f"P{self.coordenador} → P{self.id} COORDINATOR (recebido)")
                        if not self.montando_diagrama:
                            self.apresentar_diagrama()
                    if not self.montando_diagrama:
                        self.eleicao_em_andamento = False

        finally:
            conexao.close()

    def receber_eleicao(self, conexao):
        conexao.sendall(b"OK")
        print(f"[P{self.id}] enviou OK")

        if self.elegivel:
            threading.Thread(target=self.iniciar_eleicao).start()

    def enviar(self, id_destino, mensagem):
        host, porta = PROCESSOS[id_destino]
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.settimeout(2)
            cliente.connect((host, porta))
            cliente.sendall(mensagem.encode())
            resposta = cliente.recv(1024).decode()
            cliente.close()
            return resposta
        except Exception:
            return None

    def monitorar_coordenador(self):
        while self.ativo:
            time.sleep(5)

            # Se ainda não existe coordenador, não verifica
            if self.coordenador is None:
                continue

            # O coordenador não precisa verificar a si mesmo
            if self.coordenador == self.id:
                continue

            # Evita iniciar outra eleição enquanto uma está acontecendo
            if self.eleicao_em_andamento:
                continue

            print(f"[P{self.id}] Enviando PING para P{self.coordenador}")

            resposta = self.enviar(self.coordenador, "PING")

            if resposta == "PONG":
                print(f"[P{self.id}] P{self.coordenador} respondeu PONG")

            else:
                print(f"[P{self.id}] Coordenador não respondeu!")
                print(f"[P{self.id}] Iniciando eleição automaticamente...")

                self.coordenador = None
                self.iniciar_eleicao()

    def iniciar_eleicao(self):
        with self.lock_diagrama:
            if self.eleicao_em_andamento:
                return
            self.eleicao_em_andamento = True
            self.montando_diagrama = True
            self.iniciador_eleicao = self.id
            self.eventos_eleicao = []
            self.coordenador = None
        print("=" * 50)
        print(f"[P{self.id}] INICIANDO ELEIÇÃO")
        print("=" * 50)
        self.log(f"P{self.id} iniciou eleição")

        processos_maiores = [pid for pid in PROCESSOS if pid > self.id]

        alguem_respondeu = False
        for pid in processos_maiores:
            print(f"[P{self.id}] enviando ELECTION para P{pid}")
            self.log(f"P{self.id} → P{pid} ELECTION")
            resposta = self.enviar(pid, "ELECTION")
            if resposta == "OK":
                print(f"[P{self.id}] P{pid} respondeu OK")
                self.log(f"P{pid} → P{self.id} OK")
                alguem_respondeu = True
            else:
                self.log(f"P{pid} não respondeu OK")

        if not alguem_respondeu:
            self.tornar_coordenador()
        else:
            print(f"[P{self.id}] existe processo maior ativo.")
            print(f"[P{self.id}] desistindo da eleição.")

            # Registra a desistência com o horário
            self.log(f"P{self.id} desistiu da eleição")

        with self.lock_diagrama:
            self.montando_diagrama = False
            self.eleicao_em_andamento = False
            self.apresentar_diagrama()

    def tornar_coordenador(self):
        self.coordenador = self.id

        print("*" * 50)
        print(f"*** P{self.id} É O NOVO COORDENADOR ***")
        print("*" * 50)

        # Registra quem venceu a eleição
        self.log(f"P{self.id} venceu a eleição")

        for pid in PROCESSOS:
            if pid != self.id:
                # Registra o anúncio do novo coordenador
                self.log(f"P{self.id} → P{pid} COORDINATOR")
                self.enviar(pid, f"COORDINATOR:{self.id}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 processo.py <ID>")
        sys.exit(1)

    id_processo = int(sys.argv[1])
    processo = Processo(id_processo)

    servidor = threading.Thread(target=processo.iniciar_servidor, daemon=True)
    servidor.start()

    monitor = threading.Thread(target=processo.monitorar_coordenador, daemon=True)
    monitor.start()

    while True:
        comando = input(f"[P{id_processo}] comando> ")

        if comando == "eleicao":
            processo.iniciar_eleicao()

        elif comando == "status":
            print(f"ID: P{processo.id}")
            print(f"Coordenador: P{processo.coordenador}")

        elif comando == "sair":
            break
        else:
            print("Comandos: eleicao | status | sair")
