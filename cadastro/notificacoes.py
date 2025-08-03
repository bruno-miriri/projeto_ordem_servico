from django.core.mail import send_mail

def enviar_email_os(cliente, os):
    if not cliente.email:
        return  # evita erro se o e-mail estiver vazio

    # Se a OS ainda não foi fechada, data será "Não finalizada"
    data_fechamento = os.data_fechamento.strftime('%d/%m/%Y %H:%M') if os.data_fechamento else 'Não finalizada'

    # Define título diferente conforme status
    if os.status == 'fechada':
        assunto = f"Fechamento da Ordem de Serviço #{os.id} - Miriri"
    else:
        assunto = f"Abertura da Ordem de Serviço #{os.id} - Miriri"

    mensagem = (
        f"Olá, {cliente.nome}.\n\n"
        f"A Ordem de Serviço #{os.id} foi registrada no sistema.\n\n"
        f"Detalhes:\n"
        f"• Equipamento: {os.equipamento.modelo} (nº série: {os.equipamento.numero_serie})\n"
        f"• Descrição do problema: {os.descricao_problema}\n"
        f"• Status: {os.status}\n"
        #f"• Valor do serviço: R$ {os.valor:.2f}\n"
        f"• Data de fechamento: {data_fechamento}\n\n"
        f"Obrigado por utilizar o sistema de Ordens de Serviço da Miriri.\n"
        f"Em caso de dúvidas, entre em contato com nossa equipe técnica.\n\n"
        f"Atenciosamente,\n"
        f"Equipe de Suporte Técnico\n"
        f"Miriri Alimentos e Bioenergia S/A."
    )

    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=None,  # usa DEFAULT_FROM_EMAIL do settings.py
        recipient_list=[cliente.email],
        fail_silently=False,
    )
