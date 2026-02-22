// Elementos Globais
const sino = document.querySelector(".notifications");
const dropdown = document.getElementById("dropdown-notificacoes");
const badge = document.getElementById("badge");

// Função para buscar Cookie CSRF (Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function carregarNotificacoes() {
    if (!dropdown || !badge) return;

    try {
        const res = await fetch("/notificacoes/listar/");
        const data = await res.json();
        const total = data.length;

        badge.innerText = total || "";
        if (total > 0) {
            badge.classList.add("badge-pulse");
        } else {
            badge.classList.remove("badge-pulse");
        }

        if (total === 0) {
            dropdown.innerHTML = `
                <div class="sem-notificacao" style="padding: 15px; text-align: center; color: #888;">
                    Você não possui nenhuma notificação no momento.
                </div>
            `;
            return;
        }

        let html = `
            <div class="notificacao-header" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #444; background: #1a1a1a;">
                <span style="font-weight: bold; font-size: 13px; color: #fff;">Notificações</span>
                <button id="marcar-todas-lidas" style="background: none; border: none; color: #ffcc00; cursor: pointer; font-size: 11px; text-decoration: underline;">
                    Marcar todas como lida
                </button>
            </div>
            <div class="lista-notificacoes" style="max-height: 300px; overflow-y: auto;">
        `;

        data.forEach(n => {
            let corDestaque = '#ffcc00';
            let icone = '🔔';

            if (n.tipo === 'CANCELADO') {
                corDestaque = '#e74c3c';
                icone = '❌';
            } else if (n.tipo === 'CONCLUIDO') {
                corDestaque = '#2ecc71';
                icone = '✅';
            }

            html += `
                <div class="notificacao-item" data-id="${n.id}" 
                     style="padding: 12px; border-bottom: 1px solid #333; cursor: pointer; border-left: 4px solid ${corDestaque}; transition: background 0.3s;">
                    <div style="display: flex; align-items: flex-start; gap: 8px;">
                        <span>${icone}</span>
                        <div>
                            <div style="font-size: 13px; color: #eee; line-height: 1.4;">${n.mensagem}</div>
                            <small style="color: #666; font-size: 10px;">${n.criada}</small>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        dropdown.innerHTML = html;

        adicionarCliqueIndividual();
        adicionarCliqueMarcarTodas();
    } catch (error) {
        console.error("Erro ao carregar notificações:", error);
    }
}

function adicionarCliqueMarcarTodas() {
    const btn = document.getElementById("marcar-todas-lidas");
    if (btn) {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const res = await fetch("/notificacoes/ler-todas/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie('csrftoken'),
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            if (res.ok) {
                badge.innerText = "";
                badge.classList.remove("badge-pulse");
                dropdown.innerHTML = `<div class="sem-notificacao" style="padding: 15px; text-align: center; color: #888;">Você não possui nenhuma notificação no momento.</div>`;
            } else {
                alert("Erro ao marcar notificações como lidas.");
            }
        });
    }
}

function adicionarCliqueIndividual() {
    document.querySelectorAll(".notificacao-item").forEach(item => {
        item.addEventListener("click", async (e) => {
            e.stopPropagation();
            const id = item.dataset.id;
            await fetch(`/notificacoes/ler/${id}/`, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie('csrftoken') }
            });
            item.remove();

            const restantes = document.querySelectorAll(".notificacao-item").length;
            badge.innerText = restantes || "";
            if (restantes === 0) {
                badge.classList.remove("badge-pulse");
                dropdown.innerHTML = `<div class="sem-notificacao" style="padding: 15px; text-align: center; color: #888;">Você não possui nenhuma notificação no momento.</div>`;
            }
        });
    });
}

// Inicialização de Eventos
document.addEventListener('DOMContentLoaded', function () {

    // 1. Polling de Notificações
    if (badge) {
        setInterval(carregarNotificacoes, 20000);
        carregarNotificacoes();
    }

    // 2. Toggle do Dropdown do Sino
    if (sino && dropdown) {
        sino.addEventListener("click", (e) => {
            e.stopPropagation();
            dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
        });

        document.addEventListener("click", (e) => {
            if (!sino.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = "none";
            }
        });
    }

    // 3. Verificação de Segurança para SweetAlert2 (Swal)
    if (typeof Swal === 'undefined') {
        console.warn("Aviso: SweetAlert2 não foi carregado. As confirmações usarão alertas padrão.");
    }

    // 4. Botoes de Confirmação Geral (Link <a>)
    const botoesConfirmacao = document.querySelectorAll('.btn-confirmar-acao');
    botoesConfirmacao.forEach(botao => {
        botao.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            const titulo = this.getAttribute('data-titulo') || 'Tem certeza?';
            const texto = this.getAttribute('data-texto') || 'Você não poderá reverter isso!';
            const icone = this.getAttribute('data-icon') || 'question';

            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: titulo,
                    text: texto,
                    icon: icone,
                    showCancelButton: true,
                    confirmButtonColor: '#f1c40f',
                    cancelButtonColor: '#1a1a1a',
                    confirmButtonText: 'Sim, confirmar!',
                    cancelButtonText: 'Voltar',
                    background: '#161616',
                    color: '#ffffff'
                }).then((result) => {
                    if (result.isConfirmed) window.location.href = url;
                });
            } else {
                if (confirm(texto)) window.location.href = url;
            }
        });
    });

    // 5. Formulário de Cancelamento Inteligente (Regra dos 30min)
    document.querySelectorAll('.form-cancelamento').forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const agendamentoDataStr = this.getAttribute('data-horario');
            const agendamentoHora = new Date(agendamentoDataStr);
            const agora = new Date();
            const diferencaMinutos = (agendamentoHora - agora) / (1000 * 60);

            let titulo = 'Confirmar cancelamento?';
            let texto = 'Deseja realmente cancelar seu agendamento?';
            let icon = 'question';

            if (diferencaMinutos <= 30) {
                titulo = 'Atenção: Taxa de Cancelamento!';
                texto = 'Você está cancelando faltando menos de 30 minutos. Uma taxa de R$ 15,00 será gerada em seu perfil.';
                icon = 'warning';
            }

            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: titulo,
                    text: texto,
                    icon: icon,
                    showCancelButton: true,
                    confirmButtonColor: icon === 'warning' ? '#e74c3c' : '#f1c40f',
                    cancelButtonColor: '#1a1a1a',
                    confirmButtonText: 'Sim, cancelar',
                    cancelButtonText: 'Voltar',
                    background: '#161616',
                    color: '#fff'
                }).then((result) => {
                    if (result.isConfirmed) this.submit();
                });
            } else {
                if (confirm(texto)) this.submit();
            }
        });
    });
});

// Funções de Dropdown de Tabelas (Ellipsis)
function toggleDropdown(id) {
    document.querySelectorAll('.dropdown-content').forEach(d => {
        if (d.id !== 'dropdown-' + id) d.classList.remove('show');
    });
    const el = document.getElementById('dropdown-' + id);
    if (el) el.classList.toggle('show');
}

window.onclick = function (event) {
    if (!event.target.matches('.btn-dots') && !event.target.matches('.fa-ellipsis-v')) {
        document.querySelectorAll('.dropdown-content').forEach(d => d.classList.remove('show'));
    }
}