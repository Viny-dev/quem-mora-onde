import { useEffect, useState } from "react";
import "./App.css";
import { iniciarPolling } from "./polling.js";

const API = "http://127.0.0.1:8000";

function App() {
  const [jogo, setJogo] = useState(null);
  const [erro, setErro] = useState(null);

  async function iniciarPartida() {
    try {
      const resposta = await fetch(
        `${API}/partida/iniciar`,
        {
          method: "POST",
        },
      );

      if (!resposta.ok) throw new Error("Erro ao iniciar a partida.");
      // O polling e a unica fonte de snapshots, evitando disputa GET/POST.
      setErro(null);
    } catch (error) {
      console.error(error);
      setErro("Não foi possível iniciar a partida.");
    }
  }

  useEffect(() => iniciarPolling({
    url: `${API}/estado`,
    aplicar: (dados) => {
      if (import.meta.env.DEV) {
        console.debug("[estado] recebido", dados, "pecas:", dados.pecas);
      }
      setJogo(dados);
      setErro(null);
    },
    falhar: (error) => {
      console.debug("[estado] nova tentativa automatica", error);
      setErro("Não foi possível conectar ao jogo.");
    },
  }), []);

  useEffect(() => {
    if (import.meta.env.DEV && jogo) {
      console.debug("[estado] aplicado no React; pecas:", jogo.pecas);
    }
  }, [jogo]);

  if (erro) {
    return (
      <main className="game">
        <div className="background" />

        <div className="feedback-overlay">
          <div className="feedback-box error-box">
            <div className="feedback-icon">🔌</div>

            <h2>JOGO DESCONECTADO</h2>

            <p>{erro}</p>
          </div>
        </div>
      </main>
    );
  }

  if (!jogo) {
    return (
      <main className="game">
        <div className="background" />
      </main>
    );
  }

  const {
    estado,
    puzzle,
    pistas,
    tempo_formatado,
    pecas,
    total_pecas,
    mesa_completa,
    tentativas,
    resultado,
  } = jogo;

  const progresso =
    total_pecas > 0
      ? (pecas / total_pecas) * 100
      : 0;

  const aguardando =
    estado === "AGUARDANDO";

  const aguardandoRetirada =
    estado === "AGUARDANDO_RETIRADA";

  const vitoria =
    resultado === "VITORIA";

  const tempoEsgotado =
    resultado === "TEMPO_ESGOTADO";

  function mensagemStatus() {
    if (aguardandoRetirada) {
      return (
        <>
          <strong>RETIRE AS PEÇAS</strong>

          <span>
            Retire todas para liberar um novo desafio.
          </span>
        </>
      );
    }

    if (mesa_completa) {
      return (
        <>
          <strong>BAIRRO COMPLETO!</strong>

          <span>
            Pressione o botão VERIFICAR
          </span>
        </>
      );
    }

    return (
      <>
        <strong>CONTINUE EXPLORANDO</strong>

        <span>
          Cruze as pistas e complete todo o bairro.
        </span>
      </>
    );
  }

  return (
    <main
      className={`game ${
        mesa_completa
          ? "state-completo"
          : ""
      } ${
        aguardandoRetirada
          ? "state-retirada"
          : ""
      }`}
    >
      <div className="background" />

      <header className="game-header">
        <div className="title">
          <span className="house-icon">🏠</span>

          <h1>
            QUEM <span>MORA</span> ONDE?
          </h1>
        </div>

        <div className="subtitle">
          DESAFIO DE LÓGICA
        </div>
      </header>

      {aguardando ? (
        <section className="start-screen">
          <div className="start-card">
            <div className="start-icon">🏘️</div>

            <span>NOVO DESAFIO</span>

            <h2>Quem Mora Onde?</h2>

            <p>
              Observe as pistas, posicione as peças
              e descubra quem mora em cada lugar
              do bairro.
            </p>

            <button onClick={iniciarPartida} disabled={jogo.nfc_status !== "pronto"}>
              {jogo.nfc_status === "pronto" ? "COMEÇAR DESAFIO"
                : jogo.nfc_status === "degradado" ? "AGUARDANDO LEITORES NFC"
                : "INICIALIZANDO NFC..."}
            </button>
          </div>
        </section>
      ) : (
        <>
          <section className="clues-card">
            <div className="wood-title">
              PISTAS NA TELEVISÃO
            </div>

            <div className="puzzle-name">
              {puzzle}
            </div>

            <div className="clues">
              {pistas.map((pista, index) => (
                <div
                  className="clue"
                  key={`${index}-${pista}`}
                >
                  <span
                    className={
                      `clue-number color-${index % 7}`
                    }
                  >
                    {index + 1}
                  </span>

                  <p>{pista}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="timer-card">
            <div className="clock">⏱️</div>

            <div>
              <span>TEMPO</span>

              <strong>
                {tempo_formatado ?? "15:00"}
              </strong>
            </div>
          </section>

          <section className="pieces-card">
            <span className="pieces-title">
              {aguardandoRetirada
                ? "PEÇAS RESTANTES"
                : "PEÇAS POSICIONADAS"}
            </span>

            <div className="pieces-count">
              <span className="puzzle-icon">
                🧩
              </span>

              <strong>{pecas}</strong>

              <span>/ {total_pecas}</span>
            </div>

            <div className="progress">
              <div
                className="progress-fill"
                style={{
                  width: `${progresso}%`,
                }}
              />
            </div>

            <div
              className={
                `message ${
                  aguardandoRetirada
                    ? "message-retirada"
                    : mesa_completa
                      ? "message-completo"
                      : ""
                }`
              }
            >
              {mensagemStatus()}
            </div>
          </section>
        </>
      )}

      {vitoria && (
        <div className="feedback-overlay victory-feedback">
          <div className="confetti confetti-one">
            ●
          </div>

          <div className="confetti confetti-two">
            ★
          </div>

          <div className="confetti confetti-three">
            ●
          </div>

          <div className="confetti confetti-four">
            ★
          </div>

          <div className="feedback-box victory-box">
            <div className="victory-stars">
              ★ ★ ★
            </div>

            <span>PARABÉNS!</span>

            <h2>BAIRRO DESVENDADO!</h2>

            <p>
              Você descobriu quem mora
              <br />
              em cada lugar do bairro!
            </p>

            <div className="victory-stats">
              <div>
                <span>TEMPO RESTANTE</span>

                <strong>
                  {tempo_formatado}
                </strong>
              </div>

              <div>
                <span>TENTATIVAS</span>

                <strong>{tentativas}</strong>
              </div>
            </div>

            <div className="remove-warning">
              🧩 Agora retire todas as peças da mesa
            </div>
          </div>
        </div>
      )}

      {tempoEsgotado && (
        <div className="feedback-overlay error-feedback">
          <div className="feedback-box error-box">
            <div className="feedback-icon">
              ⏰
            </div>

            <span>FIM DE JOGO</span>

            <h2>TEMPO ESGOTADO!</h2>

            <p>
              Retire todas as peças para
              iniciar um novo desafio.
            </p>
          </div>
        </div>
      )}
    </main>
  );
}

export default App;