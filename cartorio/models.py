from django.db import models
from django.contrib.auth.models import User

class Usuario(User):
    is_cartorio = models.BooleanField(default=False)

class Raca(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome



class Propriedade(models.Model):
    nome = models.CharField(max_length=150)
    municipio = models.CharField(max_length=100)
    produtor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='propriedades'
    )

    def __str__(self):
        return f'{self.nome} - ({self.municipio}) - Produtor: {self.produtor.username}'


class Animal(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
        ('N', 'Não definido'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('morto', 'Morto'),
        ('transferido', 'Transferido'),
    ]

    numero_registro = models.CharField(max_length=50, unique=True) # RN01
    nome = models.CharField(max_length=150)
    especie = models.CharField(max_length=100, default='Galinha') # Default species is set to 'Galinha' (Chicken)
    raca = models.ForeignKey(Raca, on_delete=models.PROTECT)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    nascimento = models.DateField()
    propriedade_atual = models.ForeignKey(
        Propriedade, on_delete=models.PROTECT, related_name='animais'
    )

    # Genealogia
    pai = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='filhos_pai'
    )
    mae = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='filhos_mae'
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ativo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.nome} ({self.numero_registro})'

class Transferencia(models.Model):
    STATUS_TRANSF = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
    ]

    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, related_name='transferencias'
    )
    propriedade_origem = models.ForeignKey(
        Propriedade, on_delete=models.PROTECT, related_name='transferencias_saida'
    )
    propriedade_destino = models.ForeignKey(
        Propriedade, on_delete=models.PROTECT, related_name='transferencias_entrada'
    )
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20, choices=STATUS_TRANSF, default='pendente'
    )
    motivo_rejeicao = models.TextField(blank=True, null=True)

    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_decisao = models.DateTimeField(blank=True, null=True)
    analisado_por = models.ForeignKey(
        Usuario,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='analises_realizadas'
    )

    def __str__(self):
        return f'Transferência {self.id} - Animal: {self.animal.nome} ({self.animal.numero_registro}) - Status: {self.status}'

