let autocomplete; // Autocomplete compartilhado
let markerPickup, markerDropoff; // Marcadores
let map; // Mapa principal
let geocoder; // Para conversão de endereço
let directionsService, directionsRenderer; // Para rotas
let currentMode = "pickup"; // Estado atual (pickup ou dropoff)

function initMap() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userPosition = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };

        // Inicializar o mapa
        map = new google.maps.Map(document.getElementById("map"), {
          center: userPosition,
          zoom: 15,
          mapTypeControl: false,
          fullscreenControl: false,
          streetViewControl: false,
          zoomControl: false,
        });

        geocoder = new google.maps.Geocoder();
        directionsService = new google.maps.DirectionsService();
        directionsRenderer = new google.maps.DirectionsRenderer({
          map: map,
        });

        // Criar marcador de pickup
        markerPickup = new google.maps.Marker({
          position: userPosition,
          map: map,
          draggable: true,
          title: "Origem",
        });
        updateAddress(userPosition, "pickup");

        // Configurar autocompletes
        configureAutocomplete();

        // Listener para arrastar o marcador de pickup
        markerPickup.addListener("dragend", () => {
          const draggedLocation = {
            lat: markerPickup.getPosition().lat(),
            lng: markerPickup.getPosition().lng(),
          };
          updateAddress(draggedLocation, "pickup");
          if (markerDropoff) {
            showRoute();
          }
        });

        // Configurar clique no mapa
        map.addListener("click", (event) => {
          handleMapClick(event.latLng);
        });

        // Configurar botão "Avançar"
        document.getElementById("next").addEventListener("click", () => {
          switchToDropoffMode();
        });

        // Configurar botão "Retornar"
        document.getElementById("back").addEventListener("click", () => {
          switchToPickupMode();
        });
      },

      (error) => {
        console.error("Erro ao obter localização:", error);
        alert("Erro ao obter localização do usuário.");
      }
    );
  } else {
    alert("Geolocalização não suportada neste navegador.");
  }
}
document.getElementById("confirm").addEventListener("click", async function () {
  const dropoffAddress = document.getElementById("dropoff-search").value;
  if (!dropoffAddress) {
    alert("Por favor, informe o endereço de destino.");
    return;
  }
  try {
    const pickupAddress = document.getElementById("pickup-search").value;
    const id = "{{ cliente_id }}"; // Passando o id do cliente

    const response = await fetch("/corrida/location", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        embarque: pickupAddress,
        destino: dropoffAddress,
        cliente_id: id,
      }),
    });

    const result = await response.json();
    if (result.status === "success") {
      window.open(`https://wa.me/553597544794`, "_blank");
    } else {
      alert("Erro ao salvar o endereço.");
    }
  } catch (error) {
    alert("Erro ao enviar endereços.");
  }
});
document
  .getElementById("current-location-btn")
  .addEventListener("click", function () {
    // Verificar a etapa atual (pickup ou dropoff) e recentralizar no marcador correspondente
    if (currentMode === "pickup") {
      // Recentralizar no marcador de pickup
      map.setCenter(markerPickup.getPosition());
    } else if (currentMode === "dropoff") {
      // Recentralizar no marcador de dropoff, se existir, caso contrário, no pickup
      map.setCenter(
        markerDropoff ? markerDropoff.getPosition() : markerPickup.getPosition()
      );
    }
  });

function configureAutocomplete() {
  const pickupInput = document.getElementById("pickup-search");
  const dropoffInput = document.getElementById("dropoff-search");
  const autocompleteService = new google.maps.places.AutocompleteService();
  const geocoder = new google.maps.Geocoder();

  if (!navigator.geolocation) {
    alert("Geolocalização não suportada neste navegador.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const userPosition = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };

      const options = {
        bounds: new google.maps.LatLngBounds(
          new google.maps.LatLng(
            userPosition.lat - 0.1,
            userPosition.lng - 0.1
          ),
          new google.maps.LatLng(userPosition.lat + 0.1, userPosition.lng + 0.1)
        ),
        strictBounds: false,
        componentRestrictions: { country: "BR" },
        location: userPosition,
        radius: 5000, // Limite de 5 km
      };

      // Inicializar autocomplete para pickup e dropoff
      initAutocomplete(pickupInput, "pickup", options);
      initAutocomplete(dropoffInput, "dropoff", options);

      // Adicionar auto-correção no evento de entrada e de perda de foco
      setupAutoCorrectInput(pickupInput, "pickup");
      setupAutoCorrectInput(dropoffInput, "dropoff");
    },
    (error) => {
      console.error("Erro ao obter a localização do usuário:", error);
      alert(
        "Erro ao acessar a localização. Certifique-se de que a permissão foi concedida."
      );
    }
  );

  function setupAutoCorrectInput(inputField, type) {
    const handleAutoCorrect = () => {
      const inputValue = inputField.value;
      if (!inputValue.trim()) return;

      autocompleteService.getPlacePredictions(
        { input: inputValue, componentRestrictions: { country: "BR" } },
        (predictions, status) => {
          if (
            status === google.maps.places.PlacesServiceStatus.OK &&
            predictions.length > 0
          ) {
            const firstSuggestion = predictions[0].description;

            // Atualizar o campo de texto com a primeira sugestão
            inputField.value = firstSuggestion;

            // Atualizar marcador e mapa com a sugestão escolhida
            geocoder.geocode(
              { address: firstSuggestion },
              (results, geocodeStatus) => {
                if (geocodeStatus === "OK" && results[0]) {
                  const location = results[0].geometry.location;
                  updateMarkerAndMap(location, type);
                }
              }
            );
          }
        }
      );
    };

    // Auto-correção ao digitar e desfocar o campo
    inputField.addEventListener("blur", handleAutoCorrect);
  }

  function initAutocomplete(inputElement, type, options) {
    const autocomplete = new google.maps.places.Autocomplete(
      inputElement,
      options
    );
    autocomplete.setFields(["geometry", "formatted_address"]);

    // Listener para mudanças no local selecionado
    autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();
      if (place.geometry) {
        const location = place.geometry.location;
        updateMarkerAndMap(location, type);
      } else {
        alert("Nenhum endereço válido selecionado!");
      }
    });
  }
}

function updateAddress(location, type) {
  geocoder.geocode({ location }, (results, status) => {
    if (status === "OK" && results[0]) {
      const address = results[0].formatted_address;

      const input =
        type === "pickup"
          ? document.getElementById("pickup-search")
          : document.getElementById("dropoff-search");

      if (type === currentMode) {
        input.value = address;
      }

      console.log(`Endereço ${type} atualizado:`, address);

      // Atualizar rota automaticamente se ambos os marcadores estiverem definidos
      if (markerPickup && markerDropoff) {
        showRoute();
      }
    } else {
      console.error("Erro ao obter o endereço:", status);
    }
  });
}

function updateMarkerAndMap(location, type) {
  let marker;

  if (type === "pickup") {
    marker = markerPickup;
  } else {
    if (!markerDropoff) {
      markerDropoff = new google.maps.Marker({
        map: map,
        draggable: true,
        title: "Destino",
      });

      markerDropoff.addListener("dragend", () => {
        const draggedLocation = {
          lat: markerDropoff.getPosition().lat(),
          lng: markerDropoff.getPosition().lng(),
        };
        updateAddress(draggedLocation, "dropoff");
        if (markerPickup) {
          showRoute();
        }
      });
    }
    marker = markerDropoff;
  }

  marker.setPosition(location);
  map.setCenter(location);

  updateAddress(location, type);
}

function handleMapClick(latLng) {
  const location = {
    lat: latLng.lat(),
    lng: latLng.lng(),
  };

  if (currentMode === "pickup") {
    updateMarkerAndMap(location, "pickup");
  } else {
    updateMarkerAndMap(location, "dropoff");
  }
}

function showRoute() {
  if (!markerPickup || !markerDropoff) {
    console.log(
      "Ambos os marcadores precisam estar definidos para calcular a rota."
    );
    return;
  }

  const origin = markerPickup.getPosition();
  const destination = markerDropoff.getPosition();

  const request = {
    origin: origin,
    destination: destination,
    travelMode: google.maps.TravelMode.DRIVING,
  };

  directionsService.route(request, (result, status) => {
    if (status === google.maps.DirectionsStatus.OK) {
      directionsRenderer.setDirections(result);
    } else {
      console.error("Falha ao calcular a rota:", status);
    }
  });
}

function switchToDropoffMode() {
  const formSlider = document.getElementById("form-slider");
  formSlider.style.transform = "translateX(-50%)"; // Mostra o formulário de destino
  currentMode = "dropoff";
  if (markerDropoff) {
    const location = {
      lat: markerDropoff.getPosition().lat(),
      lng: markerDropoff.getPosition().lng(),
    };
    updateAddress(location, "dropoff");
  }
}

function switchToPickupMode() {
  const formSlider = document.getElementById("form-slider");
  formSlider.style.transform = "translateX(0)"; // Mostra o formulário de origem
  currentMode = "pickup";

  const location = {
    lat: markerPickup.getPosition().lat(),
    lng: markerPickup.getPosition().lng(),
  };
  updateAddress(location, "pickup");
}
