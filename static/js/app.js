document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("natal-form")
  const chartContainer = document.getElementById("chart-container")
  const chartDisplay = document.getElementById("chart-display")
  const chartInfo = document.getElementById("chart-info")
  const chartTitle = document.getElementById("chart-title")
  const btnDownload = document.getElementById("btn-download")
  const btnPrint = document.getElementById("btn-print")
  const btnLocation = document.getElementById("btn-location")
  const loading = document.getElementById("loading")
  const widthSlider = document.getElementById("width")
  const widthValue = document.getElementById("width-value")

  // Actualizar el valor del ancho en tiempo real
  widthSlider.addEventListener("input", function () {
    widthValue.textContent = `${this.value}px`
  })

  // Obtener ubicación actual
  btnLocation.addEventListener("click", () => {
    if (navigator.geolocation) {
      loading.style.display = "flex"
      navigator.geolocation.getCurrentPosition(
        (position) => {
          document.getElementById("lat").value = position.coords.latitude
          document.getElementById("lon").value = position.coords.longitude
          loading.style.display = "none"
        },
        (error) => {
          alert("Error al obtener la ubicación: " + error.message)
          loading.style.display = "none"
        },
      )
    } else {
      alert("La geolocalización no está soportada por este navegador.")
    }
  })

  // Referencia al contenedor de selección de fondos
  const backgroundSelector = document.getElementById("background-selector")
  let selectedBackground = "template-1" // Valor por defecto

  // Cargar los fondos disponibles
  fetch("/static/images/backgrounds")
    .then((response) => response.json())
    .then((data) => {
      // Limpiar el contenedor
      backgroundSelector.innerHTML = ""

      // Crear el contenedor de miniaturas
      const thumbnailsContainer = document.createElement("div")
      thumbnailsContainer.className = "thumbnails-container"

      // Añadir las miniaturas
      data.backgrounds.forEach((bg) => {
        const thumbnailItem = document.createElement("div")
        thumbnailItem.className = "thumbnail-item"
        thumbnailItem.dataset.value = bg.id

        if (bg.id === selectedBackground) {
          thumbnailItem.classList.add("selected")
        }

        const thumbnail = document.createElement("img")
        thumbnail.src = `/static/images/backgrounds/thumbnails/${bg.thumbnail}`
        thumbnail.alt = bg.name
        thumbnail.title = bg.description

        const name = document.createElement("span")
        name.textContent = bg.name

        thumbnailItem.appendChild(thumbnail)
        thumbnailItem.appendChild(name)

        // Evento de clic para seleccionar
        thumbnailItem.addEventListener("click", () => {
          // Quitar la clase selected de todos
          document.querySelectorAll(".thumbnail-item").forEach((item) => {
            item.classList.remove("selected")
          })

          // Añadir la clase selected al elemento clicado
          thumbnailItem.classList.add("selected")

          // Actualizar el valor seleccionado
          selectedBackground = bg.id
        })

        thumbnailsContainer.appendChild(thumbnailItem)
      })

      backgroundSelector.appendChild(thumbnailsContainer)
    })
    .catch((error) => {
      console.error("Error al cargar los fondos:", error)
      backgroundSelector.innerHTML = "<p>Error al cargar los fondos. Usando el fondo predeterminado.</p>"
    })

  // Enviar formulario
  form.addEventListener("submit", (e) => {
    e.preventDefault()

    const name = document.getElementById("name").value
    const date = document.getElementById("date").value
    const time = document.getElementById("time").value
    const lat = Number.parseFloat(document.getElementById("lat").value)
    const lon = Number.parseFloat(document.getElementById("lon").value)
    const width = Number.parseInt(document.getElementById("width").value)
    const background_id = selectedBackground

    // Validar datos
    if (!name || !date || !time || isNaN(lat) || isNaN(lon)) {
      alert("Por favor, completa todos los campos correctamente.")
      return
    }

    // Formatear fecha y hora para el backend
    const utc_dt = `${date} ${time}`

    // Datos para enviar
    const data = {
      name,
      utc_dt,
      lat,
      lon,
      width,
      background_id,
    }

    // Mostrar cargando
    loading.style.display = "flex"

    // Enviar solicitud
    fetch("/generar_carta_natal", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((err) => {
            throw err
          })
        }
        return response.text()
      })
      .then((svgData) => {
        // Mostrar la carta
        chartDisplay.innerHTML = svgData

        // Actualizar título
        chartTitle.textContent = `Carta Natal de ${name}`

        // Mostrar información adicional
        const dateObj = new Date(`${date}T${time}`)
        const formattedDate = dateObj.toLocaleDateString("es-ES", {
          day: "numeric",
          month: "long",
          year: "numeric",
        })
        const formattedTime = dateObj.toLocaleTimeString("es-ES", {
          hour: "2-digit",
          minute: "2-digit",
        })

        chartInfo.innerHTML = `
                <p><strong>Nombre:</strong> ${name}</p>
                <p><strong>Fecha de nacimiento:</strong> ${formattedDate}</p>
                <p><strong>Hora de nacimiento:</strong> ${formattedTime}</p>
                <p><strong>Coordenadas:</strong> ${lat.toFixed(4)}, ${lon.toFixed(4)}</p>
                <p><strong>Fondo:</strong> ${document.querySelector(`.thumbnail-item[data-value="${background_id}"] span`).textContent}</p>
            `

        // Mostrar contenedor de la carta
        chartContainer.style.display = "block"

        // Habilitar botones
        btnDownload.disabled = false
        btnPrint.disabled = false

        // Scroll a la carta
        chartContainer.scrollIntoView({ behavior: "smooth" })
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Error al generar la carta natal: " + (error.error || "Error desconocido"))
      })
      .finally(() => {
        loading.style.display = "none"
      })
  })

  // Descargar SVG
  btnDownload.addEventListener("click", () => {
    const svg = chartDisplay.querySelector("svg")
    if (!svg) return

    const svgData = new XMLSerializer().serializeToString(svg)
    const blob = new Blob([svgData], { type: "image/svg+xml" })
    const url = URL.createObjectURL(blob)

    const link = document.createElement("a")
    link.href = url
    link.download = `carta_natal_${document.getElementById("name").value.replace(/\s+/g, "_")}.svg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  })

  // Imprimir carta
  btnPrint.addEventListener("click", () => {
    const printWindow = window.open("", "_blank")
    const svg = chartDisplay.querySelector("svg")
    if (!svg) return

    const svgData = new XMLSerializer().serializeToString(svg)
    const name = document.getElementById("name").value

    printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Carta Natal de ${name}</title>
                <style>
                    body {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        font-family: "Cinzel", serif;
                        background-color: #ffffff;
                        color: #2d3748;
                    }
                    h1 {
                        color: #d4af37;
                        font-family: "Cinzel", serif;
                        margin-bottom: 1.5rem;
                    }
                    .info {
                        margin: 20px 0;
                        padding: 20px;
                        background-color: #f7fafc;
                        border-radius: 4px;
                        font-family: "Montserrat", sans-serif;
                        border: 1px solid #e2e8f0;
                    }
                </style>
            </head>
            <body>
                <h1>Carta Natal de ${name}</h1>
                <div class="info">
                    ${chartInfo.innerHTML}
                </div>
                ${svgData}
                <script>
                    window.onload = function() {
                        setTimeout(function() {
                            window.print();
                            window.close();
                        }, 500);
                    }
                </script>
            </body>
            </html>
        `)
  })
})

