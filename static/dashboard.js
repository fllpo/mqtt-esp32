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
            $('#hora').html(`<i class="material-icons tiny">access_time</i> Última atualização: ${dataHora}`);
        })
        .catch(error => {
            console.error('Erro ao buscar dados do sensor:', error);
        });
}

// Variável para controlar se uma requisição está em andamento
let isRequestPending = false;

// Sistema de perguntas RAG
$('#enviar-pergunta').click(function() {
    // Se já houver uma requisição em andamento, não faz nada
    if (isRequestPending) {
        M.toast({ html: 'Aguarde a resposta atual', classes: 'orange' });
        return;
    }
    
    const pergunta = $('#pergunta').val().trim();
    if (!pergunta) {
        M.toast({ html: 'Digite uma pergunta!', classes: 'red' });
        return;
    }
    
    // Marca que uma requisição está em andamento
    isRequestPending = true;
    $('#loading').show();
    $('#resposta').html('');
    
    // Envia a pergunta para a API RAG
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
        // Formata a resposta
        $('#resposta').html(`<br>
            <div class="resposta-container">
                <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                    <i class="material-icons" style="color: #1e88e5; margin-right: 10px;">question_answer</i>
                    <strong>Pergunta: </strong><br>${pergunta}
                </div>
                <div style="display: flex; align-items: flex-start;">
                    <i class="material-icons" style="color: #4caf50; margin-right: 10px;">lightbulb_outline</i>
                    <div>
                        <strong>Resposta: </strong><br>
                        ${data.resposta || 'Não foi possível obter uma resposta'}
                    </div>
                </div>
                ${data.fonte ? `<div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                    <i class="material-icons tiny">source</i> Fonte: ${data.fonte}
                </div>` : ''}
            </div>
        `);
        
        // Limpa o campo de pergunta
        $('#pergunta').val('');
    })
    .catch(error => {
        console.error('Erro ao buscar resposta RAG:', error);
        $('#resposta').html(`
            <div class="red lighten-4 red-text text-darken-4" style="padding: 10px; border-radius: 5px;">
                <i class="material-icons left">error</i> Erro ao processar sua pergunta: ${error.message || 'Tente novamente mais tarde'}
            </div>
        `);
    })
    .finally(() => {
        // Esconde o loading e libera para novas requisições
        $('#loading').hide();
        isRequestPending = false;
    });
});

// Permitir enviar com Enter
$('#pergunta').keypress(function(e) {
    if (e.which === 13) {
        $('#enviar-pergunta').click();
    }
});

// Atualizar dados do sensor a cada 2 segundos
setInterval(fetchData, 2000);
fetchData(); // Inicializar