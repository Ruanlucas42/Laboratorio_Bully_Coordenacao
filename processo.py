import socket
import threading
import sys

from config import PROCESSOS


class Processo:
    def __init__(self, id_processo):
        self.id = id_processo
        self.host, self.porta = PROCESSOS[self.id]
        self.coordenador = None
        self.ativo = True
        self.elegivel = True
        self.eleicao_em_andamento = False

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

            if mensagem == "ELECTION":
                self.receber_eleicao(conexao)
            elif mensagem.startswith("COORDINATOR"):
                partes = mensagem.split(":")
                self.coordenador = int(partes[1])
                self.eleicao_em_andamento = False
                print(f"[P{self.id}] novo coordenador: P{self.coordenador}")
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

    def iniciar_eleicao(self):
        if self.eleicao_em_andamento:
            return

        self.eleicao_em_andamento = True
        print("=" * 50)
        print(f"[P{self.id}] INICIANDO ELEIÇÃO")
        print("=" * 50)

        processos_maiores = [pid for pid in PROCESSOS if pid > self.id]

        alguem_respondeu = False
        for pid in processos_maiores:
            print(f"[P{self.id}] enviando ELECTION para P{pid}")
            resposta = self.enviar(pid, "ELECTION")
            if resposta == "OK":
                print(f"[P{self.id}] P{pid} respondeu OK")
                alguem_respondeu = True

        if not alguem_respondeu:
            self.tornar_coordenador()
        else:
            print(f"[P{self.id}] existe processo maior ativo.")
            print(f"[P{self.id}] desistindo da eleição.")
            self.eleicao_em_andamento = False

    def tornar_coordenador(self):
        self.coordenador = self.id
        self.eleicao_em_andamento = False

        print("*" * 50)
        print(f"*** P{self.id} É O NOVO COORDENADOR ***")
        print("*" * 50)

        for pid in PROCESSOS:
            if pid != self.id:
                self.enviar(pid, f"COORDINATOR:{self.id}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 processo.py <ID>")
        sys.exit(1)

    id_processo = int(sys.argv[1])
    processo = Processo(id_processo)

    servidor = threading.Thread(target=processo.iniciar_servidor, daemon=True)
    servidor.start()

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