import React, { useState, useEffect } from 'react';

const PlayerList = () => {
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    fetch('/api/players')
      .then(response => response.json())
      .then(data => setPlayers(data));
  useEffect(() => {
    fetch('/api/players')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => setPlayers(data))
      .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
      });
  }, []);

  return (
    <div>
      <h1>Player List</h1>
      <ul>
        {players.map(player => (
          <li key={player.id}>{player.name}</li>
        ))}
      </ul>
    </div>
  );
};

export default PlayerList;
