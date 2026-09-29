// Uma consulta por vez; o proximo ciclo sempre e agendado no finally.
export function iniciarPolling({ url, aplicar, falhar, intervalo = 500, timeout = 3000 }) {
  let ativo = true;
  let proximo;
  let controller;

  async function consultar() {
    controller = new AbortController();
    const limite = setTimeout(() => controller.abort(), timeout);
    try {
      const resposta = await fetch(url, {
        signal: controller.signal,
        cache: "no-store",
      });
      if (!resposta.ok) throw new Error(`GET /estado: ${resposta.status}`);
      const dados = await resposta.json();
      if (!dados || typeof dados !== "object" ||
          !Number.isFinite(dados.pecas) || !Array.isArray(dados.pistas)) {
        throw new Error("Resposta /estado invalida");
      }
      if (ativo) aplicar(dados);
    } catch (error) {
      if (ativo) falhar(error);
    } finally {
      clearTimeout(limite);
      if (ativo) proximo = setTimeout(consultar, intervalo);
    }
  }

  void consultar();
  return () => {
    ativo = false;
    clearTimeout(proximo);
    controller.abort();
  };
}
