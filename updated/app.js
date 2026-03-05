function setActiveButton(type) {

    const buttons = document.querySelectorAll(".action-button")

    buttons.forEach(btn => btn.classList.remove("active"))

    if (type === "restaurant")
        document.getElementById("btn-restaurant").classList.add("active")

    if (type === "coffee_shop")
        document.getElementById("btn-coffee").classList.add("active")

    if (type === "chick_fil_a")
        document.getElementById("btn-chicken").classList.add("active")

}



function showSkeletons() {

    const container = document.getElementById("card-container")

    container.innerHTML = ""

    for (let i = 0; i < 5; i++) {

        const skel = document.createElement("div")

        skel.className = "skeleton"

        container.appendChild(skel)

    }

}



async function runSearch(type) {

    setActiveButton(type)

    showSkeletons()

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

        const mapsUrl =
            `https://maps.apple.com/?daddr=${place.lat},${place.lon}`

        const card = document.createElement("div")

        card.className = "card"

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