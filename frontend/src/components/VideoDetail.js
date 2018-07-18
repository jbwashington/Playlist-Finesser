import React from 'react';
import Timestamp from 'react-timestamp';
import './VideoDetail.css';
import {Container,Row} from 'reactstrap';

const VideoDetail = ({ video }) => {
  if (!video) {
    return (
      <Container>
        <Row>
          {/*<span className="loader"></span>*/}
          <p className="text-center">
            Loading
            <span className="dot">.</span>
            <span className="dot">.</span>
            <span className="dot">.</span>
          </p>
        </Row>
      </Container>
    );
  }

  // const videoId = video.id.videoId;
  // const url = `https://www.youtube.com/embed/${videoId}`;

  return (
    <Container>
      <p className="font-weight-bold">
        {video.snippet.title}
      </p>
      <small>
        Published by {video.snippet.channelTitle} on{' '}
        <Timestamp time={video.snippet.publishedAt} precision={2} />
      </small>
    </Container>
  );
};

export default VideoDetail;
