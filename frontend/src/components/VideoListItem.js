import React from 'react';
import './VideoListItem.css';
import { Row, Col } from 'reactstrap';

const VideoListItem = ({ video, onVideoSelect }) => {

  const imageUrl = video.snippet.thumbnails.default.url;
  // const videoId = video.id.videoId;
  const title = video.snippet.title;

  return (
    <li className="list-group-item">
      <Row>
        <Col xs="3">
          <img className="img-fluid" src={imageUrl} alt="" onClick={() => onVideoSelect(video)} />
        </Col>
        <Col xs="7">
          <span onClick={() => onVideoSelect(video)}>
            {title}
          </span>
        </Col>
        <Col xs="2">
          <a href="{ videoId }">
          </a>
          <a href="{ videoId }">
          </a>
        </Col>
      </Row>
    </li>
  );
};

export default VideoListItem;
