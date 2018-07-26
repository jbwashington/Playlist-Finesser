import React, { Component } from 'react';
import './SearchBar.css';
import { Input, Form } from 'reactstrap';

export default class SearchBar extends Component {
  constructor(props) {
    super(props);
    this.addPlaylistItem = this.addPlaylistItem.bind(this);
    this.onChange = this.onChange.bind(this);
    this.state = {
      term: '',
      playlist: [],
    };
  }

  onChange = (event) => {
    this.setState({
      term: event.target.value
    });
  }

  onSubmit = (event) => {
    this.setState({
      term: event.target.value
    });
  }

  render() {
    return (
      <Form>
          <Input
            className="form-control-lg"
            type="text"
            placeholder="Search for a song..."
            value={this.state.term}
            onSubmit={event => this.addPlaylistItem(event.target.value)}
            onChange={event => this.onInputChange(event.target.value)}
          />
      </Form>
    );
  }

  onInputChange(term) {
    this.setState({ term });
    this.props.onSearchTermChange(term);
  }

  addPlaylistItem = (selectedVideo) => {
    this.preventDefault();
    console.log(selectedVideo);
    this.setState({
      playlist: this.state.playlist,
    })
  };
}

