import React from 'react';

function ResultListItem(props) {
  return (
    <li>
      <a href={ props.item.url }>
        <img
          alt={ props.item.title }
          src={ props.item.image }
        />
        <p>{ props.item.title }</p>
        <p>{ props.item.subtitle }</p>
        <p>{ props.item.publishedAt }</p>
      </a>
    </li>
  );
}

export default ResultListItem;
