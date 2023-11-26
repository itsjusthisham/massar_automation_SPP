const { ipcRenderer } = require('electron');
const path = require('path');
const Swal = require('sweetalert2');


// Close the application
document.getElementById('close-btn').addEventListener('click', () => {
  ipcRenderer.send('close-app');
});

// Minimize the application
document.getElementById('minimize-btn').addEventListener('click', () => {
    ipcRenderer.send('minimize-app');
  });








  
