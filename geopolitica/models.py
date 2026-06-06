from django.db import models


class Pais(models.Model):
    """
    Representa um país no sistema de análise geopolítica.
    Corresponde à classe 'País' do diagrama de classes do documento.
    """
    nome = models.CharField(max_length=100, unique=True)
    codigo_iso2 = models.CharField(max_length=2, blank=True, default='')
    codigo_iso3 = models.CharField(max_length=3, blank=True, default='')
    regiao = models.CharField(max_length=100)
    sub_regiao = models.CharField(max_length=100, blank=True, default='')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Países"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Indicador(models.Model):
    """
    Representa um indicador econômico, político ou social de um país.
    Inclui o atributo 'ano' para séries temporais, conforme evolução
    descrita no documento de modelagem.
    """
    class Categoria(models.TextChoices):
        ECONOMICO = 'ECO', 'Econômico'
        POLITICO = 'POL', 'Político'
        SOCIAL = 'SOC', 'Social'
        ESTRATEGICO = 'EST', 'Estratégico'

    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='indicadores')
    tipo = models.CharField(max_length=50)  # 'pib', 'idh', 'inflacao', etc.
    valor = models.FloatField()
    ano = models.IntegerField(default=2023)
    fonte = models.CharField(max_length=100, default='local')  # 'World Bank', 'PNUD', 'local'
    categoria = models.CharField(
        max_length=3,
        choices=Categoria.choices,
        default=Categoria.ECONOMICO,
    )
    codigo_api = models.CharField(max_length=50, blank=True, default='')  # Ex: 'NY.GDP.MKTP.CD'
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Indicadores"
        ordering = ['pais', 'tipo', '-ano']
        unique_together = ['pais', 'tipo', 'ano']

    def __str__(self):
        return f"{self.pais.nome} — {self.tipo} ({self.ano}): {self.valor}"


class BlocoInternacional(models.Model):
    """
    Representa organizações e blocos internacionais (OTAN, BRICS, G7, etc.).
    Relação N:N com País — substitui o campo texto livre 'relacoes_internacionais'.
    """
    class TipoBloco(models.TextChoices):
        MILITAR = 'MIL', 'Militar'
        ECONOMICO = 'ECO', 'Econômico'
        POLITICO = 'POL', 'Político'

    nome = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=20, blank=True, default='')
    tipo = models.CharField(
        max_length=3,
        choices=TipoBloco.choices,
        default=TipoBloco.POLITICO,
    )
    descricao = models.TextField(blank=True, default='')
    paises = models.ManyToManyField(Pais, related_name='blocos', blank=True)

    class Meta:
        verbose_name_plural = "Blocos Internacionais"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class PerfilGeopolitico(models.Model):
    """
    Perfil geopolítico de um país com classificação baseada em
    critérios de Relações Internacionais (potência global, regional, etc.).
    """
    class Classificacao(models.TextChoices):
        SUPERPOTENCIA = 'SUP', 'Superpotência'
        GRANDE_POTENCIA = 'GRA', 'Grande Potência'
        POTENCIA_REGIONAL = 'REG', 'Potência Regional'
        POTENCIA_MEDIA = 'MED', 'Potência Média'
        POTENCIA_EMERGENTE = 'EME', 'Potência Emergente'
        ESTADO_FRAGIL = 'FRA', 'Estado Frágil'
        OUTRO = 'OUT', 'Outro'

    class MembroConselho(models.TextChoices):
        PERMANENTE = 'P5', 'Membro Permanente (P5)'
        ROTATIVO = 'ROT', 'Membro Rotativo'
        NAO = 'NAO', 'Não Membro'

    pais = models.OneToOneField(Pais, on_delete=models.CASCADE, related_name='perfil')
    classificacao = models.CharField(
        max_length=3,
        choices=Classificacao.choices,
        default=Classificacao.OUTRO,
    )
    possui_arsenal_nuclear = models.BooleanField(default=False)
    membro_conselho_seguranca = models.CharField(
        max_length=3,
        choices=MembroConselho.choices,
        default=MembroConselho.NAO,
    )
    gastos_militares_pct_pib = models.FloatField(null=True, blank=True, help_text="% do PIB em defesa")
    indice_democracia = models.FloatField(null=True, blank=True, help_text="Economist Intelligence Unit (0-10)")
    disputas_territoriais = models.TextField(blank=True, default='')
    observacoes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = "Perfis Geopolíticos"

    def __str__(self):
        return f"{self.pais.nome} — {self.get_classificacao_display()}"
