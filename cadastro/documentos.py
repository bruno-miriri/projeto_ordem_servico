import os
from datetime import datetime
from django.conf import settings
from docx import Document

def gerar_documento(modelo_nome, destino_nome, dados):
    caminho_modelo = os.path.join(settings.BASE_DIR, 'cadastro', 'documentos_modelo', modelo_nome)
    doc = Document(caminho_modelo)

    for par in doc.paragraphs:
        for chave, valor in dados.items():
            if chave in par.text:
                par.text = par.text.replace(chave, valor)

    pasta_saida = os.path.join(settings.BASE_DIR, 'cadastro', 'documentos_gerados')
    os.makedirs(pasta_saida, exist_ok=True)

    caminho_final = os.path.join(pasta_saida, destino_nome)
    doc.save(caminho_final)
    return caminho_final

def gerar_termo_entrega(cliente, equipamento):
    dados = {
        '{{data}}': datetime.now().strftime('%d/%m/%Y'),
        '{{nome}}': cliente.nome,
        '{{matricula}}': cliente.matricula,
        '{{cpf}}': cliente.cpf,
        '{{modelo}}': equipamento.modelo,
        '{{numero_serie}}': equipamento.numero_serie,
        '{{area}}': equipamento.area.area,
        '{{responsavel_area}}': equipamento.area.responsavel_area,
    }
    nome_arquivo = f"termo_entrega_os_{cliente.matricula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return gerar_documento('termo_responsabilidade_modelo.docx', nome_arquivo, dados)

def gerar_autorizacao_desconto(cliente, valor_total):
    parcelas = 2
    valor_parcela = valor_total / parcelas
    data_atual = datetime.now()
    dados = {
        '{{data}}': data_atual.strftime('%d/%m/%Y'),
        '{{valor}}': f"{valor_total:.2f}".replace('.', ','),
        '{{num_parcelas}}': str(parcelas),
        '{{valor/num_parcelas}}': f"{valor_parcela:.2f}".replace('.', ','),
        '{{mês}}': data_atual.strftime('%m'),
        '{{ano}}': data_atual.strftime('%Y'),
        '{{nome}}': cliente.nome,
        '{{matricula}}': cliente.matricula,
        '{{cpf}}': cliente.cpf
    }
    nome_arquivo = f"autorizacao_desconto_os_{cliente.matricula}_{data_atual.strftime('%Y%m%d_%H%M%S')}.docx"
    return gerar_documento('autorizacao_desconto_modelo.docx', nome_arquivo, dados)

def gerar_termo_baixa(cliente, equipamento, motivo):
    dados = {
        '{{data}}': datetime.now().strftime('%d/%m/%Y'),
        '{{nome}}': cliente.nome,
        '{{matricula}}': cliente.matricula,
        '{{cpf}}': cliente.cpf,
        '{{modelo}}': equipamento.modelo,
        '{{numero_serie}}': equipamento.numero_serie,
        '{{responsavel_area}}': equipamento.area.responsavel_area,
        '{{motivo}}': motivo,
    }
    nome_arquivo = f"termo_baixa_{cliente.matricula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return gerar_documento('termo_baixa_equipamento_modelo.docx', nome_arquivo, dados)
