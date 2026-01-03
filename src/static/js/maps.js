let mapModal, markerA, markerB, directionsServiceModal, directionsRendererModal, geocoder, marker;
// Valores do banco passados do Flask

function initAllMaps() {
  initMap();
  initMapModal();
  initMapValores();
}

function initMapValores() {
  mapModal = new google.maps.Map(document.getElementById("mapModalValores"), {
    center: { lat: -22.1164, lng: -45.0562 },
    zoom: 13,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    zoomControl: false,
    styles: [
      { featureType: "poi", stylers: [{ visibility: "off" }] },
      { featureType: "transit", stylers: [{ visibility: "off" }] },
      { featureType: "road", elementType: "labels", stylers: [{ visibility: "on" }] }
    ]
  });

  geocoder = new google.maps.Geocoder();
  directionsServiceModal = new google.maps.DirectionsService();
  directionsRendererModal = new google.maps.DirectionsRenderer();
  directionsRendererModal.setMap(mapModal);

  const input = document.getElementById("inputEndereco");
  const autocomplete = new google.maps.places.Autocomplete(input);
  autocomplete.bindTo("bounds", mapModal);

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();

    if (!place.geometry || !place.geometry.location) {
      alert("Endereço não encontrado.");
      return;
    }

    mapModal.setCenter(place.geometry.location);
    mapModal.setZoom(15);

    if (marker) marker.setMap(null);
    marker = new google.maps.Marker({
      map: mapModal,
      position: place.geometry.location
    });

    document.getElementById("enderecoSelecionado").innerText = place.formatted_address;
  });

  // 👉 Clique no mapa para adicionar marcador e pegar endereço
  mapModal.addListener("click", (event) => {
    const clickedLocation = event.latLng;

    if (marker) marker.setMap(null);
    marker = new google.maps.Marker({
      map: mapModal,
      position: clickedLocation
    });

    // Obter endereço reverso
    geocoder.geocode({ location: clickedLocation }, (results, status) => {
      if (status === "OK" && results[0]) {
        document.getElementById("enderecoSelecionado").innerText = results[0].formatted_address;
        input.value = results[0].formatted_address;
      } else {
        document.getElementById("enderecoSelecionado").innerText = "Endereço não encontrado.";
      }
    });
  });
}

function cadastrarBairro() {
  const nome = document.getElementById("nomeBairro").value.trim();
  const tipo = document.getElementById("tipoBairro").value;
  const nomesAlternativos = document.getElementById("nomesAlternativos").value.trim();
  const endereco = document.getElementById("enderecoSelecionado").innerText;

  if (!nome || !tipo || endereco === "Endereço selecionado") {
    alert("Por favor, preencha todos os campos e selecione um local no mapa.");
    return;
  }

  // Captura a posição do marcador, se existir
  let latitude = null;
  let longitude = null;

  if (marker && marker.getPosition) {
    const pos = marker.getPosition();
    latitude = pos.lat();
    longitude = pos.lng();
  }

  const data = {
    nome,
    tipo,
    nomes_alternativos: nomesAlternativos,
    endereco,
    latitude,
    longitude
  };

  fetch("/admin/cadastrar_bairro", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  })
    .then(async response => {
      const result = await response.json();

      if (response.status === 201) {
        alert(result.response);

        // Fechar modal e limpar campos
        const modal = bootstrap.Modal.getInstance(document.getElementById('exampleModalFullscreenXxlValores'));
        modal.hide();

        document.getElementById("nomeBairro").value = "";
        document.getElementById("tipoBairro").value = "";
        document.getElementById("nomesAlternativos").value = "";
        document.getElementById("inputEndereco").value = "";
        document.getElementById("enderecoSelecionado").innerText = "Endereço selecionado";

        if (marker) {
          marker.setMap(null);
          marker = null;
        }

      } else if (response.status === 409) {
        alert("Este bairro já está cadastrado.");
      } else if (response.status === 400) {
        alert("Preencha corretamente todos os campos.");
      } else if (response.status === 401) {
        alert("Você precisa estar logado para cadastrar um bairro.");
      } else {
        alert("Erro inesperado ao cadastrar bairro. Tente novamente.");
      }
    })
    .catch(error => {
      console.error("Erro:", error);

      // Exibe a mensagem de erro em um elemento na tela, como dentro da modal
      const erroDiv = document.getElementById("erroMensagem");
      if (erroDiv) {
        erroDiv.innerText = "Erro ao conectar com o servidor. Verifique sua conexão.";
        erroDiv.style.display = "block";
      }
    });
}

function carregarBairros() {
  fetch('/admin/carregar_bairros')
    .then(response => response.json())
    .then(data => {
      data.forEach(bairro => {
        const position = { lat: bairro.latitude, lng: bairro.longitude };
        const marker = new google.maps.Marker({
          position,
          map: mapModal,
          title: bairro.nome,
          icon: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png'
        });

        const infoWindow = new google.maps.InfoWindow({
          content: `
            <strong>${bairro.nome}</strong><br>
            Tipo: ${bairro.tipo}<br>
            Alternativos: ${bairro.nomes_alternativos || "N/A"}
          `
        });

        marker.addListener("click", () => {
          infoWindow.open(mapModal, marker);
        });
      });
    })
    .catch(error => {
      console.error("Erro ao carregar bairros:", error);
    });
}



document.getElementById("exampleModalFullscreenXxlValores").addEventListener("shown.bs.modal", function () {
  if (!modalValoresInitialized && window.googleMapsLoaded) {
    setTimeout(() => {
      initMapValores();
      modalValoresInitialized = true;
    }, 200); // garante que o input esteja visível
  }
});



function initMapModal() {
  mapModal = new google.maps.Map(document.getElementById("mapModal"), {
    center: { lat: -22.1164, lng: -45.0562 },
    zoom: 13,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    zoomControl: false,
    styles: [
      { featureType: "poi", stylers: [{ visibility: "off" }] },
      { featureType: "transit", stylers: [{ visibility: "off" }] },
      { featureType: "road", elementType: "labels", stylers: [{ visibility: "on" }] }
    ]
  });

  directionsServiceModal = new google.maps.DirectionsService();
  directionsRendererModal = new google.maps.DirectionsRenderer();
  directionsRendererModal.setMap(mapModal);
  geocoder = new google.maps.Geocoder();

  // Permite selecionar os pontos clicando no mapa
  mapModal.addListener("click", (event) => {
    setMarker(event.latLng);
  });

  // Chama a função que configura o autocomplete para os inputs
  initAutocompleteInputs();
}



// Inicializa o autocomplete para os inputs de endereço
function initAutocompleteInputs() {
  const pickupInput = document.getElementById("pickup-address");
  const destinationInput = document.getElementById("destination-address");

  const pickupAutocomplete = new google.maps.places.Autocomplete(pickupInput, {
    componentRestrictions: { country: "br" }
  });
  const destinationAutocomplete = new google.maps.places.Autocomplete(destinationInput, {
    componentRestrictions: { country: "br" }
  });

  pickupAutocomplete.addListener("place_changed", function () {
    let place = pickupAutocomplete.getPlace();
    if (place.geometry) {
      if (markerA) {
        markerA.setPosition(place.geometry.location);
      } else {
        markerA = new google.maps.Marker({
          position: place.geometry.location,
          map: mapModal,
          label: "A"
        });
      }
      mapModal.panTo(place.geometry.location);
      calculateRouteModal();
    }
  });

  destinationAutocomplete.addListener("place_changed", function () {
    let place = destinationAutocomplete.getPlace();
    if (place.geometry) {
      if (markerB) {
        markerB.setPosition(place.geometry.location);
      } else {
        markerB = new google.maps.Marker({
          position: place.geometry.location,
          map: mapModal,
          label: "B"
        });
      }
      mapModal.panTo(place.geometry.location);
      calculateRouteModal();
    }
  });
}

// Define os marcadores para embarque e destino via clique no mapa
function setMarker(location) {
  if (!markerA) {
    // Define o primeiro ponto (A)
    markerA = new google.maps.Marker({
      position: location,
      map: mapModal,
      label: "A"
    });
    getAddress(location, "pickup-address");
  } else if (!markerB) {
    // Define o segundo ponto (B)
    markerB = new google.maps.Marker({
      position: location,
      map: mapModal,
      label: "B"
    });
    getAddress(location, "destination-address");
    calculateRouteModal();
  } else {
    // Se já existem A e B, redefine os pontos
    markerA.setMap(null);
    markerB.setMap(null);
    markerA = null;
    markerB = null;
    directionsRendererModal.setDirections({ routes: [] }); // Limpa a rota no mapa
    setMarker(location); // Define novamente o ponto A
  }
}

// Converte coordenadas em endereço e preenche o input correspondente
function getAddress(latLng, inputId) {
  geocoder.geocode({ location: latLng }, (results, status) => {
    if (status === "OK" && results[0]) {
      document.getElementById(inputId).value = results[0].formatted_address;
    }
  });
}

let routeDistance = 0; // em metros
let routeDuration = 0; // em segundos
// Calcula a rota entre os dois pontos, captura distância e duração, e atualiza os valores
function calculateRouteModal() {
  if (!markerA || !markerB) return;

  const request = {
    origin: markerA.getPosition(),
    destination: markerB.getPosition(),
    travelMode: google.maps.TravelMode.DRIVING,
  };

  directionsServiceModal.route(request, (result, status) => {
    if (status === google.maps.DirectionsStatus.OK) {
      directionsRendererModal.setDirections(result);

      // Captura a distância e a duração
      let distanceText = result.routes[0].legs[0].distance.text; // ex: "12,3 km"
      let distanceNum = parseFloat(distanceText.replace(" km", "").replace(",", "."));
      routeDistance = distanceNum * 1000; // converte para metros
      routeDuration = result.routes[0].legs[0].duration.value; // em segundos

      // Atualiza a seleção da bandeira e busca os dados da tarifa conforme o tipo (corrida ou viagem)
      let bandeiraSelecionada = document.querySelector('input[name="bandeiraOptions"]:checked').value;
      document.getElementById("bandeira-selecionada").textContent = bandeiraSelecionada;
      let tarifa = getTarifaSelecionada();

      if (tarifa) {
        // Preenche os inputs com os valores vindos do banco
        document.getElementById("current-base").value = `R$ ${tarifa.valor_base.toFixed(2)}`;
        document.getElementById("current-minimum").value = `R$ ${tarifa.valor_minimo.toFixed(2)}`;
        document.getElementById("current-km").value = `R$ ${tarifa.valor_km.toFixed(2)}`;
        document.getElementById("current-time").value = `R$ ${tarifa.valor_min.toFixed(2)}`;
        // Calcula o valor da corrida/viagem
        cotarCorrida();
      }
    } else {
      alert("Não foi possível calcular a rota.");
    }
  });
}

// Retorna a tarifa selecionada com base no tipo (corrida ou viagem) e na bandeira
function getTarifaSelecionada() {
  let tipo = document.querySelector('input[name="tipoCorrida"]:checked').value;
  let bandeiraSelecionada = document.querySelector('input[name="bandeiraOptions"]:checked').value;
  document.getElementById("bandeira-selecionada").textContent = bandeiraSelecionada;

  let fonte = tipo === "viagem" ? valores_viagem : valores;
  return fonte.find(v => v.bandeira == bandeiraSelecionada);
}

// Calcula o valor da corrida/viagem usando routeDistance e routeDuration
async function cotarCorrida() {
  let tarifa = getTarifaSelecionada();
  if (!tarifa) {
    console.error("Tarifa não encontrada para a seleção atual.");
    return;
  }

  let valorBase = tarifa.valor_base ? parseFloat(tarifa.valor_base) : 0.0;
  let valorMinimo = tarifa.valor_minimo ? parseFloat(tarifa.valor_minimo) : 0.0;
  let valorKm = tarifa.valor_km ? parseFloat(tarifa.valor_km) : 0.0;
  let valorMin = tarifa.valor_min ? parseFloat(tarifa.valor_min) : 0.0;

  let distanciaKm = routeDistance / 1000;
  let duracaoMinuto = routeDuration / 60;

  let valorCorrida = valorBase + (distanciaKm * valorKm) + (duracaoMinuto * valorMin);
  if (valorCorrida < valorMinimo) {
    valorCorrida = valorMinimo;
  }

  valorCorrida = parseFloat(valorCorrida.toFixed(2));

  document.getElementById("current-value").value = `R$ ${valorCorrida.toFixed(2)}`;
  console.log(`Valor da corrida/viagem: R$ ${valorCorrida}`);
  return valorCorrida;
}

// Testa os novos valores conforme os inputs de "Mudar valores"
function testarNovosValores() {
  let novoBase = parseFloat(document.getElementById("new-base").value) || 0;
  let novoMinimo = parseFloat(document.getElementById("new-minimum").value) || 0;
  let novoValorKm = parseFloat(document.getElementById("new-km").value) || 0;
  let novoValorTempo = parseFloat(document.getElementById("new-time").value) || 0;

  let novoValor = novoBase + ((routeDistance / 1000) * novoValorKm) + ((routeDuration / 60) * novoValorTempo);
  if (novoValor < novoMinimo) {
    novoValor = novoMinimo;
  }

  document.getElementById("new-value").value = `R$ ${novoValor.toFixed(2)}`;
}

// Eventos para atualizar o teste de novos valores conforme os inputs mudam
document.getElementById("new-base").addEventListener("input", testarNovosValores);
document.getElementById("new-minimum").addEventListener("input", testarNovosValores);
document.getElementById("new-km").addEventListener("input", testarNovosValores);
document.getElementById("new-time").addEventListener("input", testarNovosValores);

// Atualiza os valores se a bandeira mudar
document.querySelectorAll('input[name="bandeiraOptions"]').forEach(radio => {
  radio.addEventListener('change', () => {
    calculateRouteModal();
  });
});

// Atualiza os valores se o tipo (corrida ou viagem) mudar
document.querySelectorAll('input[name="tipoCorrida"]').forEach(radio => {
  radio.addEventListener('change', () => {
    calculateRouteModal();
  });
});

// Quando o modal for aberto, reinicializa os marcadores e inputs
document.getElementById('exampleModalFullscreenXxl').addEventListener('shown.bs.modal', function () {
  markerA = null;
  markerB = null;
  initMapModal();
  initAutocompleteInputs();
  document.getElementById("pickup-address").value = "";
  document.getElementById("destination-address").value = "";
  document.getElementById("current-minimum").value = "";
  document.getElementById("current-base").value = "";
  document.getElementById("current-km").value = "";
  document.getElementById("current-time").value = "";
  document.getElementById("current-value").value = "";
  // Limpa os inputs de novos valores
  document.getElementById("new-minimum").value = "";
  document.getElementById("new-base").value = "";
  document.getElementById("new-km").value = "";
  document.getElementById("new-time").value = "";
  document.getElementById("new-value").value = "";
});

// Atualiza as tarifas no banco via AJAX
function updateTarifas() {
  let novaTarifa = {
    bandeira: document.querySelector('input[name="bandeiraOptions"]:checked').value,
    valor_min: parseFloat(document.getElementById("new-time").value) || 0,
    valor_km: parseFloat(document.getElementById("new-km").value) || 0,
    valor_minimo: parseFloat(document.getElementById("new-minimum").value) || 0,
    valor_base: parseFloat(document.getElementById("new-base").value) || 0,
    tipo_corrida: document.querySelector('input[name="tipoCorrida"]:checked').value
  };

  fetch("/valores/atualizar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(novaTarifa)
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert("Tarifas atualizadas com sucesso!");
        let tipo = document.querySelector('input[name="tipoCorrida"]:checked').value;
        let arrayDestino = tipo === "viagem" ? valores_viagem : valores;
        let index = arrayDestino.findIndex(v => v.bandeira == novaTarifa.bandeira);
        if (index !== -1) { arrayDestino[index] = novaTarifa; }
        calculateRouteModal();
      } else {
        alert("Erro ao atualizar as tarifas.");
      }
    })
    .catch(error => {
      console.error("Erro:", error);
      alert("Erro na requisição de atualização.");
    });
}


function getCarIcon(status) {
  let color;
  switch (status) {
    case "livre":
      color = "#34A853"; // verde
      break;
    case "em_corrida":
      color = "#FBBC05"; // amarelo
      break;
    default:
      color = "#EA4335"; // vermelho
  }

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
      <!-- Pin arredondado -->
      <path fill="${color}" d="M12 2C8 2 5 5.1 5 9c0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3-7-7-7z"/>
      <!-- Ícone de carro dentro -->
      <path fill="white" d="M7 13h10l-1-3H8l-1 3zm2.5 2a1 1 0 110 2 1 1 0 010-2zm7 0a1 1 0 110 2 1 1 0 010-2z"/>
    </svg>
  `;

  return {
    url: "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg),
    scaledSize: new google.maps.Size(45, 45),
    anchor: new google.maps.Point(22, 45) // faz a ponta do pin bater no ponto certo
  };
}

function initMap() {
  // Centro fixo em São Lourenço/MG
  var centro = { lat: -22.1167, lng: -45.0500 };

  var map = new google.maps.Map(document.getElementById("map"), {
    zoom: 13,
    center: centro
  });

  motoristas.forEach(motorista => {
    var iconUrl = "https://maps.google.com/mapfiles/kml/shapes/cabs.png";

    // Ícone colorido de acordo com o status
    var statusColor;
    switch (motorista.status) {
      case "livre":
        statusColor = "green";
        break;
      case "em_corrida":
        statusColor = "orange";
        break;
      default: // offline ou outro status
        statusColor = "red";
    }

    var marcador = new google.maps.Marker({
      position: { lat: motorista.lat, lng: motorista.lon },
      map: map,
      title: motorista.nome,
      icon: getCarIcon(motorista.status)
    });

    var infoWindowContent = `
            <div style="font-family: Arial, sans-serif; font-size: 14px; padding: 10px; color: #333;">
                <strong style="font-size: 16px; color: #000;">${motorista.nome}</strong>
                <br>
                <span style="font-weight: bold;">Status:
                    <span style="color: ${statusColor}; font-size: 14px;">${motorista.status}</span>
                </span>
            </div>
        `;

    var infoWindow = new google.maps.InfoWindow({
      content: infoWindowContent
    });

    marcador.addListener("click", function () {
      infoWindow.open(map, marcador);
      setTimeout(() => {
        infoWindow.close();
      }, 5000);
    });
  });
}

document.addEventListener('DOMContentLoaded', function () {
  var modal = document.getElementById('exampleModalgrid');

  modal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget;

    // Captura os atributos do botão
    var id = button.getAttribute('data-id');
    var nome = button.getAttribute('data-nome');
    var telefone = button.getAttribute('data-telefone');
    var sexo = button.getAttribute('data-sexo');
    var cpf = button.getAttribute('data-cpf');
    var tipo_carro = button.getAttribute('data-tipo_carro');
    var status = button.getAttribute('data-status');
    var hora_livre = button.getAttribute('data-horalivre');
    var inicio_corrida = button.getAttribute('data-inicio_corrida');
    var duracao_corrida = button.getAttribute('data-duracao_corrida');
    var destino = button.getAttribute('data-destino');

    // Atualiza os elementos no modal
    document.getElementById('raceId').textContent = id;
    document.getElementById('raceNome').textContent = nome;
    document.getElementById('raceTelefone').textContent = telefone;
    document.getElementById('raceSexo').textContent = sexo;
    document.getElementById('raceCpf').textContent = cpf;
    document.getElementById('raceTipoCarro').textContent = tipo_carro;
    document.getElementById('raceHoraLivre').textContent = hora_livre;
    document.getElementById('raceStatus').textContent = status;

    // Atualiza a classe do status
    var statusElement = document.getElementById('raceStatus');
    statusElement.className = 'badge'; // Remove classes antigas
    if (status === 'em_corrida') {
      statusElement.classList.add('bg-warning', 'text-dark'); // Laranja
    } else if (status === 'off') {
      statusElement.classList.add('bg-danger', 'text-light'); // Vermelho
    } else if (status === 'livre') {
      statusElement.classList.add('bg-success', 'text-light'); // Verde
    }

    // Verifica o status e exibe/oculta os campos da corrida
    var corridaInfo = document.getElementById('corridaInfo');
    if (status === 'em_corrida') {
      corridaInfo.style.display = 'block';
      document.getElementById('raceInicioCorrida').textContent = inicio_corrida || 'None';
      document.getElementById('raceDuracaoCorrida').textContent = duracao_corrida || 'Não disponível';
      document.getElementById('raceDestino').textContent = destino || 'Não definido';
    } else {
      corridaInfo.style.display = 'none';
    }

    // Atualiza botões com POST e exibe apenas o necessário
    var btnMandarOff = document.getElementById("btnMandarOff");
    var btnMandarLivre = document.getElementById("btnMandarLivre");

    function enviarPost(url, acao) {
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telefone: telefone })
      })
        .then(response => {
          if (response.ok) return response.json();
          throw new Error("Erro ao atualizar status");
        })
        .then(data => {
          alert(`Motorista agora está ${acao}!`);
          location.reload();
        })
        .catch(error => {
          alert("Falha na atualização: " + error.message);
        });
    }

    if (status === 'livre') {
      btnMandarOff.style.display = "block";
      btnMandarLivre.style.display = "none";
      btnMandarOff.onclick = function () {
        enviarPost("/motoristas/em_off", "OFF");
      };
    } else {
      btnMandarLivre.style.display = "block";
      btnMandarOff.style.display = "none";
      btnMandarLivre.onclick = function () {
        enviarPost("/motoristas/generate", "LIVRE");
      };
    }
  });
});
setInterval(() => {
  window.location.reload();
}, 120000);
