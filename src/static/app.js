const LOCATION_TIMEOUT = 5000;
let locationTimer;
window.addEventListener("load", () => {
    locationTimer = setTimeout(() => {
        if(!userLocation) {
            showModal("Location must be enabled to use the foodfinder. Check your location permission settings, and make sure to click \"allow\" when prompted to share your location.");
        }
    }, LOCATION_TIMEOUT)
})

let userLocation = null;
navigator.geolocation.getCurrentPosition(
    pos => {
        clearTimeout(locationTimer);
        userLocation = {
            lat: pos.coords.latitude,
            lon: pos.coords.longitude
        };
    },
    err => {
        if (err.code === err.PERMISSION_DENIED) {
            showModal(
                "Location access was denied. Enable it in your browser settings."
            );
        }
    },
    {timeout: LOCATION_TIMEOUT}
)

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

async function fetchWithTimeout(url, options={}, timeout=15000){
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    try{
        const response = await fetch(url,{
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    }catch(err){
        clearTimeout(id);
        if(err.name === "AbortError"){
            showModal("Request timed out.");
        }else{
            showModal("Network error.");
        }
        throw err;
    }
}

async function runSearch(type) {
    if (!userLocation) {
            showModal("Location data still loading. Try again in a few seconds or, if the problem persists, check your location permission settings.")
        return;
    }
    const BASE_URL = window.APP_CONFIG.url_root;
    setActiveButton(type)
    showSkeletons()
    const payload = {
        type: type,
        lat: userLocation.lat,
        lon: userLocation.lon
    }
    let response;
    try {
        response = await fetchWithTimeout(`${BASE_URL}/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
    }catch (e){
        clearCards();
        return;
    }
    const data = await response.json()
    if(response.ok) {
        renderCards(data);
        return;
    }
    if(response.status == 404 && data.empty) {
        showModal(`${data.message} Expand search?`, [
            {
                text: "OK",
                action: () => runExpandedSearch(type)
            }
        ]);
        return
    }
    if("message" in data) {
        showModal(`Server error: ${data.message}`);
        return;
    }
    showModal("An unknown server error occurred.");
    return;
}

async function runExpandedSearch(type) {
    if (!userLocation) {
        return;
    }
    const BASE_URL = window.APP_CONFIG.url_root;
    showSkeletons()
    const payload = {
        type: type,
        lat: userLocation.lat,
        lon: userLocation.lon
    }
    let response;
    try {
        response = await fetchWithTimeout(`${BASE_URL}/search_expand`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
    }catch (e){
        return;
    }
    const data = await response.json()
    if(response.ok) {
        renderCards(data);
        return;
    }
    if(response.status == 404 && data.empty) {
        showModal(data.message);
        return
    }
    if("message" in data) {
        showModal(`Server error: ${data.message}`);
        return;
    }
    showModal("An unknown server error occurred.");
    return;
}

function clearCards(){
    document.getElementById("card-container").innerHTML = "";
}

function renderCards(data) {
    if(!data || data.length === 0) {
        showModal("No places found.");
        return;
    }
    const container = document.getElementById("card-container")
    container.innerHTML = ""
    data.forEach(place => {
        let title_html;
        if(!place.url) {
            title_html = place.name;
        }else {
            title_html = `<a href="${place.url}" target="_blank" rel="noopener noreferrer">${place.name}</a>`;
        }
        const mapsUrl =
            `https://maps.apple.com/?daddr=${place.lat},${place.lon}`
        const card = document.createElement("div")
        card.className = "card"
        card.innerHTML = `
        <div class="card-title">
            ${title_html}
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
// shows the appropriate modal
function showModal(message, buttons=[]) {
    const modal = document.getElementById("modal");
    const msg = document.getElementById("modal-message");
    const btnArea = document.getElementById("modal-buttons");
    msg.textContent = message;
    btnArea.innerHTML = "";
    buttons.forEach(btn => {
        const b = document.createElement("button");
        b.textContent = btn.text;
        b.onclick = () => {
            hideModal();
            btn.action();
        };
        b.className = "modal-button";
        btnArea.appendChild(b);
    });
    const okb = document.createElement("button");
    okb.textContent = "Close";
    okb.onclick = () => {
        hideModal();
        clearCards();
    };
    okb.className = "modal-button";
    btnArea.appendChild(okb);
    modal.classList.remove("hidden");
}

function hideModal(){
    document.getElementById("modal").classList.add("hidden");
}

// logs some text to a div on screen for debug on mobile.
function debug(msg) {
    const el = document.getElementById("debug")
    el.innerText = msg
}