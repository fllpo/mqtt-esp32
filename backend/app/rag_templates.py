TEMPLATES_SQL = {
    "zero_shot": """
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
""",
    "one_shot": """
Você é um especialista em SQL. Com base no esquema abaixo, gere uma consulta SQL válida para responder à pergunta.
Use apenas as tabelas e colunas fornecidas.

### Esquema do Banco de Dados:
{{ schema }}

### Exemplo:
Pergunta: Qual foi a maior temperatura registrada?
Resposta: SELECT MAX(temperatura_max) FROM clima

### Pergunta:
{{ query }}

### Instruções:
- Responda APENAS com o comando SQL
- Use a sintaxe SQL padrão
- Não inclua explicações ou texto adicional
""",
    "chain_of_thought": """
Você é um especialista em SQL. Com base no esquema abaixo, pense passo a passo e gere uma consulta SQL válida para responder à pergunta.
Use apenas as tabelas e colunas fornecidas.

### Esquema do Banco de Dados:
{{ schema }}

### Pergunta:
{{ query }}

### Passo a passo:
1. Analise a pergunta e identifique as colunas relevantes.
2. Descreva brevemente o raciocínio para montar a consulta.
3. Escreva o comando SQL final.

""",
}

TEMPLATES_TRATAMENTO = {
    "zero_shot": """
Você recebeu uma resposta do banco de dados. Responda à pergunta original de forma direta e clara, usando frases completas e sem jargões técnicos.

### Esquema do Banco de Dados:
{{ schema }}

### Resposta Bruta do Banco:
{{ resposta_db_rag }}

### Pergunta Original:
{{ query }}
""",
    "one_shot": """
Você recebeu uma resposta do banco de dados. Veja o exemplo e responda à pergunta original de forma direta e clara.

### Exemplo:
Pergunta: Qual foi a maior temperatura registrada?
Resposta Bruta do Banco: [(38.5,)]
Resposta Final: A maior temperatura registrada foi de 38,5°C.

### Esquema do Banco de Dados:
{{ schema }}

### Resposta Bruta do Banco:
{{ resposta_db_rag }}

### Pergunta Original:
{{ query }}
""",
    "chain_of_thought": """
Você recebeu uma resposta do banco de dados. Pense passo a passo para entender os dados e responda à pergunta original de forma clara.

### Passos:
1. Analise a resposta bruta do banco.
2. Interprete os valores.
3. Formule uma resposta final em português claro.

### Esquema do Banco de Dados:
{{ schema }}

### Resposta Bruta do Banco:
{{ resposta_db_rag }}

### Pergunta Original:
{{ query }}

### Resposta:
Raciocínio: <explique aqui>
Resposta Final: <resposta clara>
""",
}
