from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from database_handler import DatabaseHandler
db_handler = DatabaseHandler()

def get_resposta_rag(pergunta):
    
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

    template_sql = """
    Você é um especialista em SQL. Com base no esquema abaixo, gere uma consulta SQL válida para responder à pergunta.
    Use apenas as tabelas e colunas fornecidas.

    ### Esquema do Banco de Dados:
    {{ schema }}

    ### Pergunta:
    {{ query }}

    ### Instruções:
    - Responda APENAS com o comando SQL
    - Use a sintaxe SQL padrão
    - Não inclua explicações ou texto adicional
    - Caso precise informar localização do dispositivo: "Cacuia, Nova Iguaçu, RJ, Brasil"
    """

    template_tratamento = """
    Você recebeu uma resposta do banco de dados. Sua tarefa é:
    1. Extrair os dados relevantes
    2. Formatá-los de maneira clara e concisa
    3. Responder a pergunta original de forma direta

    ### Resposta Bruta do Banco:
    {{ resposta_db_rag }}

    ### Pergunta Original:
    {{ query }}

    ### Formato de Resposta:
    - Use frases completas
    - Seja específico com valores e datas
    - Destaque valores importantes
    - Evite jargões técnicos
    - Não inclua SQL ou código
    - Dê preferencia a respostas diretas, curtas e claras
    - Não inclua o termo "banco de dados", "tabelas" ou "colunas" na resposta
    

    """


    pipe_sql = Pipeline()
    pipe_sql.add_component("prompt_sql",
                        PromptBuilder(
                            template=template_sql,
                                required_variables=["query", 
                                                    "schema"]))
    pipe_sql.add_component("llm_sql", OllamaGenerator(model="mistral",
                                            url="http://localhost:11434"))
    pipe_sql.connect("prompt_sql", "llm_sql")

    pipe_tratamento = Pipeline()
    pipe_tratamento.add_component("prompt_tratamento",
                                PromptBuilder(
                                    template=template_tratamento,
                                    required_variables=["resposta_db_rag", 
                                                        "query"]))
    pipe_tratamento.add_component("llm_tratamento", OllamaGenerator(model="mistral",
                                            url="http://localhost:11434"))
    pipe_tratamento.connect("prompt_tratamento", "llm_tratamento")   
    
    print(f"Pergunta: {pergunta}")

    resposta_sql = pipe_sql.run({
        "prompt_sql": {
            "query": pergunta,
            "schema": schema 
        }
    })

    sql = resposta_sql["llm_sql"]["replies"][0].strip()
    print(f"SQL: {sql}")


    resposta_db_rag = db_handler.get_rag_data(sql)
    print(f"Resposta do banco: {resposta_db_rag}")

    if resposta_db_rag is None:
        return "Desculpe, não consegui encontrar uma resposta para sua pergunta."

    resposta_final = pipe_tratamento.run({
        "prompt_tratamento": {
            "resposta_db_rag": resposta_db_rag,
            "query": pergunta
        }  
    })
    print(f"Resposta Final: {resposta_final['llm_tratamento']['replies'][0]}")
    
    return resposta_final['llm_tratamento']['replies'][0]


