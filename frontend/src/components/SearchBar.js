import React, { Component } from 'react';
import './SearchBar.css';
import { Container } from 'reactstrap';

export default class SearchBar extends Component {
	constructor(props) {
		super(props);
		this.state = { term: '' };
	}
	render() {
		return (
			<Container>
				<div className="input-group mb-3">
					<input
						className="input-group-prepend"
						type="text"
						placeholder="Search for a song..."
						value={this.state.term}
						onChange={event => this.onInputChange(event.target.value)}
					/>
				</div>
			</Container>
		);
	}

	onInputChange(term) {
		this.setState({ term });
		this.props.onSearchTermChange(term);
	}
}
