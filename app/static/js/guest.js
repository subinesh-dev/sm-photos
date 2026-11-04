
const consentCheckbox = document.getElementById("consent");
const continueButton = document.getElementById("continue-btn");

const consentPanel = document.getElementById("consent-panel");
const uploadPanel = document.getElementById("upload-panel");
const loadingPanel = document.getElementById("loading-panel");
const resultsPanel = document.getElementById("results-panel");

const selfieInput = document.getElementById("selfie");
const preview = document.getElementById("preview");
const previewContainer = document.getElementById("preview-container");
const searchButton = document.getElementById("search-btn");

const messageBox = document.getElementById("message");
const resultSummary = document.getElementById("result-summary");
const resultsList = document.getElementById("results-list");

let guestSessionToken = null;
let selectedSelfie = null;

// Read QR token from URL.
const url = new URL(window.location.href);
const qrToken = url.searchParams.get("token");

// Remove token from visible browser address.
if (qrToken) {
    window.history.replaceState({}, document.title, "/guest");
}

function showMessage(message) {
    messageBox.textContent = message;
    messageBox.classList.remove("hidden");
}

function hideMessage() {
    messageBox.textContent = "";
    messageBox.classList.add("hidden");
}

function showPanel(panel) {
    [
        consentPanel,
        uploadPanel,
        loadingPanel,
        resultsPanel
    ].forEach(item => item.classList.add("hidden"));

    panel.classList.remove("hidden");
    hideMessage();
}

// Verify QR token and create guest session.
async function createGuestSession() {

    if (!qrToken) {
        showMessage(
            "No event QR token found. Please scan the event QR code again."
        );
        return;
    }

    try {
        const response = await fetch("/api/guest/session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                qr_token: qrToken
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to verify event access."
            );
        }

        guestSessionToken = data.access_token;

        if (!guestSessionToken) {
            throw new Error("Guest session token was not returned.");
        }

        consentPanel.querySelector("h2").textContent =
            `Welcome to ${data.event.name}`;

    } catch (error) {
        showMessage(error.message);
        continueButton.disabled = true;
    }
}

// Enable Continue only after consent.
consentCheckbox.addEventListener("change", () => {
    continueButton.disabled = !consentCheckbox.checked;
});

continueButton.addEventListener("click", () => {

    if (!guestSessionToken) {
        showMessage(
            "Event access could not be verified. Please scan the QR again."
        );
        return;
    }

    showPanel(uploadPanel);
});

// Handle selfie selection.
selfieInput.addEventListener("change", () => {

    hideMessage();

    const file = selfieInput.files[0];

    if (!file) return;

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowedTypes.includes(file.type)) {
        selfieInput.value = "";
        selectedSelfie = null;
        searchButton.disabled = true;
        showMessage("Please select a JPG, PNG or WEBP image.");
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        selfieInput.value = "";
        selectedSelfie = null;
        searchButton.disabled = true;
        showMessage("Image size must be less than 50 MB.");
        return;
    }

    selectedSelfie = file;

    const objectUrl = URL.createObjectURL(file);
    preview.src = objectUrl;

    preview.onload = () => URL.revokeObjectURL(objectUrl);

    previewContainer.classList.remove("hidden");
    searchButton.disabled = false;
});

// Remove selected selfie.
document.getElementById("remove-btn").addEventListener("click", () => {

    selfieInput.value = "";
    selectedSelfie = null;
    preview.src = "";

    previewContainer.classList.add("hidden");
    searchButton.disabled = true;
});

// Submit selfie to guest search API.
searchButton.addEventListener("click", async () => {

    if (!selectedSelfie || !guestSessionToken) {
        showMessage("Select a selfie before searching.");
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedSelfie);

    showPanel(loadingPanel);
    searchButton.disabled = true;

    try {

        const response = await fetch("/api/guest/search", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${guestSessionToken}`
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Photo search failed."
            );
        }

        displayResults(data);

    } catch (error) {

        showPanel(uploadPanel);
        showMessage(error.message);

    } finally {
        searchButton.disabled = false;
    }
});

// Display search results.
function displayResults(data) {

    resultsList.replaceChildren();

    resultSummary.textContent =
        `${data.total_matches} matching photos found. ` +
        `${data.faces_detected} face(s) detected in your selfie.`;

    if (!data.matches || data.matches.length === 0) {

        const emptyMessage = document.createElement("p");

        emptyMessage.textContent =
            "No matching photos found. Try another clear selfie.";

        resultsList.appendChild(emptyMessage);

    } else {

        data.matches.forEach(match => {

            const card = document.createElement("div");
            card.className = "match-card";

            const filename = document.createElement("strong");
            filename.textContent = match.filename;

            const similarity = document.createElement("small");

            similarity.textContent =
                `Match similarity: ${(match.similarity * 100).toFixed(1)}%`;

            const quality = document.createElement("div");
            quality.className = "match-quality";

            quality.textContent =
                match.match_quality.replaceAll("_", " ");

            card.append(filename, similarity, quality);

            resultsList.appendChild(card);
        });
    }

    showPanel(resultsPanel);
}

// Search using another selfie.
document.getElementById("retry-btn").addEventListener("click", () => {

    selfieInput.value = "";
    selectedSelfie = null;
    preview.src = "";

    previewContainer.classList.add("hidden");
    searchButton.disabled = true;

    showPanel(uploadPanel);
});

// Start guest authentication.
createGuestSession();
