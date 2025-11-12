from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from database_handler import DatabaseHandler
from rag_templates import TEMPLATES_SQL, TEMPLATES_TRATAMENTO
import re
import requests
import sys

db_handler = DatabaseHandler()

def extrair_sql(resposta):
    match = re.search(r"```SQL\s*(.*?)\s*```", resposta, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return resposta.strip()


def verificar_modelo(modelo, url="http://localhost:11434"):
    try:
        response = requests.get(f"{url}/api/tags", timeout=3)
        response.raise_for_status()
        modelos_instalados = [m["name"] for m in response.json().get("models", [])]

        if modelo not in modelos_instalados:
            print(f"Erro: o modelo '{modelo}' não está instalado no Ollama.")
            print(
                "Modelos disponíveis:",
                ", ".join(modelos_instalados) or "nenhum modelo encontrado",
            )
            sys.exit(1)  # encerra o programa imediatamente

    except requests.exceptions.ConnectionError:
        print("Erro: não foi possível conectar ao Ollama em http://localhost:11434")
        print("Verifique se o Ollama está rodando (`ollama serve` ou o serviço ativo).")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao verificar modelo: {e}")
        sys.exit(1)


def get_resposta_rag(pergunta, modo_sql, modo_tratamento, modelo):
    # verificar_modelo(modelo)

    schema = """
        TABLE clima (
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
    template_sql = TEMPLATES_SQL[modo_sql]
    template_tratamento = TEMPLATES_TRATAMENTO[modo_tratamento]

    pipe_sql = Pipeline()
    pipe_sql.add_component(
        name="prompt_sql",
        instance=PromptBuilder(
            template=template_sql, required_variables=["query", "schema"]
        ),
    )
    pipe_sql.add_component(
        name="llm_sql",
        instance=OllamaGenerator(model=modelo, url="http://localhost:11434"),
    )
    pipe_sql.connect(sender="prompt_sql", receiver="llm_sql")

    pipe_tratamento = Pipeline()
    pipe_tratamento.add_component(
        name="prompt_tratamento",
        instance=PromptBuilder(
            template=template_tratamento,
            required_variables=["resposta_db_rag", "query"],
        ),
    )
    pipe_tratamento.add_component(
        name="llm_tratamento",
        instance=OllamaGenerator(model=modelo, url="http://localhost:11434"),
    )
    pipe_tratamento.connect(sender="prompt_tratamento", receiver="llm_tratamento")

    resposta_sql = pipe_sql.run({"prompt_sql": {"query": pergunta, "schema": schema}})

    sql_string = extrair_sql(resposta=resposta_sql["llm_sql"]["replies"][0].strip())

    if sql_string.startswith("SELECT") is False:
        return "Desculpe, não posso executar esse comando."

    resposta_db_rag = db_handler.get_rag_data(sql_string)

    if resposta_db_rag is None:
        return "Desculpe, não consegui encontrar uma resposta para sua pergunta."

    resposta_final = pipe_tratamento.run(
        {"prompt_tratamento": {"resposta_db_rag": resposta_db_rag, "query": pergunta}}
    )

    return sql_string, resposta_final["llm_tratamento"]["replies"][0]
