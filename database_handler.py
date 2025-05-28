import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_config = {
            'host': os.getenv("DB_HOST", "localhost"),
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'database': os.getenv("DB_NAME")
        }
        self.connect()
        self.create_table()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            print("Conectado ao banco de dados MySQL")

        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao banco de dados: {err}")
            raise

    def create_table(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dados_sensor (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME,
                temperatura FLOAT,
                umidade FLOAT,
                pressao FLOAT
            )
            """)
            self.connection.commit()
            print("Tabela verificada/criada com sucesso")

        except mysql.connector.Error as err:
            print(f"Erro ao criar tabela: {err}")
            self.connection.rollback()
            raise

    def insert_reading(self, temperatura, umidade, pressao):
        try:
            query = """
            INSERT INTO dados_sensor (timestamp, temperatura, umidade, pressao)
            VALUES (%s, %s, %s, %s)
            """
            valor = (datetime.now(), temperatura, umidade, pressao)

            self.cursor.execute(query, valor)
            self.connection.commit()
            print("Dados inseridos com sucesso")
            return True

        except mysql.connector.Error as err:
            print(f"Erro ao inserir dados: {err}")
            self.connection.rollback()
            return False

    def get_latest_data(self):
        try:
            self.connect()

            query = """
                SELECT * FROM dados_sensor
                ORDER BY timestamp DESC
                LIMIT 1
                """

            self.cursor.execute(query)
            result = self.cursor.fetchone()

            if result:
                return {
                    "timestamp": result[1].strftime("%H:%M"),
                    "temperatura": result[2],
                    "umidade": result[3],
                    "pressao": result[4],
                }
            else:
                return None

        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None
        finally:
            self.close()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Conexão com o banco encerrada")
