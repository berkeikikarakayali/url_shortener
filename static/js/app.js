function copyShortUrl() {
    const shortUrl = document.getElementById("shortUrl");
    const copyButton = document.getElementById("copyButton");

    if (!shortUrl || !copyButton) return;

    const text = shortUrl.textContent;
    const defaultText = copyButton.textContent;

    navigator.clipboard.writeText(text)
        .then(() => {
            copyButton.textContent = "Copied!";
            copyButton.disabled = true;

            setTimeout(() => {
                copyButton.textContent = defaultText;
                copyButton.disabled = false;
            }, 1500);
        })
        .catch(() => {
            copyButton.textContent = "Error";

            setTimeout(() => {
                copyButton.textContent = defaultText;
            }, 1500);
        });
}