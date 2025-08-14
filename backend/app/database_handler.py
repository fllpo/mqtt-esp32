from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

Base = declarative_base()


class Clima(Base):
    __tablename__ = "clima"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    temperatura_atual = Column(Float)
    temperatura_max = Column(Float)
    temperatura_min = Column(Float)
    umidade_atual = Column(Float)
    umidade_max = Column(Float)
    umidade_min = Column(Float)
    pressao_atual = Column(Float)
    pressao_max = Column(Float)
    pressao_min = Column(Float)
    orvalho_atual = Column(Float)
    orvalho_max = Column(Float)
    orvalho_min = Column(Float)


class DatabaseHandler:
    def __init__(self):
        db_host = os.getenv("DB_HOST", "localhost")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        self.engine = create_engine(
            f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
        )
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
        print("[DB_HANDLER] Configuração do banco de dados concluída")

    def create_tables(self):
        try:
            Base.metadata.create_all(self.engine)
            print("[DB_HANDLER] Tabelas verificadas/criadas com sucesso")
        except Exception as err:
            print(f"[DB_HANDLER] Erro ao criar tabelas: {err}")
            raise

    def insert_reading(
        self,
        temperatura_atual,
        temperatura_max,
        temperatura_min,
        umidade_atual,
        umidade_max,
        umidade_min,
        pressao_atual,
        pressao_max,
        pressao_min,
        orvalho_atual,
        orvalho_max,
        orvalho_min,
    ):

        valores = [
            temperatura_atual,
            temperatura_max,
            temperatura_min,
            umidade_atual,
            umidade_max,
            umidade_min,
            pressao_atual,
            pressao_max,
            pressao_min,
            orvalho_atual,
            orvalho_max,
            orvalho_min,
        ]

        if any(valor < 0 for valor in valores):
            print(
                "[DB_HANDLER] Valores negativos não são permitidos. Verifique o ESP32."
            )
            return False

        session = self.Session()
        try:
            novo_registro = Clima(
                temperatura_atual=temperatura_atual,
                temperatura_max=temperatura_max,
                temperatura_min=temperatura_min,
                umidade_atual=umidade_atual,
                umidade_max=umidade_max,
                umidade_min=umidade_min,
                pressao_atual=pressao_atual,
                pressao_max=pressao_max,
                pressao_min=pressao_min,
                orvalho_atual=orvalho_atual,
                orvalho_max=orvalho_max,
                orvalho_min=orvalho_min,
            )

            session.add(novo_registro)
            session.commit()
            print(
                f"[DB_HANDLER] Dados inseridos com sucesso - ({datetime.now().strftime('%d/%m/%Y às %H:%M')})\n"
            )
            return True

        except Exception as err:
            session.rollback()
            print(f"[DB_HANDLER] Erro ao inserir dados: {err}")
            return False
        finally:
            session.close()

    def get_rag_data(self, query):
        session = self.Session()
        try:
            result = session.execute(text(query))
            return result.fetchall()
        except Exception as err:
            print(f"[DB_HANDLER] Erro ao buscar dados: {err}")
            return None
        finally:
            session.close()

    def get_latest_data(self):
        session = self.Session()
        try:
            latest = session.query(Clima).order_by(Clima.timestamp.desc()).first()

            if latest:
                return {
                    "timestamp": latest.timestamp,
                    "temperatura_atual": latest.temperatura_atual,
                    "temperatura_max": latest.temperatura_max,
                    "temperatura_min": latest.temperatura_min,
                    "umidade_atual": latest.umidade_atual,
                    "umidade_max": latest.umidade_max,
                    "umidade_min": latest.umidade_min,
                    "pressao_atual": latest.pressao_atual,
                    "pressao_max": latest.pressao_max,
                    "pressao_min": latest.pressao_min,
                    "orvalho_atual": latest.orvalho_atual,
                    "orvalho_max": latest.orvalho_max,
                    "orvalho_min": latest.orvalho_min,
                }
            return None

        except Exception as e:
            print(f"[DB_HANDLER] Erro ao buscar dados: {e}")
            return None
        finally:
            session.close()
