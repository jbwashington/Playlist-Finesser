import React from 'react';
import Config               from './config';
import fetch from 'unfetch';

const REACT_APP_API_KEY = Config.YT_API_KEY;
const YT_URL_1 = "https://youtube/v3/search?part=snippet&key=";
const YT_URL_2 = "&type=video&q=";
const YT_FINAL_URL = YT_URL_1+REACT_APP_API_KEY+YT_URL_2

function YoutubeSearchExtension(query) {
	const options = {
		headers: {
			Accept: 'application/json',
		},
		prom = fetch(YT_FINAL_URL+query, options),
		url = "https://youtube/v3/search?part=snippet&key=AIzaSyAN0pUr2wN-ZuAVqICIt2RR_ZGgvUOx3xU${query}";
	}
	return prom.then(resp =>
		resp.items.map(item => ({
			title: item.snippet.title,
			subtitle: item.snippet.publishedAt,
			image: item.snippet.thumbnails.default.url,
			url: video_url_prefix+item.video_url
		}))
	);
};


export default YoutubeSearchExtension;
