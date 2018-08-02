import React, { Component } from 'react';
import './SearchBar.css';
import { Input, Form } from 'reactstrap';
import './song';

export default class SearchBar extends Component {
  constructor(props) {
    super(props);
    this.addPlaylistItem = this.addPlaylistItem.bind(this);
    this.onChange = this.onChange.bind(this);

    this.state = {
      term: '',
    };
  }

  onChange = (event) => {
    this.setState({
      term: event.target.value
    });
  }

  // onKeyPress = (event) => {
  //   if (event.key === 'Enter') {
  //     this.props.onAdd(this.state);
  //     return null;
  //   }
  // }

  // setStateUtil = (property, value = undefined) => {
  //   this.setState({
  //     [property]: value,
  //   });
  // };

  render() {
        // const { title, videoId, thumbnail } = this.state;
    return (
      <Form>
        <Input
          className="form-control-lg"
          type="text" autoFocus
          placeholder="Search for a song..."
          value={this.state.term}
          onChange={e => this.onInputChange(e.target.value)}
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

