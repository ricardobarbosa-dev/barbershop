document.addEventListener('DOMContentLoaded', () => {
    const showToast = (message, type) => {
        const toastFn = window.createToast || (typeof createToast === 'function' ? createToast : null);

        if (toastFn) {
            toastFn(message, type);
        } else {
            console.error("ERRO: A função createToast não foi encontrada. Verifique se o toast.js está carregado.");
        }
    };

    const displayFieldErrors = (errors) => {
        document.querySelectorAll('.error-feedback').forEach(el => el.remove());
        for (const formKey in errors) {
            const formErrors = errors[formKey];
            for (const fieldName in formErrors) {
                const input = document.querySelector(`[name="${fieldName}"]`);
                if (input) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-feedback';
                    errorDiv.style.color = '#dc3545';
                    errorDiv.style.fontSize = '12px';
                    errorDiv.style.marginTop = '5px';
                    errorDiv.innerText = Array.isArray(formErrors[fieldName]) ? formErrors[fieldName][0] : formErrors[fieldName];
                    input.parentElement.appendChild(errorDiv);
                }
            }
        }
    };

    // perfil
    const perfilForm = document.getElementById('perfilForm');
    if (perfilForm) {
        perfilForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(perfilForm);
            try {
                const response = await fetch(perfilForm.action || window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                const resData = await response.json();
                if (resData.success) {
                    showToast(resData.message, 'success');
                } else {
                    if (resData.errors) displayFieldErrors(resData.errors);
                    else showToast(resData.message || 'Erro ao atualizar perfil', 'error');
                }
            } catch (err) {
                showToast('Erro de conexão com o servidor', 'error');
            }
        });
    }

    // senha
    const senhaForm = document.getElementById('senhaForm');
    if (senhaForm) {
        senhaForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            copiarSenha();

            const formData = new FormData(senhaForm);
            try {
                const response = await fetch(senhaForm.action || window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                const resData = await response.json();

                if (resData.success) {
                    showToast(resData.message, 'success');
                    senhaForm.reset();
                } else {
                    showToast(resData.message || 'Erro ao alterar senha', 'error');
                    if (resData.errors) displayFieldErrors(resData.errors);
                }
            } catch (err) {
                console.error(err);
                showToast('Erro ao processar alteração de senha', 'error');
            }
        });
    }

    // logica e horarios
    const barbeiroSelect = document.getElementById('barbeiro_select');
    const dataInput = document.getElementById('data_input');
    const container = document.getElementById('horarios-container');
    const hiddenInput = document.getElementById('horario_selecionado');

    function carregarHorarios() {
        const barbeiroId = barbeiroSelect ? barbeiroSelect.value : null;
        const data = dataInput ? dataInput.value : null;
        if (!barbeiroId || !data || !container) return;

        container.innerHTML = '<p class="no-slots" style="color: #FF9800;background: #FFF3E0; border: 1px solid #FF9800; border-radius: 6px;">Buscando horários disponíveis.. Aguarde!</p>';

        fetch(`/buscar-horarios/?barbeiro=${barbeiroId}&data=${data}`)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';
                if (!data.horarios || data.horarios.length === 0) {
                    container.innerHTML = '<p class="no-slots" style="color: #e74c3c;background: #FFEBEE; border:1px solid #F44336; border-radius: 6px;">Não há nenhum horário disponível para essa data.</p>';
                    return;
                }
                data.horarios.forEach(slot => {
                    const div = document.createElement('div');
                    div.classList.add('slot-card');
                    div.innerText = slot.hora;
                    if (slot.disponivel === false) {
                        div.classList.add('unavailable');
                        Object.assign(div.style, { backgroundColor: '#2c0b0b', color: '#ff4d4d', border: '1px solid #e74c3c', textDecoration: 'line-through', cursor: 'not-allowed', opacity: '0.6' });
                    } else {
                        div.onclick = function () {
                            document.querySelectorAll('.slot-card').forEach(s => s.classList.remove('selected'));
                            div.classList.add('selected');
                            if (hiddenInput) hiddenInput.value = slot.hora;
                        };
                    }
                    container.appendChild(div);
                });
            })
            .catch(err => {
                if (container) container.innerHTML = '<p class="no-slots">Erro ao carregar horários.</p>';
            });
    }

    if (barbeiroSelect && dataInput) {
        barbeiroSelect.addEventListener('change', carregarHorarios);
        dataInput.addEventListener('change', carregarHorarios);
    }
});

// Funções globais 
function copiarSenha() {
    const pass1 = document.getElementsByName('new_password1')[0];
    const pass2 = document.getElementById('id_new_password2');
    if (pass1 && pass2) pass2.value = pass1.value;
}

// Preview da imagem
const fotoInput = document.getElementById('foto-input');
if (fotoInput) {
    fotoInput.onchange = (evt) => {
        const [file] = evt.target.files;
        if (file) {
            const preview = document.getElementById('avatar-preview');
            if (preview) preview.src = URL.createObjectURL(file);
        }
    }
}
