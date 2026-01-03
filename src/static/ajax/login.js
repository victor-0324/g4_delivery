$(document).ready(function () {
    $("#login-button").click(function (e) {
        e.preventDefault(); // Previne o envio padrão do formulário
        console.log("Botão de login clicado."); // Log inicial

        // Captura os dados do formulário
        const formData = {
            cpf: $("input[name='cpf']").val(),
            password: $("input[name='password']").val(),
        };
        console.log("Dados do formulário capturados:", formData); // Log dos dados do formulário

        // Verifica se os campos estão preenchidos
        if (!formData.cpf || !formData.password) {
            console.log("Campos vazios detectados. Exibindo alerta.");
            Swal.fire({
                icon: "warning",
                title: "Atenção",
                text: "Por favor, preencha todos os campos!",
            });
            return;
        }

        console.log("Enviando requisição AJAX para login."); // Log antes da requisição

        // Faz a requisição AJAX para a rota de login
        $.ajax({
            url: "/login", // Substitua pela rota correta se necessário
            type: "POST",
            contentType: "application/json", // Define o tipo de conteúdo
            data: JSON.stringify(formData), // Converte os dados para JSON
            success: function (response) {
                console.log("Login realizado com sucesso. Redirecionando para:", response.redirect);
                
                window.location.href = response.redirect;
            },
            error: function (xhr) {
                console.error("Erro:", xhr.responseJSON.message);
                Swal.fire({
                    icon: "error",
                    title: "Erro",
                    text: xhr.responseJSON.message || "Erro desconhecido.",
                });
            }
        });
    });
});
