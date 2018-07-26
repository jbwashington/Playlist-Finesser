import React from 'react';

const Playlist = props => (
  <ul className="list-group">
    { props.items.map((item, index) => <li className="list-item" key={index}>{item}</li>) }
  </ul>
)

export default Playlist;
