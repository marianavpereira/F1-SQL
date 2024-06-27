# SQL-F1
# Sumário

Aplicação Python demonstrando o acesso à BD F1

Referência
sqlite3
Flask
Jinja templates

# Instalação de dependências
## Python 3 e pip

Deve ter o Python 3 e o gestor de pacotes pip instalado. Pode instalar os mesmos em Ubuntu por exemplo usando:
```
sudo apt-get install python3 python3-pip
```
## Bibliotecas Python
```
pip3 install --user Flask
```
# Execução
Inicie a aplicação executando python3 server.py e interaja com a mesma abrindo uma janela no seu browser com o endereço http://localhost:9001/
```
$ python3 server.py
2021-11-27 15:07:33 - INFO - Connected to database movie_stream
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
2021-11-27 15:07:33 - INFO -  * Running on http://0.0.0.0:9001/ (Press CTRL+C to quit)
...
```
