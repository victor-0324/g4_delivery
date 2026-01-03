// Evento do botão "Estou Aqui"

document.getElementById('small-button').addEventListener('click', function() {
    if (userPosition) {
        // Dados a serem enviados para o backend
        const data = {
            lat: userPosition.lat,
            lon: userPosition.lng
        };

        // Enviar os dados via fetch para a rota no Flask
        fetch('/motoristas/location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Localização enviada com sucesso!');
            } else {
                alert('Erro ao enviar localização: ' + result.message);
            }
        })
        .catch(error => {
            console.error('Erro ao enviar localização:', error);
            alert('Erro ao enviar localização.');
        });
    } else {
        alert('Localização não está disponível.');
    }
});
