"""
Testes automatizados para o sistema AGPy.
Cobre: carregamento de dados, services, models e views.
"""
from django.test import TestCase, Client
from django.urls import reverse

from geopolitica.models import Pais, Indicador, BlocoInternacional, PerfilGeopolitico
from geopolitica.services.dados_service import carregar_dados, get_dado_recente, validar_indicador
from geopolitica.services.analise_service import detectar_tendencia, prever_proximo_ano, classificar_pais_automaticamente


class DadosServiceTest(TestCase):
    """Testes para o serviço centralizado de dados."""

    def test_carregar_dados_retorna_dataframe(self):
        df = carregar_dados()
        self.assertGreater(len(df), 0, "CSV deve conter ao menos 1 país")
        self.assertIn("nome", df.columns)
        self.assertIn("pib", df.columns)

    def test_carregar_dados_contem_novos_indicadores(self):
        df = carregar_dados()
        for col in ["pib_per_capita", "gastos_militares", "divida_publica", "gini", "indice_democracia"]:
            self.assertIn(col, df.columns, f"Coluna '{col}' ausente no CSV")

    def test_get_dado_recente_com_dados_validos(self):
        historico = [
            {"value": None, "date": "2023"},
            {"value": 5.5, "date": "2022"},
        ]
        resultado = get_dado_recente(historico)
        self.assertEqual(resultado, 5.5)

    def test_get_dado_recente_com_divisor(self):
        historico = [{"value": 1000000000, "date": "2023"}]
        resultado = get_dado_recente(historico, divisor=1e9)
        self.assertEqual(resultado, 1.0)

    def test_get_dado_recente_sem_dados(self):
        self.assertIsNone(get_dado_recente(None))
        self.assertIsNone(get_dado_recente([]))

    def test_validar_indicador_valido(self):
        self.assertEqual(validar_indicador("pib"), "pib")
        self.assertEqual(validar_indicador("idh"), "idh")
        self.assertEqual(validar_indicador("gini"), "gini")

    def test_validar_indicador_invalido(self):
        self.assertEqual(validar_indicador("xpto"), "pib")
        self.assertEqual(validar_indicador(""), "pib")


class AnaliseServiceTest(TestCase):
    """Testes para o serviço de análise com Scikit-learn."""

    def test_tendencia_crescente(self):
        anos = [2018, 2019, 2020, 2021, 2022]
        valores = [100, 120, 140, 160, 180]
        tipo, coef = detectar_tendencia(anos, valores)
        self.assertEqual(tipo, "crescente")
        self.assertGreater(coef, 0)

    def test_tendencia_decrescente(self):
        anos = [2018, 2019, 2020, 2021, 2022]
        valores = [180, 160, 140, 120, 100]
        tipo, coef = detectar_tendencia(anos, valores)
        self.assertEqual(tipo, "decrescente")
        self.assertLess(coef, 0)

    def test_tendencia_estavel(self):
        anos = [2018, 2019, 2020, 2021, 2022]
        valores = [100, 100.5, 99.8, 100.2, 100.1]
        tipo, coef = detectar_tendencia(anos, valores)
        self.assertEqual(tipo, "estável")

    def test_previsao_proximo_ano(self):
        anos = [2020, 2021, 2022, 2023]
        valores = [10, 20, 30, 40]
        ano_prev, valor_prev = prever_proximo_ano(anos, valores)
        self.assertEqual(ano_prev, 2024)
        self.assertAlmostEqual(valor_prev, 50, delta=1)

    def test_classificar_superpotencia(self):
        indicadores = {
            "pib": 25000, "gastos_militares": 3.5,
            "nuclear": True, "conselho_p5": True,
            "democracia": 7.85, "idh": 0.92
        }
        classificacao, score, _ = classificar_pais_automaticamente(indicadores)
        self.assertEqual(classificacao, "Superpotência")

    def test_classificar_potencia_media(self):
        indicadores = {
            "pib": 2000, "gastos_militares": 1.3,
            "nuclear": False, "conselho_p5": False,
            "democracia": 8.88, "idh": 0.93
        }
        classificacao, score, _ = classificar_pais_automaticamente(indicadores)
        self.assertIn(classificacao, ["Potência Regional", "Potência Média"])


class ModelsTest(TestCase):
    """Testes para os models Django."""

    def setUp(self):
        self.brasil = Pais.objects.create(
            nome="Brasil Teste",
            codigo_iso2="br",
            codigo_iso3="BRA",
            regiao="América do Sul",
        )

    def test_criar_pais(self):
        self.assertEqual(str(self.brasil), "Brasil Teste")
        self.assertEqual(Pais.objects.count(), 1)

    def test_criar_indicador(self):
        ind = Indicador.objects.create(
            pais=self.brasil, tipo="pib", valor=1920,
            ano=2023, fonte="local", categoria="ECO"
        )
        self.assertEqual(ind.pais.nome, "Brasil Teste")
        self.assertEqual(self.brasil.indicadores.count(), 1)

    def test_criar_bloco(self):
        bloco = BlocoInternacional.objects.create(
            nome="BRICS Teste", tipo="POL"
        )
        bloco.paises.add(self.brasil)
        self.assertEqual(self.brasil.blocos.count(), 1)

    def test_criar_perfil(self):
        perfil = PerfilGeopolitico.objects.create(
            pais=self.brasil,
            classificacao="REG",
            possui_arsenal_nuclear=False,
            membro_conselho_seguranca="ROT",
        )
        self.assertEqual(perfil.get_classificacao_display(), "Potência Regional")


class ViewsTest(TestCase):
    """Testes para as views principais."""

    def setUp(self):
        self.client = Client()

    def test_index_status_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_ranking_status_200(self):
        response = self.client.get("/ranking/")
        self.assertEqual(response.status_code, 200)

    def test_comparar_get_200(self):
        response = self.client.get("/comparar/")
        self.assertEqual(response.status_code, 200)

    def test_graficos_status_200(self):
        response = self.client.get("/graficos/")
        self.assertEqual(response.status_code, 200)

    def test_classificacao_status_200(self):
        response = self.client.get("/classificacao/")
        self.assertEqual(response.status_code, 200)

    def test_buscar_sem_query_200(self):
        response = self.client.get("/buscar/")
        self.assertEqual(response.status_code, 200)

    def test_buscar_com_query_200(self):
        response = self.client.get("/buscar/?q=Brasil")
        self.assertEqual(response.status_code, 200)

    def test_exportar_excel_200(self):
        response = self.client.get("/exportar/excel/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
