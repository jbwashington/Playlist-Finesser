import React from 'react';

function ResultItem(props) {
    return (
        <div>
        <a href={props.item.url}>
        <img src={props.item.image} />
        <h2>{props.item.title}</h2>
        <h3>{props.item.subtitle}</h3>
        <h3>{props.item.publishedAt}</h3>
        </a>
        </div>
    );
}

export default ResultItem;
