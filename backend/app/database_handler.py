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
        self.nome_tabela = "clima"
        self.connect()
        self.create_table()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            print("[DB_HANDLER] Conectado ao banco de dados MySQL")

        except mysql.connector.Error as err:
            print(f"[DB_HANDLER] Erro ao conectar ao banco de dados: {err}")
            raise

    def create_table(self):
        try:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS {self.nome_tabela} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                temperatura_atual FLOAT,
                temperatura_max FLOAT,
                temperatura_min FLOAT,
                umidade_atual FLOAT,
                umidade_max FLOAT,
                umidade_min FLOAT,
                pressao_atual FLOAT,
                pressao_max FLOAT,
                pressao_min FLOAT,
                orvalho_atual FLOAT,
                orvalho_max FLOAT,
                orvalho_min FLOAT
            )
            """
            )
            self.connection.commit()
            print("[DB_HANDLER] Tabela verificada/criada com sucesso")

        except mysql.connector.Error as err:
            print(f"[DB_HANDLER] Erro ao criar tabela: {err}")
            self.connection.rollback()
            raise

    def insert_reading(self, temperatura_atual, temperatura_max, temperatura_min, 
                        umidade_atual, umidade_max, umidade_min,
                        pressao_atual, pressao_max, pressao_min,
                        orvalho_atual, orvalho_max, orvalho_min):
        
        if not self.connection.is_connected():
            self.connect()
        try:
            query = f"""
            INSERT INTO {self.nome_tabela} (
                temperatura_atual, temperatura_max, temperatura_min, 
                umidade_atual, umidade_max, umidade_min,
                pressao_atual, pressao_max, pressao_min, 
                orvalho_atual, orvalho_max, orvalho_min
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            valor = (
                temperatura_atual, temperatura_max, temperatura_min,
                umidade_atual, umidade_max, umidade_min,
                pressao_atual, pressao_max, pressao_min,
                orvalho_atual, orvalho_max, orvalho_min
            )

            self.cursor.execute(query, valor)
            self.connection.commit()
            print(
                f"[DB_HANDLER] Dados inseridos com sucesso - ({datetime.now().strftime('%d/%m/%Y às %H:%M')})\n"
            )
            return True

        except mysql.connector.Error as err:
            print(f"[DB_HANDLER] Erro ao inserir dados: {err}")
            self.connection.rollback()
            return False

    def get_rag_data(self, query):
        try:
            self.connect() 
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return results

        except mysql.connector.Error as err:
            print(f"[DB_HANDLER] Erro ao buscar dados: {err}")
            return None
        finally:
            self.close()


    def get_latest_data(self):
        try:
            self.connect() 
            
            query = f"""
                SELECT * FROM {self.nome_tabela}
                ORDER BY timestamp DESC
                LIMIT 1
                """

            self.cursor.execute(query)
            result = self.cursor.fetchone()

            if result:
                return {
                    "timestamp": result[1],
                    "temperatura_atual": result[2],
                    "temperatura_max": result[3],
                    "temperatura_min": result[4],
                    "umidade_atual": result[5],
                    "umidade_max": result[6],
                    "umidade_min": result[7],
                    "pressao_atual": result[8],
                    "pressao_max": result[9],
                    "pressao_min": result[10],
                    "orvalho_atual": result[11],
                    "orvalho_max": result[12],
                    "orvalho_min": result[13],
                }
            else:
                return None

        except Exception as e:
            print(f"[DB_HANDLER]Erro ao buscar dados: {e}")
            return None
        finally:
            self.close()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("[DB_HANDLER] Conexão com o banco encerrada")
