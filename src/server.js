const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const port = 3000;

// Middleware pour permettre les requêtes CORS
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*'); // Permettre l'accès depuis n'importe quelle origine
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE'); // Méthodes autorisées
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization'); // En-têtes autorisés
  if (req.method === 'OPTIONS') {
    res.sendStatus(200); // Répondre immédiatement aux requêtes OPTIONS
  } else {
    next(); // Passer au prochain middleware
  }
});

// Endpoint pour récupérer la liste des fichiers JSON
app.get('/api/tree-files', async (req, res) => {
  try {
    const files = await fs.readdir(path.join(__dirname, 'trees')); // Lire les fichiers dans le répertoire 'trees'
    const jsonFiles = files.filter(file => file.endsWith('.json')); // Filtrer seulement les fichiers JSON
    console.log(jsonFiles)
    res.json(jsonFiles);
  } catch (error) {
    console.error('Error reading tree files:', error);
    res.status(500).json({ error: 'Unable to retrieve tree files', details: error.message });
  }
});

// Servir les fichiers statiques depuis le répertoire 'trees'
app.use('/api/trees', express.static(path.join(__dirname, 'trees')));

// Lancer le serveur
app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
