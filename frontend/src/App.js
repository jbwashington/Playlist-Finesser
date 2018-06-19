import React, { Component } from 'react'

// Material-UI
import RaisedButton from 'material-ui/RaisedButton'
import TextField from 'material-ui/TextField'

// Theme
import { deepOrange500 } from 'material-ui/styles/colors'
import getMuiTheme from 'material-ui/styles/getMuiTheme'
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider'

// Font
import 'typeface-roboto'

// Click handler
import injectTapEventPlugin from 'react-tap-event-plugin'
injectTapEventPlugin()

// Styles
const styles = {
	container: {
		textAlign: 'center',
		paddingTop: 50
	}
}

// Theme
const muiTheme = getMuiTheme({
	palette: {
		accent1Color: deepOrange500
	}
})

class App extends Component {
	constructor (props, context) {
		super(props, context)

		// Default text
		this.state = {
			text: 'Young Thug - Digits'
		}
	}

	onSubmit = e => {
		// No real submit
		e.preventDefault()

		// Get input value
		const text = this.refs.cool_text.input.value

		// Set state
		this.setState({
			text
		})

		// Do something with text
		alert(`You said : ${text}`)
	}

	render () {
		return (
			<MuiThemeProvider muiTheme={muiTheme}>
			<div style={styles.container}>
			<h1>Playlist Finesser</h1>
			<h2>Create playlists from any song on the web.</h2>
			<form onSubmit={this.onSubmit}>
			<TextField
			ref='cool_text'
			floatingLabelText='Type a song below:'
			defaultValue={this.state.text}
			/>
			<br />
			<RaisedButton type='submit' label='Search' primary />
			</form>
			</div>
			</MuiThemeProvider>
		)
	}
}

export default App
