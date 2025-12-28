from flask import json
import re

def dados_valores(dados_valores, viagem):

    valores = json.dumps(
        [
            {
                "bandeira": valor.bandeira,
                "valor_min": float(valor.valor_min),
                "valor_km": float(valor.valor_km),
                "valor_minimo": float(valor.valor_minimo),
                "valor_base": float(valor.valor_base),
            }
            for valor in dados_valores
        ],
        ensure_ascii=False,
        indent=4,
    )

    valores_viagem = json.dumps(
        [
            {
                "bandeira": valor.bandeira,
                "valor_min": float(valor.valor_min),
                "valor_km": float(valor.valor_km),
                "valor_minimo": float(valor.valor_minimo),
                "valor_base": float(valor.valor_base),
            }
            for valor in viagem
        ],
        ensure_ascii=False,
        indent=4,
    )

    return valores, valores_viagem


def is_valid_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def is_valid_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro.

    Regras:
      - Deve conter 11 dígitos numéricos.
      - Não pode ser sequência de dígitos repetidos.
      - Os dois últimos dígitos devem obedecer ao cálculo do dígito verificador.
    """
    # 1) Remove tudo que não for dígito
    cpf_digits = re.sub(r"\D", "", cpf)

    # 2) Deve ter exatamente 11 dígitos
    if len(cpf_digits) != 11:
        return False

    # 3) Não pode ser sequência de mesmo dígito
    if cpf_digits == cpf_digits[0] * 11:
        return False

    # Função para cálculo de dígito verificador
    def calc_digit(digs: str, weights: list[int]) -> int:
        s = sum(int(digs[i]) * weights[i] for i in range(len(weights)))
        d = (s * 10) % 11
        return 0 if d == 10 else d

    # 4) Pesos para os dígitos
    first_weights  = list(range(10, 1, -1))  # [10,9,8,7,6,5,4,3,2]
    second_weights = list(range(11, 1, -1))  # [11,10,9,8,7,6,5,4,3,2]

    # 5) Compara dígitos calculados com os informados
    dv1 = calc_digit(cpf_digits[:9],  first_weights)
    dv2 = calc_digit(cpf_digits[:10], second_weights)

    return dv1 == int(cpf_digits[9]) and dv2 == int(cpf_digits[10])
