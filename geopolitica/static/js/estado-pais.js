/**
 * Estado global do "país atual" (currentCountry) do AGPy.
 *
 * O AGPy é uma aplicação multi-página renderizada pelo Django (sem SPA/framework JS),
 * então não existe um "estado de aplicação" em memória que sobreviva entre páginas.
 * O equivalente nesse tipo de arquitetura é persistir o país selecionado no localStorage
 * do navegador: cada página, ao carregar, lê esse valor e propaga o contexto (Mapa
 * destaca o país, Comparar pré-preenche a primeira coluna, Histórico busca sem exigir
 * nova seleção etc.), e cada ponto de seleção (clique no Mapa, resultado da Busca) grava
 * o valor mais atual — reproduzindo, entre requisições HTTP distintas, o efeito de um
 * estado global único.
 *
 * O objeto guardado é sempre a identidade canônica do país (id ISO2 + nome), nunca um
 * alias cru — a normalização de aliases acontece no backend (resolver_pais, em
 * dados_service.py) antes de chegar aqui.
 */
const AGPyEstado = (function () {
    const CHAVE = "agpy_pais_atual";

    function definirPaisAtual(pais) {
        if (!pais || !pais.nome) return;
        const iso2 = (pais.iso2 || "").toLowerCase();
        const registro = {
            id: (pais.id || iso2 || "").toUpperCase(),
            nome: pais.nome,
            iso2: iso2,
            atualizadoEm: Date.now(),
        };
        try {
            localStorage.setItem(CHAVE, JSON.stringify(registro));
        } catch (e) {
            // localStorage pode estar indisponível (navegação privada, cookies bloqueados etc.)
            // Nesse caso a propagação de contexto simplesmente não ocorre — não é um erro fatal.
        }
    }

    function obterPaisAtual() {
        try {
            const bruto = localStorage.getItem(CHAVE);
            return bruto ? JSON.parse(bruto) : null;
        } catch (e) {
            return null;
        }
    }

    function limparPaisAtual() {
        try {
            localStorage.removeItem(CHAVE);
        } catch (e) {
            // ignora
        }
    }

    /** Seleciona, num <select>, a opção cujo value bate exatamente com o país atual. */
    function preencherSelect(select) {
        if (!select) return null;
        const atual = obterPaisAtual();
        if (!atual || !atual.nome) return null;
        const existe = Array.from(select.options).some((o) => o.value === atual.nome);
        if (existe) {
            select.value = atual.nome;
            return atual;
        }
        return null;
    }

    return { definirPaisAtual, obterPaisAtual, limparPaisAtual, preencherSelect };
})();
