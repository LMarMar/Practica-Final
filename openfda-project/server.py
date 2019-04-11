import http.server
import socketserver
import http.client
import json
socketserver.TCPServer.allow_reuse_address = True #Para no tener que cambiar el puerto
# -- Puerto donde lanzar el servidor
PORT = 8000 #8000
headers = {'User-Agent': 'http-client'}

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_openfda(self,search=None, limit=1):

        #Conectamos con el servidor
        conn = http.client.HTTPSConnection("api.fda.gov")

        #------------------------------------------------------
        request = '/drug/label.json/'+'?limit={}'.format(limit)
        if search != None:
            request += '&search={}'.format(search)
        print('Petición: ',request)
        #------------------------------------------------------

        #Enviar mensaje de solicitud.
        conn.request('GET',request,None, headers)

        #Obtener respuesta
        r1 = conn.getresponse()
        if r1.status ==404:
            print('ERROR, Recurso no encontrado')
            exit(1)
        print(r1.status, r1.reason) #200 OK

        #Leer contenido del json
        data_json = r1.read().decode("utf-8")
        conn.close()

        #Tenemos que pocesar el contenido que nos ha devueto en form json
        data = json.loads(data_json)

        return data


    def find_medicamento(self,search=None,limit=1):
        drug = self.do_openfda(search,limit)

        #Creamos el inicio del fichero html que enviaremos
        message = ('<!DOCTYPE html>\n'
                   '<html lang="en">\n'
                   '<head>\n'
                        '<meta charset="UTF-8">\n'
                        '<title>Openfda</title>\n'
                   '</head>\n'
                   '<body>\n'
                   '<ul>\n'
                   )

        #META tiene la informacion de búsqueda
        meta = drug['meta']
        total = meta['results']['total'] #Total de objetos
        limit = meta['results']['limit'] #Total objetos recibidos

        #Ampliamos el fichero html
        message += 'Se han recibido {} / {} medicamentos'.format(limit,total)

        #RESULTS tiene los resultados de la búsqueda
        drugs = drug['results']
        for drug in drugs:
            if drug['openfda']:
                nombre = drug['openfda']['substance_name'][0]
                marca = drug['openfda']['brand_name'][0]
                fabricante = drug['openfda']['manufacturer_name'][0]
            else:
                nombre ='?'
                marca ='?'
                fabricante ='?'
            drug_id = drug['id']
            if drug['purpose']:
                drug_purpose = drug['purpose'][0]
            else:
                drug_purpose='?'

            #Ampliamos el ficher html
            message += ('\n' 
                       'NOMBRE:{}\n '
                       'MARCA:{}\n '
                       'FABRICANTE:{}\n '
                       'ID:{}\n '
                       'PROPÓSITO:{}\n '
                       '---------------------------------'.format(nombre,marca,fabricante,drug_id,drug_purpose)
                        )


        #Finalizamos el html
        message +=('</ul>\n'
                   '</body>\n'
                   '</html>')

        return message



    def find_empresa(self, search=None,limit=1):
        empresa = self.do_openfda(search,limit)

        #Creamos el inicio del fichero html que enviaremos
        message = ('<!DOCTYPE html>\n'
                   '<html lang="en">\n'
                   '<head>\n'
                        '<meta charset="UTF-8">\n'
                        '<title>Openfda</title>\n'
                   '</head>\n'
                   '<body>\n'
                   '<ul>\n'
                   )

        #META tiene la informacion de búsqueda
        meta = empresa['meta']
        total = meta['results']['total'] #Total de objetos
        limit = meta['results']['limit'] #Total objetos recibidos

        #Ampliamos el fichero html
        message += 'Se han recibido {} / {} medicamentos'.format(limit,total)

        #RESULTS tiene los resultados de la búsqueda
        empresas = empresa['results']
        for empresa in empresas:
            if empresa['openfda']:
                if empresa['openfda']['manufacturer_name']:
                    empresa=empresa['openfda']['manufacturer_name'][0]
                else:
                    empresa ='?'
            else:
                empresa ='?'

            #Ampliamos el ficher html
            message += ('\n' 
                       'EMPRESA FABRICANTE:{}\n '
                       
                       '---------------------------------'.format(empresa)
                        )


        #Finalizamos el html
        message +=('</ul>\n'
                   '</body>\n'
                   '</html>')

        return message


    # GET. Este metodo se invoca automaticamente cada vez que hay una peticion GET por HTTP. El recurso que nos solicitan se encuentra en self.path
    def do_GET(self):

        global medicamento
        print('Path: ', self.path)

        recurso = self.path.split('?') #Se convierte en lista
        path1 = recurso[0]
        if len(recurso) == 1: #Si solo mide 1 es porque no tiene parámetros
            path2 = ''
        else:                 #Si mide más de 1 es porque tiene parámetros 'path2'
            path2 = recurso[1]

        if path2: #Si existe es porque tenemos datos en la url
            #Como solo enviamos un dato en cada path1 no necesitamos dividirlo por el &
            dato = path2.split('=') # Tenemos una lista con el nombre el dato y su valor

            if dato[0]=='medicamento':
                medicamento = dato[1]
            elif dato[0] == 'empresa':
                empresa = dato[1]
            elif dato[0] == "limit":
                limit = int(dato[1])


        #FORMULARIO
        if path1 == '/':
            with open('form_openfda.html', 'r')as f:
                content = f.read()
            message = "Por favor rellena este formulario " + content
#-----------------------------------------------------------------------------------------------------------------------
        #MEDICAMENTO
        elif path1 =='/medicamento':
            message = self.find_medicamento(search='active_ingredient:'+medicamento)

        #EMPRESA
        elif path1 =='/empresa':
            message = self.find_empresa(search='openfda.manufacturer_name:'+ empresa)

        #LISTA MEDICAMENTOS
        elif path1 =='/listamedicamentos':
            message = self.find_medicamento(limit=limit)

        #LISTA EMPRESAS
        elif path1 =='/listaempresas':
            message = self.find_empresa(limit=limit)
#-----------------------------------------------------------------------------------------------------------------------
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(message, "utf8"))
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

