from django.db import models

class Area(models.Model):
    area = models.CharField(max_length=100, db_column='area')
    responsavel_area = models.CharField(max_length=100, db_column='responsavel_area')

    def __str__(self):
        return f"{self.responsavel_area} - {self.area}"

    class Meta:
        managed = False  # Django não criará nem alterará a tabela
        db_table = 'areas'


class Cliente(models.Model):
    empresa = models.CharField(max_length=20, choices=[('Miriri', 'Miriri'), ('Condomínio', 'Condomínio')])
    matricula = models.CharField(max_length=20)
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    ugb = models.CharField(max_length=20)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()

    class Meta:
        db_table = 'clientes'  # ← Nome exato da tabela no banco

    def __str__(self):
        return f"{self.nome} ({self.matricula})"
    

class Equipamento(models.Model):
    TIPOS = [
        ('Celular', 'Celular'),
        ('Tablet', 'Tablet'),
        ('Notebook', 'Notebook'),
    ]

    STATUS = [
        ('Ativo', 'Ativo'),
        ('Inativo', 'Inativo'),
        ('Devolução', 'Devolução')
    ]

    tipo = models.CharField(max_length=10, choices=TIPOS, db_column='tipo_equipamento')
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=50)
    responsavel = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS)
    area = models.ForeignKey('Area', on_delete=models.PROTECT)

    class Meta:
        db_table = 'equipamentos'  # ← Nome exato da tabela no banco

    def __str__(self):
        return f"{self.tipo} - {self.modelo} ({self.numero_serie})"

class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('fechada', 'Fechada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    descricao_problema = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aberta')
    data_abertura = models.DateTimeField(blank=True, null=True)
    data_fechamento = models.DateTimeField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagem_situacao = models.CharField(max_length=255)

    class Meta:
        db_table = 'ordens_servico'

    def __str__(self):
        return f"OS #{self.id} - {self.equipamento.modelo} - {self.equipamento.responsavel}"

class BaixaEquipamento(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_baixa = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'baixas_equipamentos'

    def __str__(self):
        return f"Baixa de {self.equipamento.modelo} ({self.cliente.nome}) em {self.data_baixa.strftime('%d/%m/%Y')}"