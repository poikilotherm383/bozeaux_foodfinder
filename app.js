async function runSearch(type) {

    const container = document.getElementById("card-container")

    container.innerHTML =
        '<div class="spinner"></div>'

    navigator.geolocation.getCurrentPosition(async pos => {

        const lat = pos.coords.latitude
        const lon = pos.coords.longitude

        const payload = {
            type: type,
            lat: lat,
            lon: lon
        }

        const response = await fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })

        const data = await response.json()

        renderCards(data)

    })
}


function renderCards(data) {

    const container = document.getElementById("card-container")
    container.innerHTML = ""

    data.forEach(place => {

        const card = document.createElement("div")
        card.className = "card"

        const mapsUrl =
            `https://maps.apple.com/?daddr=${place.lat},${place.lon}`

        card.innerHTML = `
            <div class="card-title">
                <a href="${place.url}" target="_blank">
                    ${place.name}
                </a>
            </div>

            Closes: ${place.closes_at}<br>

            Distance: ${place.distance.toFixed(1)} mi<br>

            <a href="${mapsUrl}" target="_blank">
                ${place.address}
            </a>
        `

        container.appendChild(card)
    })
}