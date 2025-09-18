import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app"))
)
from rag import get_resposta_rag


perguntas = [
    # Fáceis
    "Qual foi a temperatura máxima registrada ontem?",
    "Qual a umidade mínima registrada hoje?",
    "Qual era a pressão às 12h de hoje?",
    "Qual foi o valor do orvalho às 8h do dia 10 de junho de 2025?",
    "Qual a temperatura agora?",
    # Médias
    "Quais foram as temperaturas máximas e mínimas desta semana?",
    "Como variou a umidade ao longo do dia de ontem?",
    "Qual foi a maior pressão registrada nos últimos três dias?",
    "Quais foram os valores de orvalho registrados no mês passado?",
    "Qual foi a menor temperatura registrada neste mês?",
    # Difíceis
    "Como está o clima hoje?",
    "Quais são as médias de temperatura, umidade e pressão deste ano?",
    "Como o clima variou nos últimos seis meses?",
    "Quais tendências de temperatura podem ser observadas esse ano?",
    "Resuma os dados climáticos registrados até agora.",
]


def testar_perguntas_combinacoes():
    modos = ["zero_shot", "one_shot", "chain_of_thought"]
    modelos = ["mistral"]

    timestamp = __import__("datetime").datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    timestamp_file = timestamp.replace("/", "_").replace(" ", "_").replace(":", "_")

    filename = f"log/resposta_avaliacao_rag_{timestamp_file}.txt"
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"\n\n[Teste realizado em: {timestamp}]\n\n")
        for idx, pergunta in enumerate(perguntas, start=1):
            file.write(f"\n{'='*100}\nPergunta {idx}: {pergunta}\n{'='*100}\n")
            for modelo in modelos:
                file.write(f"\n##### MODELO: {modelo} #####\n")
                for modo_sql in modos:
                    for modo_tratamento in modos:
                        file.write(
                            f"\n--- SQL: {modo_sql} | Tratamento: {modo_tratamento} ---\n"
                        )
                        try:
                            resposta = get_resposta_rag(
                                pergunta, modo_sql, modo_tratamento, modelo
                            )
                        except Exception as e:
                            resposta = (f"Erro: {e}", "")
                        file.write(f"SQL: {resposta[0]}\n")
                        file.write(f"SAÍDA DO MODELO: {resposta[1]}\n")
            file.write("-" * 100 + "\n")


if __name__ == "__main__":
    testar_perguntas_combinacoes()
