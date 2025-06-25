from haystack import Pipeline
#from haystack.components.fetchers import LinkContentFetcher
#from haystack.components.converters import HTMLToDocument
#from haystack.components.preprocessors import DocumentSplitter
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator

db_schema = """
CREATE TABLE clima (
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

sql_template = """
Você é um especialista em SQL. Gere uma consulta SQL para responder à pergunta usando apenas o esquema abaixo:

Esquema do banco de dados: {{schema}}
Pergunta: {{query}}

Retorne apenas a consulta SQL, sem explicações adicionais. não inclua comentários ou texto adicional. A consulta deve ser válida e executável no MySQL.
não inclua o esquema do banco de dados na resposta, apenas a consulta SQL.

"""

template = """
Responda em 1 parágrafo baseado SOMENTE nisto:
{% for doc in documents %}
{{ doc.content }}
% endfor %}
Pergunta: {{query}}
Responda em português, de forma clara e objetiva, sem repetir a pergunta.
"""


pipe = Pipeline()
#pipe.add_component("fetcher", LinkContentFetcher())
#pipe.add_component("converter", HTMLToDocument())
#pipe.add_component("splitter", DocumentSplitter(split_by="word", split_length=300))
pipe.add_component("prompt", PromptBuilder(template=sql_template,
                                           required_variables=["query", "schema"],))
pipe.add_component("llm", OllamaGenerator(
    model="sqlcoder", 
    url="http://localhost:11434",
    timeout=300.0,
    generation_kwargs={
        #"num_predict": 200,
        "temperature": 0.1,
        "stop": ["```"],
    }
))



#pipe.connect("fetcher.streams", "converter.sources")
#pipe.connect("converter.documents", "splitter.documents")
#pipe.connect("splitter.documents", "prompt.documents")
pipe.connect("prompt", "llm")


def gerar_sql(pergunta):
    try:
        response = pipe.run({"prompt": {
                                "query": pergunta,
                                "schema": db_schema}})
        sql = response["llm"]["replies"][0].strip()
        
        if sql.startswith("```sql"):
            sql = sql[6:-3].strip()
        return sql
    except Exception as e:
        print(f"Erro ao gerar SQL: {e}")
        return None

pergunta = "Qual a temperatura máxima registrada essa semana?"
sql_gerado = gerar_sql(pergunta)

print(f"Pergunta: {pergunta}")
print(f"SQL Gerado:")
print(sql_gerado)


#try:
#    response = pipe.run(
#        {"prompt": {"query": "Qual a temperatura máxima registrada essa semana?"}, 
#         "fetcher": {"urls": ["https://pt.wikipedia.org/wiki/Mario_(personagem)"]}}
#    )
#    print(response["llm"]["replies"][0])
#except Exception as e:
#    print(f"Falha: {e}")
    