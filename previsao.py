import pandas as pd
import math
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from database_handler import DatabaseHandler


class Previsor:

    def treinar_modelo(self, df):
        features = [
            "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)",
            "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)",
            "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)",
            
       
            "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
            'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
            'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',

            "TEMPERATURA DO PONTO DE ORVALHO (°C)",
            'TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)',
            'TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)',


            "UMIDADE RELATIVA DO AR, HORARIA (%)",
            'UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)',
            'UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)'
        ]
        X = df[features].dropna()      
        y = df["CHUVA"].loc[X.index]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        self.model = RandomForestClassifier(n_estimators=500 , random_state=42,
                                            class_weight='balanced')
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        probabilidade = self.model.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred)

    def get_previsao(self, dados):
        if not hasattr(self, 'model'):
            raise Exception("Modelo não treinado. Por favor, treine o modelo antes de fazer previsões.")
        previsao = self.model.predict(dados)
        probabilidade = self.model.predict_proba(dados)[:, 1]
        return {
            "chuva": True if previsao[0] == 1 else False,
            "probabilidade_chuva": f"{probabilidade:.2}",
            "probabilidade_chuva_percentual": f"{probabilidade[0] * 100:.2f}%",
        }


df = pd.read_csv(
    "dataset\INMET_SE_RJ_A601_SEROPEDICA-ECOLOGIA AGRICOLA_01-01-2024_A_31-12-2024.CSV",
    delimiter=";",
    decimal=",",
    encoding="latin-1",
    skiprows=8,
)

df["CHUVA"] = df["PRECIPITAÇÃO TOTAL, HORÁRIO (mm)"].apply(lambda x: 1 if x > 0 else 0)

previsor = Previsor()
previsor.treinar_modelo(df)
