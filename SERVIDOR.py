import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
# -- Puerto donde lanzar el servidor
PORT = 8088


# Clase con nuestro manejador. Es una clase derivada de BaseHTTPRequestHandler
# Esto significa que "hereda" todos los metodos de esta clase. Y los que
# nosotros consideremos los podemos reemplazar por los nuestros
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    # GET. Este metodo se invoca automaticamente cada vez que hay una
    # peticion GET por HTTP. El recurso que nos solicitan se encuentra
    # en self.path
    def do_GET(self):
        # La primera linea del mensaje de respuesta es el
        # status. Indicamos que OK

        if self.path == '/':
            self.send_response(200)
        # En las siguientes lineas de la respuesta colocamos las
        # cabeceras necesarias para que el cliente entienda el
        # contenido que le enviamos (que sera HTML)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        # Este es el mensaje que enviamos al cliente: un texto y
        # el recurso solicitado
            with open('formulario.html', 'r')as f:
                content = f.read()

            message = "Por favor rellena este formulario " + content

        # Enviar el mensaaje completo
            self.wfile.write(bytes(message, "utf8"))
            print("Formulario enviado")
            return

        elif self.path !='/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            medicamento = parse_qs(urlparse(self.path).query).get('medicamento',)
            laboratorio = parse_qs(urlparse(self.path).query).get('laboratorio',)

            print(medicamento)
            print(laboratorio)

            self.wfile.write(bytes('datos enviados', "utf8"))
            return


# ----------------------------------
# El servidor comienza a aqui
# ----------------------------------
# Establecemos como manejador nuestra propia clase
Handler = testHTTPRequestHandler

# -- Configurar el socket del servidor, para esperar conexiones de clientes
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)

    # Entrar en el bucle principal
    # Las peticiones se atienden desde nuestro manejador
    # Cada vez que se ocurra un "GET" se invoca al metodo do_GET de
    # nuestro manejador
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Interrumpido por el usuario")

print("")
print("Servidor parado")

