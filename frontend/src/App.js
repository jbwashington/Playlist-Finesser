import debounce             from 'lodash.debounce';
import React, { Component } from 'react';
import YTSearch             from 'youtube-api-search';
import                           './App.css';
import Config               from './config';
import SearchBar            from './components/SearchBar';
import VideoDetail          from './components/VideoDetail';
import VideoList            from './components/VideoList';
import Player               from './components/Player';
import Playlist             from './components/Playlist';
import Footer               from './components/Footer';
import {
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink,
  Container,
  Col,
  Row,
} from 'reactstrap';

const REACT_APP_API_KEY = Config.YT_API_KEY;

class App extends Component {
  constructor(props) {
    super(props);
    this.toggle = this.toggle.bind(this);
    this.videoSearch('type beat'); // default search term
    this.state = {
      videos: [], // holds 5 videos fetched from API
      playlist: [],
      term: '',
      selectedVideo: null,
      playing: false,
      isOpen: false
    };
  }

  toggle() {
    this.setState({
      isOpen: !this.state.isOpen
    });
  }

  // function for search term
  videoSearch(term) {
    YTSearch(
      {
        key: REACT_APP_API_KEY,
        term: term
      },
      videos => {
        this.setState({ videos: videos, selectedVideo: videos[0] }); // through states setting the default video
      }
    );
  }

  renderVideoDetail () {
    if (!this.state.selectedVideo) {
      return <div>Loading...</div>
    }
    return <VideoDetail video={ this.state.selectedVideo } />
  }

  // function for adding song to playlist
  onSubmit = (event) => {
    event.preventDefault();
    this.setState({
      term: '',
      playlist : [...this.state.playlist, this.state.selectedVideo.id.displayId]
    })
    console.log('query submitted ==> ', event);
    console.log(this.state.playlist);
  }

  render() {
    // for consistent ui such that it re-renders after 300ms on search
    const videoSearch = debounce(term => {
      this.videoSearch(term);
    }, 600);


    return (

      <div>
        <Navbar color="inverse" light expand="md">
          <NavbarBrand href="/">FINESSE.FM</NavbarBrand>
          <NavbarToggler onClick={this.toggle} />
          <Collapse isOpen={this.state.isOpen} navbar>
            <Nav className="ml-auto" navbar>
              <NavItem>
                <NavLink href="#">Register</NavLink>
              </NavItem>
              <NavItem>
                <NavLink href="#">Sign In</NavLink>
              </NavItem>
            </Nav>
          </Collapse>
        </Navbar>

        <Container>

          <Row>
            <Col md="4">
              <SearchBar value={this.state.term} onSearchTermChange={videoSearch} />
              <VideoDetail video={this.state.selectedVideo} />
              <VideoList
                videos = { this.state.videos }
                onVideoSelect = { selectedVideo => {
                  this.setState({ selectedVideo });
                }
                }
              />
            </Col>

            <Col md="8">
              <Player/>
              <Playlist items={this.state.playlist} />
            </Col>
          </Row>
        </Container>

        <Footer/>
      </div>
    );
  }
}

export default App;
