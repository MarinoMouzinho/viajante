
const sessionTabs = document.getElementById("sessionTabs");
const newSessionButton = document.getElementById("newSessionButton");
const clearSessionButton = document.getElementById("clearSessionButton");

const sessionIdElement = document.getElementById("sessionId");
const sessionClientElement = document.getElementById("sessionClient");
const sessionStatusElement = document.getElementById("sessionStatus");
const sessionCreatedAtElement = document.getElementById("sessionCreatedAt");

const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendMessageButton = document.getElementById("sendMessageButton");

let sessoes = [];
let sessaoAtiva = null;

async function requisicao(url, opcoes = {}) {
    const resposta = await fetch(url, {
        headers: {
            "Content-Type": "application/json"
        },
        ...opcoes
    });

    const dados = await resposta.json();

    if (!resposta.ok || !dados.sucesso) {
        throw new Error(dados.erro || "Erro na comunicação com o servidor.");
    }

    return dados;
}


function formatarData(data) {
    return new Date(data).toLocaleString("pt-BR");
}

function atualizarInformacoesSessao(sessao) {
    if (!sessao) {
        sessionIdElement.textContent = "--";
        sessionClientElement.textContent = "--";
        sessionStatusElement.textContent = "Aguardando";
        sessionCreatedAtElement.textContent = "--";

        clearSessionButton.disabled = true;
        return;
    }

    sessionIdElement.textContent = sessao.id;
    sessionClientElement.textContent = sessao.cliente;
    sessionStatusElement.textContent = sessao.estado;
    sessionCreatedAtElement.textContent = formatarData(sessao.criada_em);

    clearSessionButton.disabled = false;
}


function renderizarAbas() {
    sessionTabs.replaceChildren();

    sessoes.forEach(sessao => {
        const aba = document.createElement("div");
        aba.className = "session-tab";

        if (sessao.id === sessaoAtiva) {
            aba.classList.add("active");
        }

        const nome = document.createElement("button");
        nome.type = "button";
        nome.className = "session-tab-name";
        nome.textContent = sessao.cliente;

        nome.addEventListener("click", () => {
            selecionarSessao(sessao.id);
        });

        const fechar = document.createElement("button");
        fechar.type = "button";
        fechar.className = "session-tab-close";
        fechar.textContent = "×";
        fechar.title = "Encerrar sessão";

        fechar.addEventListener("click", event => {
            event.stopPropagation();
            encerrarSessao(sessao.id);
        });

        aba.append(nome, fechar);
        sessionTabs.appendChild(aba);
    });
}


async function carregarSessoes() {
    try {
        const dados = await requisicao("/api/sessoes");

        sessoes = dados.sessoes;

        if (
            sessaoAtiva &&
            !sessoes.some(sessao => sessao.id === sessaoAtiva)
        ) {
            sessaoAtiva = null;
        }

        renderizarAbas();

        if (sessaoAtiva) {
            atualizarInformacoesSessao(
                sessoes.find(sessao => sessao.id === sessaoAtiva)
            );
        } else {
            atualizarInformacoesSessao(null);
        }

    } catch (erro) {
        alert(erro.message);
    }
}



async function criarSessao() {
    try {
        const dados = await requisicao("/api/sessoes", {
            method: "POST"
        });

        sessoes.push(dados.sessao);
        sessaoAtiva = dados.sessao.id;

        renderizarAbas();
        atualizarInformacoesSessao(dados.sessao);

        messageInput.disabled = false;
        sendMessageButton.disabled = false;

        await carregarMensagens(sessaoAtiva);

        messageInput.focus();

    } catch (erro) {
        alert(erro.message);
    }
}

async function selecionarSessao(sessaoId) {
    const sessao = sessoes.find(item => item.id === sessaoId);
    if (!sessao) {
        return;
    }

    sessaoAtiva = sessaoId;
    renderizarAbas();
    atualizarInformacoesSessao(sessao);
    messageInput.disabled = false;
    sendMessageButton.disabled = false;

    await carregarMensagens(sessaoId);
}


async function encerrarSessao(sessaoId) {
    const sessao = sessoes.find(item => item.id === sessaoId);

    if (!sessao) {
        return;
    }

    const confirmar = confirm(
        `Deseja encerrar a sessão "${sessao.cliente}"?`
    );

    if (!confirmar) {
        return;
    }

    try {
        await requisicao(`/api/sessoes/${sessaoId}`, {
            method: "DELETE"
        });

        sessoes = sessoes.filter(item => item.id !== sessaoId);

        if (sessaoAtiva === sessaoId) {
            sessaoAtiva = null;

            if (sessoes.length > 0) {
                await selecionarSessao(sessoes[sessoes.length - 1].id);
            } else {
                atualizarInformacoesSessao(null);
                exibirEstadoInicial();

                messageInput.disabled = true;
                sendMessageButton.disabled = true;
            }
        }

        renderizarAbas();

    } catch (erro) {
        alert(erro.message);
    }
}

async function limparSessao() {
    if (!sessaoAtiva) {
        return;
    }

    const confirmar = confirm(
        "Deseja realmente limpar o histórico desta conversa?"
    );

    if (!confirmar) {
        return;
    }

    try {
        await requisicao(`/api/sessoes/${sessaoAtiva}/limpar`, {
            method: "POST"
        });

        exibirEstadoInicial();

    } catch (erro) {
        alert(erro.message);
    }
}

function adicionarMensagem(papel, conteudo) {
    const mensagem = document.createElement("div");

    mensagem.className = `message message-${papel}`;

    const identificacao = document.createElement("span");
    identificacao.className = "message-author";
    identificacao.textContent = papel === "user" ? "Você" : "Viajante";

    const texto = document.createElement("p");
    texto.className = "message-text";
    texto.textContent = conteudo;

    mensagem.append(identificacao, texto);
    chatMessages.appendChild(mensagem);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function exibirEstadoInicial() {
    chatMessages.replaceChildren();

    const boasVindas = document.createElement("div");
    boasVindas.className = "welcome-message";

    const icone = document.createElement("div");
    icone.className = "welcome-icon";
    icone.textContent = "✈";

    const titulo = document.createElement("h3");
    titulo.textContent = "Bem-vindo ao Viajante!";

    const descricao = document.createElement("p");
    descricao.textContent = "Envie uma mensagem para começar a conversar.";

    boasVindas.append(icone, titulo, descricao);
    chatMessages.appendChild(boasVindas);
}


async function carregarMensagens(sessaoId) {
    chatMessages.replaceChildren();

    try {
        const dados = await requisicao(
            `/api/sessoes/${sessaoId}/mensagens`
        );

        if (dados.mensagens.length === 0) {
            exibirEstadoInicial();
            return;
        }

        dados.mensagens.forEach(mensagem => {
            adicionarMensagem(
                mensagem.role,
                mensagem.content
            );
        });

    } catch (erro) {
        exibirEstadoInicial();
        alert(erro.message);
    }
}


async function enviarMensagem() {
    const mensagem = messageInput.value.trim();

    if (!mensagem || !sessaoAtiva) {
        return;
    }

    messageInput.disabled = true;
    sendMessageButton.disabled = true;

    adicionarMensagem("user", mensagem);

    messageInput.value = "";

    const indicador = document.createElement("div");
    indicador.className = "message message-assistant";
    indicador.textContent = "Viajante está pensando...";
    indicador.id = "thinkingIndicator";

    chatMessages.appendChild(indicador);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const sessaoId = sessaoAtiva;

    try {
        const dados = await requisicao(
            `/api/sessoes/${sessaoAtiva}/mensagens`,
            {
                method: "POST",
                body: JSON.stringify({
                    mensagem: mensagem
                })
            }
        );

        if (sessaoAtiva === sessaoId) {
            indicador.remove();
            adicionarMensagem("assistant", dados.resposta);
        }else{
            indicador.remove();
        }
        
        console.log("Execução do agente:", {
            iteracoes: dados.iteracoes,
            limiteAtingido: dados.limite_atingido
        });

    } catch (erro) {
        indicador.remove();

        adicionarMensagem(
            "assistant",
            `Não foi possível processar sua mensagem: ${erro.message}`
        );

        await carregarMensagens(sessaoAtiva);

    } finally {
        messageInput.disabled = false;
        sendMessageButton.disabled = false;
        messageInput.focus();
    }
}

newSessionButton.addEventListener("click", criarSessao);
clearSessionButton.addEventListener("click", limparSessao);
sendMessageButton.addEventListener("click", enviarMensagem);
messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        enviarMensagem();
    }
});

// Inicialização
carregarSessoes().then(() => {
    if (sessoes.length === 0) {
        criarSessao();
    } else {
        selecionarSessao(sessoes[0].id);
    }
});
