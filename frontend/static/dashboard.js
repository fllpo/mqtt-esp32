function fetchData() {
    fetch('/api/dados_sensor')
        .then(response => response.json())
        .then(data => {
            $('#temperatura').text(data.temperatura_atual);
            $('#umidade').text(data.umidade_atual);
            $('#pressao').text(data.pressao_atual);

            let dataHora = '--/--/---- às --:--';
            if (data.timestamp) {
                const dt = new Date(data.timestamp);
                dt.setHours(dt.getHours() + 3);
                dataHora = dt.toLocaleDateString('pt-BR') + ' às ' + dt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            }
            $('#hora').html(`<i class="bi bi-clock"></i> Última atualização: ${dataHora}`);
        })
        .catch(error => {
            console.error('Erro ao buscar dados do sensor:', error);
        });
}

let aguardandoResposta = false;

function showToastBootstrap(message, type = 'danger') {
    const alert = $(`
        <div class="toast align-items-center text-bg-${type} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
            </div>
        </div>
    `);

    $('#toast-container').append(alert);
    const bsToast = new bootstrap.Toast(alert[0]);
    bsToast.show();
}

$('#enviar-pergunta').click(function () {
    if (aguardandoResposta) {
        showToastBootstrap('Aguarde a resposta atual', 'warning');
        return;
    }

    const pergunta = $('#pergunta').val().trim();
    if (!pergunta) {
        showToastBootstrap('Digite uma pergunta!', 'danger');
        return;
    }

    aguardandoResposta = true;
    $('#resposta').html(`
        <div class="text-center my-3">
            <div class="spinner-border text-primary" role="status"/>
        </div>
    `);

    fetch('/api/rag', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pergunta: pergunta })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta da API');
            }
            return response.json();
        })
        .then(data => {
            $('#resposta').html(`
                <div class="resposta-container my-3">
                    <div class="d-flex align-items-start mb-2">                                                
                        <strong>Pergunta:</strong><br>
                    </div>
                    <div class="d-flex align-items-start mb-2">
                    ${pergunta}
                    </div>

                    <div class="d-flex align-items-start">    
                        <strong>Resposta:</strong><br>
                    </div>
                        
                    <div class="d-flex align-items-start">    
                        ${data.resposta || 'Não foi possível obter uma resposta'}
                    </div>
                    
                </div>
            `);
            $('#pergunta').val('');
        })
        .catch(error => {
            console.error('Erro ao buscar resposta RAG:', error);
            $('#resposta').html(`
                <div class="alert alert-danger" role="alert">
                    Erro ao processar sua pergunta: ${error.message || 'Tente novamente mais tarde'}
                </div>
            `);
        })
        .finally(() => {
            aguardandoResposta = false;
        });
});

$('#pergunta').keypress(function (e) {
    if (e.which === 13) {
        $('#enviar-pergunta').click();
    }
});

$(document).ready(function () {
    let graficos = {};

    $('.card-grafico').on('click', function () {
        const $card = $(this);
        const $container = $card.next('.grafico-container');
        const tipo = $card.data('tipo');
        let unidade = '';
        if (tipo === 'temperatura') {
            titulo = 'Temperatura';
            unidade = '°C';
        } else if (tipo === 'umidade') {
            titulo = 'Umidade';
            unidade = '%';
        } else if (tipo === 'pressao') {
            titulo = 'Pressão';
            unidade = 'hPa';
        }

        $('.grafico-container').not($container).slideUp();

        $container.slideToggle(function () {
            if ($container.is(':visible')) {

                $.get(`/api/historico/${tipo}`, function (dados) {
                    const labels = dados.map(item => item.hora);
                    const valores = dados.map(item => item.valor);

                    if (graficos[tipo]) {
                        graficos[tipo].destroy();
                    }

                    const ctx = $container.find('.graficoHistorico')[0].getContext('2d');

                    if (tipo === 'temperatura') {
                        backgroundColor = 'rgba(255, 99, 132, 0.2)';
                    } else if (tipo === 'umidade') {
                        backgroundColor = 'rgba(54, 162, 235, 0.2)';
                    } else if (tipo === 'pressao') {
                        backgroundColor = 'rgba(173, 86, 255, 0.2)';
                    }

                    if (tipo === 'temperatura') {
                        borderColor = $('.bg-danger').css('background-color');
                    } else if (tipo === 'umidade') {
                        borderColor = $('.bg-primary').css('background-color');
                    } else if (tipo === 'pressao') {
                        borderColor = $('.bg-purple').css('background-color');
                    }

                    const canvas = $container.find('.graficoHistorico')[0];
                    canvas.height = 200;

                    graficos[tipo] = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: titulo,
                                data: valores,
                                borderColor: borderColor,
                                backgroundColor: backgroundColor,
                                tension: 0.3,
                                pointRadius: 2,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    display: false,
                                },
                                tooltip: {
                                    callbacks: {
                                        title: function (context) {
                                            return 'Hora: ' + context[0].label;
                                        },
                                        label: function (context) {
                                            return ` ${context.dataset.label}: ${context.parsed.y} ${unidade}`;
                                        }
                                    }
                                }
                            },
                            scales: {
                                x: { title: { display: true, text: 'Hora' } },
                                y: { title: { display: true, text: unidade } }
                            }
                        }
                    });
                });
            }
        });
    });
});

setInterval(fetchData, 2000);
fetchData();
