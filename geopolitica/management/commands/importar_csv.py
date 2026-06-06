"""
Management command para importar os dados do CSV para o banco de dados Django.
Popula os models Pais, Indicador, BlocoInternacional e PerfilGeopolitico.
"""
import pandas as pd
from pathlib import Path
from django.core.management.base import BaseCommand
from geopolitica.models import Pais, Indicador, BlocoInternacional, PerfilGeopolitico


# Dados de coordenadas para geolocalização
COORDENADAS = {
    "Brasil": {"lat": -14.2350, "lng": -51.9253, "iso2": "br", "iso3": "BRA", "sub_regiao": "América do Sul"},
    "Estados Unidos": {"lat": 37.0902, "lng": -95.7129, "iso2": "us", "iso3": "USA", "sub_regiao": "América do Norte"},
    "China": {"lat": 35.8617, "lng": 104.1954, "iso2": "cn", "iso3": "CHN", "sub_regiao": "Ásia Oriental"},
    "Alemanha": {"lat": 51.1657, "lng": 10.4515, "iso2": "de", "iso3": "DEU", "sub_regiao": "Europa Ocidental"},
    "Índia": {"lat": 20.5937, "lng": 78.9629, "iso2": "in", "iso3": "IND", "sub_regiao": "Ásia Meridional"},
    "Japão": {"lat": 36.2048, "lng": 138.2529, "iso2": "jp", "iso3": "JPN", "sub_regiao": "Ásia Oriental"},
    "Canadá": {"lat": 56.1304, "lng": -106.3468, "iso2": "ca", "iso3": "CAN", "sub_regiao": "América do Norte"},
    "França": {"lat": 46.2276, "lng": 2.2137, "iso2": "fr", "iso3": "FRA", "sub_regiao": "Europa Ocidental"},
    "Reino Unido": {"lat": 55.3781, "lng": -3.4360, "iso2": "gb", "iso3": "GBR", "sub_regiao": "Europa Setentrional"},
    "Austrália": {"lat": -25.2744, "lng": 133.7751, "iso2": "au", "iso3": "AUS", "sub_regiao": "Oceania"},
}

# Dados de perfil geopolítico (fontes: SIPRI 2023, EIU 2023, dados públicos)
PERFIS = {
    "Brasil": {
        "classificacao": "REG",
        "nuclear": False,
        "conselho": "ROT",
        "gastos_mil": 1.2,
        "democracia": 6.68,
        "disputas": "",
        "obs": "Líder regional sul-americano, membro fundador do BRICS e participante ativo do G20."
    },
    "Estados Unidos": {
        "classificacao": "SUP",
        "nuclear": True,
        "conselho": "P5",
        "gastos_mil": 3.5,
        "democracia": 7.85,
        "disputas": "",
        "obs": "Única superpotência global com projeção militar em todos os continentes."
    },
    "China": {
        "classificacao": "GRA",
        "nuclear": True,
        "conselho": "P5",
        "gastos_mil": 1.7,
        "democracia": 2.12,
        "disputas": "Mar do Sul da China, Taiwan, fronteira Índia-China (Aksai Chin)",
        "obs": "Potência em ascensão com ambições de paridade estratégica com os EUA."
    },
    "Alemanha": {
        "classificacao": "GRA",
        "nuclear": False,
        "conselho": "ROT",
        "gastos_mil": 1.5,
        "democracia": 8.80,
        "disputas": "",
        "obs": "Motor econômico da União Europeia, poder normativo e institucional significativo."
    },
    "Índia": {
        "classificacao": "EME",
        "nuclear": True,
        "conselho": "ROT",
        "gastos_mil": 2.4,
        "democracia": 7.04,
        "disputas": "Caxemira (com Paquistão), Aksai Chin e Arunachal Pradesh (com China)",
        "obs": "Maior democracia do mundo por população, potência emergente no BRICS."
    },
    "Japão": {
        "classificacao": "GRA",
        "nuclear": False,
        "conselho": "ROT",
        "gastos_mil": 1.2,
        "democracia": 8.33,
        "disputas": "Ilhas Curilas (com Rússia), Ilhas Senkaku/Diaoyu (com China)",
        "obs": "Terceira maior economia, aliado estratégico dos EUA no Indo-Pacífico."
    },
    "Canadá": {
        "classificacao": "MED",
        "nuclear": False,
        "conselho": "ROT",
        "gastos_mil": 1.3,
        "democracia": 8.88,
        "disputas": "Passagem do Noroeste (soberania ártica)",
        "obs": "Potência média com forte atuação multilateral e em peacekeeping."
    },
    "França": {
        "classificacao": "GRA",
        "nuclear": True,
        "conselho": "P5",
        "gastos_mil": 1.9,
        "democracia": 8.07,
        "disputas": "",
        "obs": "Membro permanente do Conselho de Segurança, projeção militar na África e Indo-Pacífico."
    },
    "Reino Unido": {
        "classificacao": "GRA",
        "nuclear": True,
        "conselho": "P5",
        "gastos_mil": 2.3,
        "democracia": 8.54,
        "disputas": "Gibraltar (com Espanha), Malvinas/Falklands (com Argentina)",
        "obs": "Potência nuclear com rede global de alianças (Five Eyes, AUKUS, OTAN)."
    },
    "Austrália": {
        "classificacao": "MED",
        "nuclear": False,
        "conselho": "ROT",
        "gastos_mil": 2.0,
        "democracia": 8.71,
        "disputas": "",
        "obs": "Aliado chave no Indo-Pacífico, membro do AUKUS e Five Eyes."
    },
}

# Blocos internacionais e seus membros
BLOCOS = {
    "G7": {"tipo": "POL", "desc": "Grupo dos 7 países mais industrializados", "membros": ["Estados Unidos", "Canadá", "Reino Unido", "França", "Alemanha", "Japão"]},
    "G20": {"tipo": "POL", "desc": "Grupo das 20 maiores economias do mundo", "membros": ["Brasil", "Estados Unidos", "China", "Alemanha", "Índia", "Japão", "Canadá", "França", "Reino Unido", "Austrália"]},
    "BRICS": {"tipo": "POL", "desc": "Bloco de economias emergentes (Brasil, Rússia, Índia, China, África do Sul + novos membros)", "membros": ["Brasil", "China", "Índia"]},
    "OTAN": {"tipo": "MIL", "desc": "Organização do Tratado do Atlântico Norte — aliança militar ocidental", "membros": ["Estados Unidos", "Canadá", "Reino Unido", "França", "Alemanha"]},
    "União Europeia": {"tipo": "ECO", "desc": "Bloco econômico e político europeu", "membros": ["Alemanha", "França"]},
    "AUKUS": {"tipo": "MIL", "desc": "Pacto trilateral de segurança Austrália-Reino Unido-Estados Unidos", "membros": ["Austrália", "Reino Unido", "Estados Unidos"]},
    "Five Eyes": {"tipo": "MIL", "desc": "Aliança de inteligência anglófona", "membros": ["Estados Unidos", "Reino Unido", "Canadá", "Austrália"]},
    "Mercosul": {"tipo": "ECO", "desc": "Mercado Comum do Sul", "membros": ["Brasil"]},
    "QUAD": {"tipo": "MIL", "desc": "Diálogo de Segurança Quadrilateral (EUA, Japão, Índia, Austrália)", "membros": ["Estados Unidos", "Japão", "Índia", "Austrália"]},
}


class Command(BaseCommand):
    help = "Importa dados do CSV e dados geopolíticos complementares para o banco de dados Django."

    def handle(self, *args, **options):
        csv_path = Path(__file__).resolve().parent.parent.parent.parent / "dados" / "paises.csv"
        
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV não encontrado: {csv_path}"))
            return

        df = pd.read_csv(csv_path)
        self.stdout.write(f"Lendo {len(df)} países do CSV...")

        # === 1. Criar/atualizar países ===
        for _, row in df.iterrows():
            nome = row["nome"]
            geo = COORDENADAS.get(nome, {})

            pais, created = Pais.objects.update_or_create(
                nome=nome,
                defaults={
                    "codigo_iso2": geo.get("iso2", ""),
                    "codigo_iso3": geo.get("iso3", ""),
                    "regiao": row["regiao"],
                    "sub_regiao": geo.get("sub_regiao", ""),
                    "latitude": geo.get("lat"),
                    "longitude": geo.get("lng"),
                },
            )
            status = "CRIADO" if created else "ATUALIZADO"
            self.stdout.write(f"  {status}: {pais.nome}")

            # === 2. Criar indicadores do CSV ===
            indicadores_csv = {
                "pib": ("ECO", "NY.GDP.MKTP.CD"),
                "inflacao": ("ECO", "FP.CPI.TOTL.ZG"),
                "idh": ("SOC", ""),
                "estabilidade": ("POL", "PV.EST"),
            }

            for tipo, (cat, codigo) in indicadores_csv.items():
                valor = row.get(tipo)
                if pd.notna(valor):
                    Indicador.objects.update_or_create(
                        pais=pais, tipo=tipo, ano=2023,
                        defaults={
                            "valor": float(valor),
                            "fonte": "local (CSV)",
                            "categoria": cat,
                            "codigo_api": codigo,
                        },
                    )

            # Indicador: relacoes_internacionais (texto, armazena como observação)
            ri = row.get("relacoes_internacionais", "")

            # === 3. Criar perfil geopolítico ===
            perfil_data = PERFIS.get(nome)
            if perfil_data:
                PerfilGeopolitico.objects.update_or_create(
                    pais=pais,
                    defaults={
                        "classificacao": perfil_data["classificacao"],
                        "possui_arsenal_nuclear": perfil_data["nuclear"],
                        "membro_conselho_seguranca": perfil_data["conselho"],
                        "gastos_militares_pct_pib": perfil_data["gastos_mil"],
                        "indice_democracia": perfil_data["democracia"],
                        "disputas_territoriais": perfil_data["disputas"],
                        "observacoes": perfil_data["obs"],
                    },
                )
                self.stdout.write(f"    Perfil geopolítico: {perfil_data['classificacao']}")

        # === 4. Criar blocos internacionais ===
        self.stdout.write("\nCriando blocos internacionais...")
        for nome_bloco, info in BLOCOS.items():
            bloco, created = BlocoInternacional.objects.update_or_create(
                nome=nome_bloco,
                defaults={
                    "tipo": info["tipo"],
                    "descricao": info["desc"],
                },
            )
            # Associar países ao bloco
            for nome_pais in info["membros"]:
                try:
                    pais_obj = Pais.objects.get(nome=nome_pais)
                    bloco.paises.add(pais_obj)
                except Pais.DoesNotExist:
                    self.stdout.write(f"    AVISO: País '{nome_pais}' não encontrado para bloco '{nome_bloco}'")

            status = "CRIADO" if created else "ATUALIZADO"
            self.stdout.write(f"  {status}: {bloco.nome} ({len(info['membros'])} membros)")

        # === Resumo ===
        self.stdout.write(self.style.SUCCESS(
            f"\nImportação concluída!"
            f"\n  Países: {Pais.objects.count()}"
            f"\n  Indicadores: {Indicador.objects.count()}"
            f"\n  Blocos: {BlocoInternacional.objects.count()}"
            f"\n  Perfis: {PerfilGeopolitico.objects.count()}"
        ))
