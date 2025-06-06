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
        });
}
setInterval(fetchData, 2000);
fetchData();