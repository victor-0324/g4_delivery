document.getElementById('uploadBtn').addEventListener('click', () => {
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);
    
    // Exibir status de envio
    const uploadStatus = document.getElementById('uploadStatus');
    uploadStatus.innerHTML = "<p class='text-info'>Enviando arquivo...</p>";

    // Simular envio via fetch (substitua pela lógica do backend)
    fetch('/admin/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            uploadStatus.innerHTML = "<p class='text-success'>Arquivo enviado com sucesso!</p>";
        } else {
            uploadStatus.innerHTML = "<p class='text-danger'>Erro ao enviar o arquivo.</p>";
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        uploadStatus.innerHTML = "<p class='text-danger'>Erro ao enviar o arquivo.</p>";
    });
});