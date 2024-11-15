import socket
import threading

# Função para receber mensagens do servidor
def receber_mensagens(socket_cliente):
    while True:
        try:
            msg = socket_cliente.recv(1024).decode("utf-8")
            print(msg)  # Exibe a mensagem recebida do servidor
        except:
            print("[DESCONECTADO] A conexão com o servidor foi encerrada.")
            socket_cliente.close()
            break

# Função principal do cliente
def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Define o IP padrão do servidor
    servidor_ip = "192.168.0.100"  # Substitua pelo IP do servidor na rede local
    try:
        cliente.connect((servidor_ip, 5555))
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao servidor: {e}")
        return

    # Solicita o nome de exibição
    while True:
        nome = input("Digite seu nome de exibição: ").strip()
        if nome:
            cliente.send(nome.encode("utf-8"))  # Envia o nome para o servidor
            break
        else:
            print("[ERRO] O nome de exibição não pode ser vazio.")

    print(f"[CONECTADO] Bem-vindo, {nome}! Você está conectado ao chat.")

    # Inicia uma thread para receber mensagens de outros clientes
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente,))
    thread_receber.start()

    while True:
        try:
            msg = input()  # Usuário digita a mensagem
            cliente.send(msg.encode("utf-8"))
        except KeyboardInterrupt:  # Permite que o cliente saia com Ctrl+C
            print("\n[DESCONECTADO] Conexão encerrada pelo usuário.")
            break

    cliente.close()

iniciar_cliente()