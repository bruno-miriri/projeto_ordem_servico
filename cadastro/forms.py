from django import forms
from .models import Area, Cliente, Equipamento, OrdemServico, BaixaEquipamento
from django.utils import timezone

from django import forms
from .models import Area

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['area', 'responsavel_area']
        labels = {
            'area': 'Nome da Área',
            'responsavel_area': 'Responsável',
        }


class ClienteForm(forms.ModelForm):
    nome = forms.CharField(required=False)
    cpf = forms.CharField(required=False)

    class Meta:
        model = Cliente
        fields = ['empresa', 'matricula', 'nome', 'cpf', 'ugb', 'telefone', 'email']
        labels = {
            'empresa': 'Empresa',
            'matricula': 'Matrícula',
            'nome': 'Nome completo',
            'cpf': 'CPF',
            'ugb': 'UGB',
            'telefone': 'Telefone',
            'email': 'E-mail',
        }
        widgets = {
            'cpf': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': '000.000.000-00'
            }),
            'nome': forms.TextInput(attrs={
                'readonly': 'readonly'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(83) 99999-9999',
                'maxlength': '15',
                'inputmode': 'numeric'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@dominio.com'
            }),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        return cpf.replace('.', '').replace('-', '')

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '')
        telefone_numerico = ''.join(filter(str.isdigit, telefone))

        if len(telefone_numerico) != 11:
            raise forms.ValidationError("O telefone deve conter 11 dígitos numéricos (incluindo DDD).")

        return telefone_numerico


class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ['tipo', 'modelo', 'numero_serie', 'responsavel', 'status', 'area']
        labels = {
            'tipo': 'Tipo do Equipamento',
            'modelo': 'Modelo',
            'numero_serie': 'Número de Série',
            'responsavel': 'Nome do Responsável',
            'status': 'Status',
            'area': 'Área',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].label_from_instance = lambda obj: f"{obj.responsavel_area} - {obj.area}"

class OrdemServicoForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        label="Cliente",
        widget=forms.Select(),
    )

    equipamento = forms.ModelChoiceField(
        queryset=Equipamento.objects.all(),
        label="Equipamento",
        widget=forms.Select(),
    )

    descricao_problema = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Descrição do Problema"
    )

    imagem_situacao = forms.FileField(
        label="Foto da Situação do Equipamento",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Exibir cliente como "matrícula - nome"
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.matricula} - {obj.nome}"

        # Exibir equipamento como "modelo - responsável"
        self.fields['equipamento'].label_from_instance = lambda obj: f"{obj.modelo} - {obj.responsavel}"

class FechamentoOSForm(forms.Form):
    os = forms.ModelChoiceField(
        queryset=OrdemServico.objects.filter(status='aberta'),
        label='Selecione a OS',
        required=True
    )
    valor = forms.DecimalField(
        label='Valor do Serviço (R$)',
        min_value=0,
        decimal_places=2,
        max_digits=10
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['os'].label_from_instance = lambda obj: (
            f"OS {obj.id} - {obj.cliente.nome} - {obj.equipamento.modelo} ({obj.equipamento.responsavel})"
        )
    os = forms.ModelChoiceField(
        queryset=OrdemServico.objects.filter(status='aberta'),
        label='Selecione a OS',
        required=True
    )
    valor = forms.DecimalField(min_value=0, decimal_places=2, label='Valor do Serviço')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza a forma como cada OS será exibida no select
        self.fields['os'].label_from_instance = lambda obj: (
            f"{obj.id} - {obj.equipamento.modelo} - {obj.equipamento.responsavel}"
        )

class BaixaEquipamentoForm(forms.ModelForm):
    class Meta:
        model = BaixaEquipamento
        fields = ['equipamento', 'cliente', 'motivo', 'observacao']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Informe o motivo da devolução'}),
            'observacao': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Observações adicionais (opcional)'}),
        }