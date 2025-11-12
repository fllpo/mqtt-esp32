# Projeto de Monitoramento Ambiental com ESP32, MQTT e IA

## Descrição do Projeto

Este projeto está sendo desenvolvido como Trabalho de Conclusão de Curso e consiste em um sistema completo de monitoramento ambiental que coleta dados de um sensor (temperatura, umidade, pressão atmosférica e ponto de orvalho) através de um microcontrolador ESP32, transmite os dados via protocolo MQTT para um servidor Flask utilizando o broker HiveMQ como o intermediário, armazena em um banco de dados MySQL e disponibiliza uma interface web com dashboard e assistente de IA para consulta dos dados.

## Como usar

### 1. Configuração

Crie um arquivo `.env` em `/backend` com:

```py
# Configuração MQTT
HOST="seu_broker_mqtt"
CLIENT_NAME="usuario"
PASSWORD="senha"
TOPIC="topico_dados"

# Configuração MySQL
DB_HOST="localhost"
DB_USER="usuario"
DB_PASSWORD="senha"
DB_NAME="clima_db"
```

### 2. Instalação

```py
pip install -r requirements.txt  # Instala dependências Python
```

### 3. Execução do servidor

```py
python mqtt_server.py #Inicia o servidor Flask
```
Acesse http://localhost:5000


### 4. Extra: Rodando o experimento
```py
python perguntas_avaliacao_rag.py mistral:latest #Inicia o experimento ao passar os modelos por parâmetro
```