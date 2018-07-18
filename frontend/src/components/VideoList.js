import React from 'react';
import VideoListItem from './VideoListItem';
import './VideoList.css';

const VideoList = props => {


  const videoItems = props.videos.map(video => {
    return (
      <VideoListItem
        key={video.id.videoId}
        video={video}
        onVideoSelect={props.onVideoSelect}
      />
    );
  });
  return (
    <div
      className="list-group list-group-flush"
      id="list-tab"
      role="tablist"
    >
      {videoItems}
    </div>
  );
};

export default VideoList;
