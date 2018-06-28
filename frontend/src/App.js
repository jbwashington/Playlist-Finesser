import debounce             from 'lodash.debounce';
import React, { Component } from 'react';
import                           './App.css';
import Config               from './config';
import SearchBar            from './components/SearchBar';
import VideoDetail          from './components/VideoDetail';
import VideoList            from './components/VideoList';
import SongQueue            from './components/SongQueue';
import YTSearch             from 'youtube-api-search';
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
    Button
} from 'reactstrap';

const REACT_APP_API_KEY = Config.YT_API_KEY;

class App extends Component {
    constructor(props) {
        super(props);
        this.toggle = this.toggle.bind(this);
        this.state = {
            videos: [], // holds 5 videos fetched from API
            selectedVideo: null, 
            isOpen: false
        };

        this.videoSearch('type beat'); // default search term
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
    render() {
        // for consistent ui such that it re-renders after 300ms on search
        const videoSearch = debounce(term => {
            this.videoSearch(term);
        }, 300);

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
            <Col md="3">
            <SearchBar onSearchTermChange={videoSearch} />
            <VideoDetail video={this.state.selectedVideo} />
            <VideoList
            videos={ this.state.videos }
            onVideoSelect = { selectedVideo => {
                this.setState({ selectedVideo });
            }
            }
            />
            <Button
            tag="a"
            className="btn btn-primary"
            size="small"
            href="#"
            target="_blank"
            >
            Add Songs to Playlist
            </Button>
            </Col>
            <Col md="8">
            <SongQueue playlist = {this.state.selectedPlaylist} />
            </Col>
            </Row>
            </Container>

            <Footer/>
            </div>
        );
    }
}

export default App;
