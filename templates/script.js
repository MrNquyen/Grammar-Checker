const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    fileName.textContent = "Selected: " + fileInput.files[0].name;
  } else {
    fileName.textContent = "No file chosen";
  }
});
