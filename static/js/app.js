function copyShortUrl() {
    const shortUrlElement = document.getElementById("shortUrl");

    if (!shortUrlElement) return;

    const text = shortUrlElement.textContent;

    navigator.clipboard.writeText(text)
        .then(() => {
            alert("Link copied to clipboard.");
        })
        .catch(() => {
            alert("Failed to copy link.");
        });
}