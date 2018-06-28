import React from 'react';
import Timestamp from 'react-timestamp';

import './VideoDetail.css';

import {
    Container,
    Row
} from 'reactstrap';


const VideoDetail = ({ video }) => {
    if (!video) {
        return (
            <div className="block">
            {/*<span className="loader"></span>*/}
            <h4 className="title is-2 is-unselectable is-centered">
            Loading
            <span className="dot">.</span>
            <span className="dot">.</span>
            <span className="dot">.</span>
            </h4>
            </div>
        );
    }

    // const videoId = video.id.videoId;
    // const url = `https://www.youtube.com/embed/${videoId}`;

    return (
        <div>
            <Container>
                <Row>
                    <div className="video-detail column is-8">
                        <div className="box video-meta">
                            <div className="video-title">
                                {video.snippet.title}
                            </div>
                            <small>
                                by {video.snippet.channelTitle}, Published on{' '}
                                <Timestamp time={video.snippet.publishedAt} precision={2} />
                            </small>
                        </div>
                    </div>
                </Row>
            </Container>
        </div>
    );
};

export default VideoDetail;
