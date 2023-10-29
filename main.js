const { app, BrowserWindow, ipcMain } = require('electron');
const windowStateKeeper = require('electron-window-state');
const { spawn } = require('child_process');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

let mainWindow;

function createWindow() {
  const mainWindowState = windowStateKeeper({
    defaultWidth: 1000,
    defaultHeight: 600,
  });

  mainWindow = new BrowserWindow({
    x: mainWindowState.x,
    y: mainWindowState.y,
    width: mainWindowState.width,
    height: mainWindowState.height,
    frame: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
    },
  });

  // Load the index.html file
  mainWindow.loadFile('index.html');

  // mainWindow.webContents.openDevTools(); // Open DevTools

  // Handle form submission from the renderer process
  ipcMain.on('form-submit', (event, data) => {
    // Parse the JSON string back into an object
    const formData = JSON.parse(data);

    // Get the email and password from the form data
    const email = formData.email;
    const password = formData.password;

    // Open the SQLite database connection
    const dbPath = path.join(__dirname, 'db', 'login.db');
    const conn = new sqlite3.Database(dbPath);

    // Insert the email and password into the database
    conn.get('SELECT 1 FROM users WHERE email = ? AND password = ?', [email, password], (err, row) => {
      if (err) {
        console.error(err.message);
        return;
      }

      // Insert the record if it doesn't exist
      if (!row) {
        const query = 'INSERT INTO users (email, password) VALUES (?, ?)';
        conn.run(query, [email, password], (err) => {
          if (err) {
            console.error(err.message);
            // Send an error response to the renderer process
            mainWindow.webContents.send('python-response', { success: false, error: err.message });
          } else {
            console.log('Data inserted successfully');
            
            // Continue with the Python process spawning here
            const pythonProcess = spawn('python', ['python/spp.py', 'getFilesFromMassar', JSON.stringify(formData)]);
            
            pythonProcess.stdout.on('data', (data) => {
              // Capture the output from the Python process
              const response = data.toString();
              // Send the response back to the renderer process
              event.sender.send('python-response', response);
            });
            
            
            pythonProcess.stderr.on('data', (data) => {
              console.error(data.toString());
            });

            pythonProcess.on('exit', (code) => {
              if (code === 0) {
                // Send a success event to the renderer process
                mainWindow.webContents.send('python-response', { success: true });
              } else {
                // Send an error event to the renderer process
                mainWindow.webContents.send('python-response', { success: false });
              }
            });
          }
        });
      } else {
        // Record already exists, continue with the Python process spawning here
        
        const pythonProcess = spawn('python', ['python/spp.py', 'getFilesFromMassar', JSON.stringify(formData)]);
        
        pythonProcess.on('exit', (code) => {
          if (code === 0) {
            // Send a success event to the renderer process
            mainWindow.webContents.send('python-response', { success: true });
          } else {
            // Send an error event to the renderer process
            mainWindow.webContents.send('python-response', { success: false });
          }
        });
        
        // Capture the output from the Python process
        pythonProcess.stdout.on('data', (data) => {
          const response = data.toString();
          // Send the response back to the renderer process
          mainWindow.webContents.send('python-response', response);
        });

        pythonProcess.stderr.on('data', (data) => {
          console.error(data.toString());
        });
      }
    });

    // Close the database connection
    conn.close();  
  });

  ipcMain.on('get-email-suggestions', (event, searchTerm) => {
    // Open the SQLite database connection
    const dbPath = path.join(__dirname, 'db', 'login.db');
    const conn = new sqlite3.Database(dbPath);

    // Query the database for email suggestions based on the search term
    const query = `SELECT email FROM users WHERE email LIKE '%${searchTerm}%'`;
    conn.all(query, [], (err, rows) => {
      if (err) {
        console.error(err.message);
        // Send an error response to the renderer process
        mainWindow.webContents.send('email-suggestions', { success: false, error: err.message });
      } else {
        // Extract email suggestions from the result rows
        const suggestions = rows.map((row) => row.email);
        // Send the email suggestions to the renderer process
        mainWindow.webContents.send('email-suggestions', { success: true, suggestions });
      }

      // Close the database connection
      conn.close();
    });
  });

  // Handle password retrieval request from the renderer process
  ipcMain.on('fetch-password', (event, email) => {
    // Open the SQLite database connection
    const dbPath = path.join(__dirname, 'db', 'login.db');
    const conn = new sqlite3.Database(dbPath);

    // Fetch the password for the provided email
    const query = 'SELECT password FROM users WHERE email = ?';
    conn.get(query, [email], function(err, row) {
      if (err) {
        console.error(err.message);
        // Send an error response to the renderer process
        event.sender.send('password-response', { success: false, error: err.message });
      } else {
        if (row) {
          const password = row.password;
          // console.log('Password retrieved successfully');
          // Send the password response to the renderer process
          event.sender.send('password-response', { success: true, password: password });
        } else {
          console.log('Email not found');
          // Send a response indicating that the email was not found in the database
          event.sender.send('password-response', { success: false, error: 'Email not found' });
        }
      }

      // Close the database connection
      conn.close();
    });
  });


  // Handle the 'get-additional-data' event from the renderer process
  ipcMain.on('get-additional-data', (event) => {
    // Spawn the Python process
    const pythonProcess = spawn('python', ['python/spp.py', 'allClasses']);

    // Capture the output from the Python process
    pythonProcess.stdout.on('data', (data) => {
      // Convert the data to a string
      const output = data.toString().trim();

      // Parse the data from a JSON string to an actual object
      const additionalData = JSON.parse(output);

      // Send the additional data back to the renderer process
      event.sender.send('additional-data', additionalData);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(data.toString());
      event.sender.send('additional-data', null); // Send null in case of an error
    });
  });


  // Handle the request to run the Python code
  ipcMain.on('run-python-code', (event, selectedValue) => {
    // Execute your Python code here
    const pythonProcess = spawn('python', ['python/spp.py', 'getStudentsFromClasse',selectedValue]);

    // Capture the output from the Python process
    pythonProcess.stdout.on('data', (data) => {
      const responseData = JSON.parse(data.toString());
      // Send the data back to the renderer process
      event.sender.send('python-data', responseData);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(data.toString());
    });
  });

  // this one is for adding notes
  ipcMain.on('run-python-function', (event, selectedValue) => {
    // Execute your Python function with the selected value
    const pythonProcess = spawn('python', ['python/spp.py', 'getAllStudents', selectedValue]);

    // Capture the output from the Python process
    pythonProcess.stdout.on('data', (students) => {
      const response = students.toString();
      // const studentsData = JSON.parse(response); // Parse the students data

      console.log("yes its work")
      // Send the response back to the renderer process
      event.sender.send('python-function-response', { success: true, data: response });
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(data.toString());

      // Send an error response to the renderer process
      event.sender.send('python-function-response', { success: false, error: data.toString() });
    });
  });

  ipcMain.on('execute-python-function', (event, inputValue, column, classe) => {
    const pythonProcess = spawn('python', ['python/spp.py', 'changeNoteOfStudent', inputValue, column, classe]);
    // Capture the output from the Python process
    pythonProcess.stdout.on('data', () => {
      

      console.log("Done")
      
      event.sender.send('send-note', { success: true });
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(data.toString());

      // Send an error response to the renderer process
      event.sender.send('send-note', { success: false, error: data.toString() });
    });
  });

  ipcMain.on('generate-rapport', (event, controleNumber, classe) => {
    const pythonProcess = spawn('python', ['python/spp.py', 'generateRapport', controleNumber, classe]);
    // Capture the output from the Python process
    pythonProcess.stdout.on('data', (response) => {
      console.log(response)
      event.sender.send('send-rapport', { success: true });
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(data.toString());

      // Send an error response to the renderer process
      event.sender.send('send-rapport', { success: false, error: data.toString() });
    });
  });

  ipcMain.on('charger-notes', (event, classe, session, loginInfo) => {
    const pythonProcess = spawn('python', ['python/spp.py', 'addToMassarNotes', classe, session, loginInfo]);
    // Capture the output from the Python process
    pythonProcess.stdout.on('data', () => {
      event.sender.send('notes-added', { success: true });
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(data.toString());

      // Send an error response to the renderer process
      event.sender.send('notes-added', { success: false, error: data.toString() });
    });

    pythonProcess.on('exit', (code) => {
      if (code === 0) {
        // Send a success event to the renderer process
        mainWindow.webContents.send('notes-added', { success: true });
      } else {
        // Send an error event to the renderer process
        mainWindow.webContents.send('notes-added', { success: false });
      }
    });
  });

  ipcMain.on('delete-files', (event) => {
    const pythonProcess = spawn('python', ['python/spp.py', 'deleteAllFiles']);
    // Capture the output from the Python process
    pythonProcess.stdout.on('data', () => {
      event.sender.send('deleted', { success: true });
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(data.toString());

      // Send an error response to the renderer process
      event.sender.send('deleted', { success: false, error: data.toString() });
    });

    pythonProcess.on('exit', (code) => {
      if (code === 0) {
        // Send a success event to the renderer process
        mainWindow.webContents.send('deleted', { success: true });
      } else {
        // Send an error event to the renderer process
        mainWindow.webContents.send('deleted', { success: false });
      }
    });
  });
  

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

ipcMain.on('close-app', () => {
  app.quit();
});

ipcMain.on('minimize-app', () => {
  mainWindow.minimize();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
