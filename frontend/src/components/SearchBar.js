import React, { Component } from 'react';
import './SearchBar.css';
import { Container, Input } from 'reactstrap';

export default class SearchBar extends Component {
  constructor(props) {
    super(props);
    this.state = { term: '' };
  }
  render() {
    return (
      <Container>
          <Input
            className="form-control form-control-lg"
            type="text"
            placeholder="Search for a song..."
            value={this.state.term}
            onChange={event => this.onInputChange(event.target.value)}
          />
      </Container>
    );
  }

  onInputChange(term) {
    this.setState({ term });
    this.props.onSearchTermChange(term);
  }
}
