document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('exampleModalgrid');
    modal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;

        // Pega os atributos do botão
        const id = button.getAttribute('data-id');
      
        const status = button.getAttribute('data-status');
        const valor = button.getAttribute('data-valor');
        const embarque = button.getAttribute('data-embarque');
        const destino = button.getAttribute('data-destino');
        const data = button.getAttribute('data-data');

        document.getElementById('raceId').textContent = id;
        document.getElementById('raceValue').textContent = valor;
        document.getElementById('raceEmbarque').textContent = embarque;
        document.getElementById('raceDestino').textContent = destino;
        document.getElementById('raceDate').textContent = data;

        // Formata a data no formato pt-BR com hora, minuto e segundo
        const dateObj = new Date(data);

        const formattedDate = dateObj.toLocaleDateString('pt-BR'); // Exemplo: 01/12/2024
        const formattedTime = dateObj.toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            hour12: false // Formato de 24 horas
        }); // Exemplo: 14:30:45

        // Combina data e hora
        const formattedDateTime = `${formattedDate} ${formattedTime}`;

        // Exibe a data formatada com hora, minuto e segundo
        document.getElementById('raceDate').textContent = formattedDateTime;

        // Atualiza o status com as classes de estilo dinâmico
        const statusElement = document.getElementById('raceStatus');
        statusElement.textContent = status;
        statusElement.className = 'badge'; // Remove classes anteriores
        if (status === 'OK') {
            statusElement.classList.add('bg-success-subtle', 'text-success');
        } else if (status === 'cancelado') {
            statusElement.classList.add('bg-danger-subtle', 'text-danger');
        } else {
            statusElement.classList.add('bg-secondary-subtle', 'text-secondary');
        }
    });
});