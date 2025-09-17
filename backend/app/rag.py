from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from database_handler import DatabaseHandler
from rag_templates import TEMPLATES_SQL, TEMPLATES_TRATAMENTO
import re

db_handler = DatabaseHandler()


def extrair_sql(resposta):
    match = re.search(r"```SQL\s*(.*?)\s*```", resposta, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return resposta.strip()


def get_resposta_rag(pergunta, modo_sql, modo_tratamento):

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
        instance=OllamaGenerator(model="mistral", url="http://localhost:11434"),
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
        instance=OllamaGenerator(model="mistral", url="http://localhost:11434"),
    )
    pipe_tratamento.connect(sender="prompt_tratamento", receiver="llm_tratamento")

    print(f"Pergunta: {pergunta}")

    resposta_sql = pipe_sql.run({"prompt_sql": {"query": pergunta, "schema": schema}})

    print(
        f"Resposta SQL bruta: {resposta_sql["llm_sql"]["replies"][0].strip()}",
    )

    sql = extrair_sql(resposta=resposta_sql["llm_sql"]["replies"][0].strip())

    print(f"SQL: {sql}")
    if sql.startswith("SELECT") is False:
        return "Desculpe, não posso executar comandos que não sejam SELECT."
    if "insert" in sql or "INSERT" in sql or "update" in sql or "UPDATE" in sql:
        return "Desculpe, não posso executar comandos de inserção ou atualização."
    if "delete" in sql or "DELETE" in sql or "drop" in sql or "DROP" in sql:
        return "Desculpe, não posso executar comandos de exclusão ou remoção."

    resposta_db_rag = db_handler.get_rag_data(sql)
    print(f"Resposta do banco: {resposta_db_rag}")

    if resposta_db_rag is None:
        return "Desculpe, não consegui encontrar uma resposta para sua pergunta."

    resposta_final = pipe_tratamento.run(
        {"prompt_tratamento": {"resposta_db_rag": resposta_db_rag, "query": pergunta}}
    )
    print(f"Resposta Final: {resposta_final['llm_tratamento']['replies'][0]}")

    return resposta_final["llm_tratamento"]["replies"][0]
