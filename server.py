import socket
import threading

# Lista para acompanhar todos os clientes conectados e seus nomes
clientes_conectados = []

# Função para enviar uma mensagem para todos os clientes, exceto o remetente
def enviar_mensagem(msg, cliente_remetente):
    for cliente, nome in clientes_conectados:
        if cliente != cliente_remetente:
            try:
                cliente.send(msg.encode("utf-8"))
            except Exception as e:
                print(f"[ERRO] Falha ao enviar mensagem para {nome}: {e}")
                cliente.close()
                clientes_conectados.remove((cliente, nome))

# Função para lidar com conexões de clientes individuais
def lidar_com_cliente(socket_cliente, endereco):
    try:
        # Recebe o nome de exibição do cliente
        nome = socket_cliente.recv(1024).decode("utf-8").strip()
        if not nome:
            raise ValueError("Nome vazio recebido.")
        print(f"[NOVA CONEXÃO] {nome} ({endereco}) se conectou.")
        clientes_conectados.append((socket_cliente, nome))

        # Notifica todos os clientes sobre a nova conexão
        enviar_mensagem(f"{nome} entrou no chat!", socket_cliente)

        while True:
            try:
                msg = socket_cliente.recv(1024).decode("utf-8").strip()
                if not msg:
                    break  # Mensagem vazia indica desconexão

                # Verifica se a mensagem é um comando de unicast
                if msg.startswith("/w "):
                    # Formato de mensagem unicast: "/w <nome_destinatario> <mensagem>"
                    partes = msg.split(" ", 2)
                    if len(partes) == 3:
                        nome_destinatario = partes[1]
                        mensagem_unicast = f"{nome} sussurra: {partes[2]}"
                        for cliente, nome_cliente in clientes_conectados:
                            if nome_cliente == nome_destinatario:
                                cliente.send(mensagem_unicast.encode("utf-8"))
                                socket_cliente.send(mensagem_unicast.encode("utf-8"))
                                break
                        else:
                            socket_cliente.send(f"[ERRO] Usuário '{nome_destinatario}' não encontrado.".encode("utf-8"))
                    else:
                        socket_cliente.send("[ERRO] Formato de unicast inválido. Use: /w <nome_destinatario> <mensagem>".encode("utf-8"))
                else:
                    # Formata a mensagem com o nome do cliente e a mensagem
                    mensagem_formatada = f"{nome} diz: {msg}"
                    print(mensagem_formatada)
                    enviar_mensagem(mensagem_formatada, socket_cliente)
                    socket_cliente.send(f"Você: {msg}".encode("utf-8"))
            except Exception as e:
                print(f"[ERRO] Erro ao lidar com mensagem de {nome}: {e}")
                break
    except Exception as e:
        print(f"[ERRO] Erro de conexão com {endereco}: {e}")
    finally:
        socket_cliente.close()
        if (socket_cliente, nome) in clientes_conectados:
            clientes_conectados.remove((socket_cliente, nome))
        enviar_mensagem(f"{nome} saiu do chat.", socket_cliente)
        print(f"[DESCONECTADO] {nome} ({endereco}) se desconectou.")

# Função para iniciar o servidor
def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("0.0.0.0", 5555))  # Aceita conexões de qualquer IP na rede
    servidor.listen()
    print("[SERVIDOR INICIADO] Aguardando conexões...")

    while True:
        socket_cliente, endereco = servidor.accept()
        thread_cliente = threading.Thread(target=lidar_com_cliente, args=(socket_cliente, endereco), daemon=True)
        thread_cliente.start()
        print(f"[CONEXÕES ATIVAS] {threading.active_count() - 1}")

iniciar_servidor()