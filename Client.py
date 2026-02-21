import socket, threading, time

# Configuración del servidor al que se conectará este cliente
HOST = "172.17.0.2"  # IP del servidor
PUERTO = 5000           # Puerto del servidor

# Función que escucha continuamente mensajes del servidor
def escuchar_servidor(cliente_socket, conectado):
    while conectado[0]: # Mientras la conexión esté activa
        try:
            datos = cliente_socket.recv(1024) # Recibe hasta 1024 bytes
            if not datos: # Si no hay datos, el servidor cerró la conexión
                print("\n[!] El servidor cerró la conexión.")
                conectado[0] = False
                break

            print(datos.decode("utf-8"), end="") # Muestra el mensaje recibido
        except OSError:
            # Error por socket cerrado
            break
        except Exception as e:
            print(f"\n[ERROR al recibir] {e}")
            conectado[0] = False
            break

# Función principal del cliente
def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crear socket TCP
    print("=" * 45)
    print("  💬 MiniDistributedChat — CLIENTE")
    print(f"  Conectando a {HOST}:{PUERTO} ...")
    print("=" * 45)
    try:
        cliente.connect((HOST, PUERTO)) # Intentar conectarse al servidor
    except ConnectionRefusedError:
        print("[ERROR] No se pudo conectar. ¿El servidor está encendido?")
        return
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print("✅ Conectado al servidor!\n")
    print("Comandos disponibles:")
    print("  JOIN <tu_nombre>  — Unirte al chat")
    print("  MSG <texto>       — Enviar un mensaje")
    print("  EXIT              — Salir del chat")
    print("-" * 45)
    conectado = [True] # Lista mutable para compartir el estado entre hilos

    # Hilo que se encargará de recibir mensajes mientras el usuario escribe
    hilo_receptor = threading.Thread(
        target=escuchar_servidor,
        args=(cliente, conectado),
        daemon=True # Hilo que se cierra cuando termina el programa
    )

    hilo_receptor.start()
    try:
        while conectado[0]: # Bucle principal para enviar mensajes al servidor
            try:
                entrada = input()
            except EOFError: # Si se cierra el input
                break

            if not entrada.strip(): # Ignorar líneas vacías
                continue

            upper = entrada.strip().upper()
            if not (upper.startswith("JOIN ") or upper.startswith("MSG ")  or upper == "EXIT"): # Validar comandos permitidos
                print("[!] Comando inválido. Usa: JOIN <nombre> | MSG <texto> | EXIT")
                continue

            try:
                cliente.send(entrada.strip().encode("utf-8")) # Enviar comando al servidor
            except Exception:
                print("[!] Error al enviar. Conexión perdida.")
                break

            if upper == "EXIT": # Si el usuario quiere salir
                time.sleep(0.3)  # Espera breve para que llegue el mensaje de salida al servidor
                conectado[0] = False
                break
    except KeyboardInterrupt: # Ctrl+C
        print("\n[!] Desconectando...")
        try:
            cliente.send("EXIT".encode("utf-8")) # Avisar al servidor
        except Exception:
            pass
    finally:
        cliente.close() # Cerrar socket
        print("👋 Desconectado del servidor. ¡Hasta luego!")

# Arranca el cliente si se ejecuta directamente
if __name__ == "__main__":
    iniciar_cliente()