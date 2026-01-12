from jinja2 import Environment
import os
from datetime import datetime, timedelta
# from src.blueprints.fechamento.consultas import ConsultarCorrida


# Filtro para formatar números
def format_number(value):
    try:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return value


# def gerar_faturas_mysql():

    # Período de 7 dias
    data_fim = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    data_inicio = data_fim - timedelta(days=7)

    # Carregar template HTML
    with open("fatura.html", "r", encoding="utf-8") as f:
        modelo_html = f.read()

    env = Environment()
    env.filters["format_number"] = format_number
    template = env.from_string(modelo_html)

    # Criar diretório de saída
    diretorio = "faturas_motoristas"
    os.makedirs(diretorio, exist_ok=True)

    # Buscar todos os motoristas
    motoristas = ConsultarCorrida.busca_corridas_periodo()

    for motorista in motoristas:
        motorista_id = motorista["id"]
        nome = motorista["nome"]

        corridas = ConsultarCorrida.busca_corridas_periodo(
            motorista_id=motorista_id, data_inicio=data_inicio, data_fim=data_fim
        )

        if not corridas:
            continue

        # Buscar comissão padrão
        comissao_padrao = motorista.get("comissao_padrao", 15)

        # Processar corridas
        detalhes = []
        valor_total_corridas = 0
        total_descontos = 0
        valor_total_comissao = 0

        for c in corridas:
            valor = float(c.valor)
            via = c.via
            data_formatada = c.data_hora.strftime("%d/%m/%Y %H:%M")

            if valor < 0:
                desconto = abs(valor)
                total_descontos += desconto
                valor_total_corridas += desconto
                comissao_corrida = -desconto
            else:
                comissao_corrida = valor * comissao_padrao / 100
                valor_total_corridas += valor
                valor_total_comissao += comissao_corrida

            detalhes.append(
                {
                    "valor_corrida": format_number(valor),
                    "comissao_corrida": format_number(comissao_corrida),
                    "data": data_formatada,
                    "via": via,
                }
            )

        detalhes.sort(key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y %H:%M"))

        # Benefício para faturamento acima de 2000
        if comissao_padrao == 15 and valor_total_corridas >= 2000:
            comissao_padrao = 10

        valor_total_comissao = (
            valor_total_corridas * comissao_padrao / 100
        ) - total_descontos
        valor_total_comissao = max(valor_total_comissao, 50)

        html = template.render(
            nome=nome,
            total_corridas=len(corridas),
            valor_total_corridas=format_number(valor_total_corridas),
            valor_total_comissao=format_number(valor_total_comissao),
            detalhes_corridas=detalhes,
        )

        caminho_html = os.path.join(diretorio, f"{nome}.html")
        with open(caminho_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Fatura gerada para {nome}: {caminho_html}")
