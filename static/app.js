const input = document.getElementById("fileInput");
const selected = document.getElementById("selectedFile");
const nameEl = document.getElementById("fileName");
const sizeEl = document.getElementById("fileSize");
const zone = document.getElementById("dropZone");

function showFile(file) {
    if (!file) return;
    selected.hidden = false;
    nameEl.textContent = file.name;
    sizeEl.textContent = formatBytes(file.size);
}

function formatBytes(bytes) {
    if (!bytes) return "0 Bytes";
    const units = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${units[i]}`;
}

input.addEventListener("change", () => showFile(input.files[0]));

["dragenter", "dragover"].forEach(e =>
    zone.addEventListener(e, event => {
        event.preventDefault();
        zone.classList.add("dragging");
    })
);

["dragleave", "drop"].forEach(e =>
    zone.addEventListener(e, event => {
        event.preventDefault();
        zone.classList.remove("dragging");
    })
);

zone.addEventListener("drop", event => {
    if (event.dataTransfer.files.length) {
        input.files = event.dataTransfer.files;
        showFile(event.dataTransfer.files[0]);
    }
});

function copyLink() {
    const link = document.getElementById("shareLink");
    navigator.clipboard.writeText(link.value);
    const button = link.nextElementSibling;
    button.textContent = "Copied!";
    setTimeout(() => button.textContent = "Copy", 1500);
}
