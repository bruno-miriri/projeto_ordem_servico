from django.shortcuts import render, redirect
from .forms import AreaForm, ClienteForm, EquipamentoForm, OrdemServicoForm, FechamentoOSForm, BaixaEquipamentoForm
from django.utils import timezone
from .models import OrdemServico, BaixaEquipamento
import os
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db import connections
from docx import Document
from datetime import datetime
from .documentos import gerar_termo_entrega, gerar_autorizacao_desconto, gerar_termo_baixa
from .notificacoes import enviar_email_os


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def get_dados_cliente(request):
    empresa = request.GET.get('empresa')
    matricula = request.GET.get('matricula')

    if not empresa or not matricula:
        return JsonResponse({'sucesso': False, 'mensagem': 'Empresa ou matrícula não informada.'}, status=400)

    try:
        with connections['oracle'].cursor() as cursor:
            if empresa == 'Miriri':
                query = """
                    SELECT RA_NOME, RA_CIC
                    FROM SRA010
                    WHERE RA_MAT = :matricula
                """
            elif empresa == 'Condomínio':
                query = """
                    SELECT RA_NOME, RA_CIC
                    FROM SRA070
                    WHERE RA_MAT = :matricula
                """
            else:
                return JsonResponse({'sucesso': False, 'mensagem': 'Empresa inválida.'}, status=400)

            cursor.execute(query, {'matricula': matricula})
            resultado = cursor.fetchone()

            if resultado:
                nome, cpf = resultado
                cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
                return JsonResponse({'sucesso': True, 'nome': nome.strip(), 'cpf_formatado': cpf_formatado})
            else:
                return JsonResponse({'sucesso': False, 'mensagem': 'Funcionário não encontrado.'}, status=404)

    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': f'Erro ao consultar Oracle: {str(e)}'}, status=500)

def menu_principal(request):
    return render(request, 'menu.html')

def cadastrar_area(request):
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área cadastrada com sucesso!')
            return redirect('cadastrar_area')
    else:
        form = AreaForm()
    
    return render(request, 'cadastro/cadastrar_area.html', {'form': form})

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ClienteForm

def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()  # ← isso salva no banco de dados
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cadastrar_cliente')
        else:
            messages.error(request, 'Erro ao cadastrar cliente. Verifique os dados informados.')
    else:
        form = ClienteForm()

    return render(request, 'cadastro/cadastrar_cliente.html', {'form': form})


def cadastrar_equipamento(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento cadastrado com sucesso!')
            return redirect('cadastrar_equipamento')  # Redireciona para a mesma tela
        else:
            messages.error(request, 'Erro ao cadastrar equipamento. Verifique os dados.')
    else:
        form = EquipamentoForm()

    return render(request, 'cadastro/cadastrar_equipamento.html', {'form': form})

def cadastrar_ordem_servico(request):
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
            equipamento = form.cleaned_data['equipamento']
            descricao_problema = form.cleaned_data['descricao_problema']
            valor = 0  # valor só será definido no fechamento da OS
            imagem = form.cleaned_data.get('imagem_situacao')

            # Caminho da imagem (se enviada)
            imagem_path = None
            if imagem:
                nome_arquivo = f"{cliente.matricula}_{equipamento.modelo}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{imagem.name.split('.')[-1]}"
                pasta_destino = os.path.join(settings.BASE_DIR, 'imagens_os')
                os.makedirs(pasta_destino, exist_ok=True)
                caminho_completo = os.path.join(pasta_destino, nome_arquivo)

                with open(caminho_completo, 'wb+') as destino:
                    for chunk in imagem.chunks():
                        destino.write(chunk)
                
                imagem_path = f"imagens_os/{nome_arquivo}"

            # Inserção direta no banco
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ordens_servico 
                        (cliente_id, equipamento_id, descricao_problema, status, valor, imagem_situacao) 
                    VALUES (%s, %s, %s, 'aberta', %s, %s)
                """, [cliente.id, equipamento.id, descricao_problema, valor, imagem_path])

                cursor.execute("SELECT LAST_INSERT_ID();")
                os_id = cursor.fetchone()[0]

                # Recupera instância real da OS criada
                ordem_criada = OrdemServico.objects.get(id=os_id)

                enviar_email_os(ordem_criada.cliente, ordem_criada)

                gerar_termo_entrega(cliente, equipamento)            

            messages.success(request, 'Ordem de Serviço cadastrada com sucesso!')
            return redirect('cadastrar_ordem_servico')
        else:
            messages.error(request, 'Erro ao cadastrar OS. Verifique os dados.')
    else:
        form = OrdemServicoForm()

    return render(request, 'cadastro/cadastrar_ordem_servico.html', {'form': form})

def fechar_ordem_servico(request):
    if request.method == 'POST':
        form = FechamentoOSForm(request.POST)
        if form.is_valid():
            ordem_servico = form.cleaned_data['os']
            ordem_servico.valor = form.cleaned_data['valor']
            ordem_servico.status = 'fechada'
            ordem_servico.data_fechamento = timezone.now()
            ordem_servico.save()

            if ordem_servico.valor > 0:
                gerar_autorizacao_desconto(ordem_servico.cliente, ordem_servico.valor)
            
            messages.success(request, f'Ordem de Serviço #{ordem_servico.id} fechada com sucesso!')
            return redirect('fechar_ordem_servico')
        else:
            messages.error(request, 'Erro ao fechar a Ordem de Serviço. Verifique os dados.')
    else:
        form = FechamentoOSForm()

    return render(request, 'cadastro/fechar_ordem_servico.html', {'form': form})


def gerar_documento(modelo_nome, destino_nome, dados):
    caminho_modelo = os.path.join(settings.BASE_DIR, 'cadastro', 'documentos_modelo', modelo_nome)
    doc = Document(caminho_modelo)

    for par in doc.paragraphs:
        for chave, valor in dados.items():
            if chave in par.text:
                par.text = par.text.replace(chave, valor)

    # Criar pasta de saída se necessário
    pasta_saida = os.path.join(settings.BASE_DIR, 'cadastro', 'documentos_gerados')
    os.makedirs(pasta_saida, exist_ok=True)

    caminho_final = os.path.join(pasta_saida, destino_nome)
    doc.save(caminho_final)
    return caminho_final

def registrar_baixa_equipamento(request):
    if request.method == 'POST':
        form = BaixaEquipamentoForm(request.POST)
        if form.is_valid():
            baixa = form.save()

            # Gerar documento da baixa
            gerar_termo_baixa(baixa.cliente, baixa.equipamento, baixa.motivo)

            messages.success(request, 'Baixa de equipamento registrada com sucesso!')
            return redirect('registrar_baixa_equipamento')
        else:
            messages.error(request, 'Erro ao registrar a baixa. Verifique os dados informados.')
    else:
        form = BaixaEquipamentoForm()

    return render(request, 'cadastro/registrar_baixa_equipamento.html', {'form': form})