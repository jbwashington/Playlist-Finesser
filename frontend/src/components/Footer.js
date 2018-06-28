import React from 'react';
import'./Footer.css';
const Footer = () => {
	return (
		<footer className="footer">
			<div className="container">
				<div className="content has-text-centered">
					<p className="logo">
						<i className="fa fa-youtube-play fa-lg" />&nbsp;<strong>Playlist Finesser</strong>&nbsp;
						<i className="fa fa-code fa-lg" /> by&nbsp;
						<a href="https://github.com/jbwashington">James Washington</a>. The
						source code is licensed under MIT and is available on &nbsp;
						<a href="https://github.com/jbwashington">
							<i className="fa fa-github fa-lg" />
						</a>
					</p>
					<p />
				</div>
			</div>
		</footer>
	);
};

export default Footer;
