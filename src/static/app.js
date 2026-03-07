let userLocation = null;

navigator.geolocation.getCurrentPosition(pos => {
    userLocation = {
        lat: pos.coords.latitude,
        lon: pos.coords.longitude
    }
})

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

    if (!userLocation) {
        console.log("Location not ready yet.");
        return;
    }
    debug("location ready")

    const BASE_URL = window.APP_CONFIG.url_root;

    setActiveButton(type)

    showSkeletons()
    debug("skeletons shown")

    const payload = {

        type: type,
        lat: userLocation.lat,
        lon: userLocation.lon

    }
    debug("payload generated")

    const response = await fetch(`${BASE_URL}/search`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(payload)

    })
    debug("payload fetched")

    const data = await response.json()

    renderCards(data)

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

// logs some text to a div on screen for debug on mobile.
function debug(msg) {
    const el = document.getElementById("debug")
    el.innerText = msg
}

// logs whether or not the context is considered secure.
window.addEventListener("DOMContentLoaded", () => {

    debug("Secure context: " + window.isSecureContext)

})