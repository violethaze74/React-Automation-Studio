
import React, { Component } from 'react';

//import AutomationStudioContext from '../SystemComponents/AutomationStudioContext';


//import './App.css';
//import io from 'socket.io-client';
import Routes from './routes'

import 'typeface-roboto';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';

import AutomationStudioContext from './components/SystemComponents/AutomationStudioContext';
import { blue, indigo,pink, red, green,cyan,lime } from '@material-ui/core/colors'
import io from 'socket.io-client';
import { Redirect } from 'react-router-dom'
import LogIn from './LogIn';

// const socket = io('https://172.16.5.52:5000/test',{
//   transports: ['websocket'],
//   secure:true
// })


//console.log('process.env',process.env)
let port;
if(typeof process.env.REACT_APP_PyEpicsServerPORT==='undefined'){
  port= 5000;
}
else{
  port=process.env.REACT_APP_PyEpicsServerPORT;
}

let pvServerBASEURL;
if(typeof process.env.REACT_APP_PyEpicsServerBASEURL==='undefined'){
  pvServerBASEURL= "http://127.0.0.1";
}
else{
  pvServerBASEURL=process.env.REACT_APP_PyEpicsServerBASEURL;
}

let pvServerNamespace;
if(typeof process.env.REACT_APP_PyEpicsServerNamespace==='undefined'){
  pvServerNamespace= "pvServer";
}
else{
  pvServerNamespace=process.env.REACT_APP_PyEpicsServerNamespace;
}

let PyEpicsServerURL=pvServerBASEURL+":"+port+"/"+pvServerNamespace;



let socket = io(PyEpicsServerURL,{
  transports: ['websocket'],
})



/*
const socket = io('127.0.0.1:5000/test',{
transports: ['websocket']
})*/
let themeStyle='dark';
class App extends Component {
  constructor(props) {
    super(props);

    let themeStyle= JSON.parse(localStorage.getItem('themeStyle'));

    //console.log('jwt',jwt);
    if(!themeStyle){
      themeStyle='dark'
      localStorage.setItem('themeStyle', JSON.stringify(themeStyle));
    }

    console.log(themeStyle)
    let theme = createMuiTheme({
      palette: {
        type:themeStyle,
        primary: themeStyle=='dark'?cyan:indigo,
        secondary:pink,
        error: pink,
        action:green,
        // Used by `getContrastText()` to maximize the contrast between the background and
        // the text.
        contrastThreshold: 3,
        // Used to shift a color's luminance by approximately
        // two indexes within its tonal palette.
        // E.g., shift from Red 500 to Red 300 or Red 700.
        tonalOffset: 0.2,



      },
      lightLineColors:['#12939A', '#79C7E3', '#1A3177', '#FF9833', '#EF5D28'],
      darkLineColors:['#ff9800', '#f44336', '#9c27b0', '#3f51b5', '#e91e63'],
      typography: {
        useNextVariants: true,
        fontFamily: [

          'Roboto',


        ].join(','),
      },
    });

    this.toggleTheme=()=>{
      //console.log(this.state.themeStyle)
      let themeStyle=this.state.themeStyle;
      if (themeStyle=='dark'){
        themeStyle='light';
      }
      else {
        themeStyle='dark';
      }

      let theme = createMuiTheme({
        palette: {
          type:themeStyle,
          primary: themeStyle=='dark'?cyan:indigo,
          secondary:pink,
          error: pink,
          action:green,
          // Used by `getContrastText()` to maximize the contrast between the background and
          // the text.
          contrastThreshold: 3,
          // Used to shift a color's luminance by approximately
          // two indexes within its tonal palette.
          // E.g., shift from Red 500 to Red 300 or Red 700.
          tonalOffset: 0.2,



        },
        lightLineColors:['#12939A', '#79C7E3', '#1A3177', '#FF9833', '#EF5D28'],
        darkLineColors:['#ff9800', '#f44336', '#9c27b0', '#3f51b5', '#e91e63'],
        typography: {
          useNextVariants: true,
          fontFamily: [

            'Roboto',


          ].join(','),
        },
      });
      this.setState({themeStyle:themeStyle,theme:theme} )
      localStorage.setItem('themeStyle', JSON.stringify(themeStyle));
    }
    this.setUserData=(username)=>{
      let system=this.state.system;
      let userData={ 
        username:username,
        roles:[]
      };
      system.userData=userData;
    
      this.setState({system:system})
    }
    this.logout=()=>{
      localStorage.removeItem('jwt');
      let system=this.state.system;
      let userData={ 
        username:'',
        roles:[]
      };
      system.userData=userData;
    
      this.setState({system:system})
    }
    this.updateLocalVariable = (name,data) => {
      let system=this.state.system;
      let localVariables=system.localVariables;

      localVariables[name]=data;
      system.localVariables=localVariables
      this.setState({
        system:system,

      });
      //console.log('name',name)
      //console.log('data',data)
    };
    let userData={ 
      username:'',
      roles:[]
    };
   
    let localVariables={};
    let system={socket:socket,toggleTheme:this.toggleTheme,localVariables:localVariables,updateLocalVariable:this.updateLocalVariable,userData:userData,setUserData:this.setUserData,logout:this.logout,enableProbe:true,styleGuideRedirect:true}
    this.state={
      themeStyle:themeStyle,
      theme :theme,
      system:system,
      redirectToLoginPage:false,
      Authenticated:false,
      AuthenticationFailed:false,


    }
    this.handleConnect=this.handleConnect.bind(this);

    this.handleClientAuthorisation=this.handleClientAuthorisation.bind(this);
  }


  handleConnect(){

    //  console.log('soceket connecting');
    let jwt = JSON.parse(localStorage.getItem('jwt'));

    //console.log('jwt',jwt);
    if(jwt){
      let socket=this.state.system.socket;
      socket.emit('AuthoriseClient', jwt);
    }


  }
  handleClientAuthorisation(msg){
    this.state.system.setUserData(msg.username);
    this.setState({'Authorised':msg.successful,'AuthorisationFailed':msg.successful!==true});
    
    

  }
  componentDidMount(){

    let jwt = JSON.parse(localStorage.getItem('jwt'));

    if(jwt){
      this.setState({'redirectToLoginPage':false});
      let socket=this.state.system.socket;
      socket.on('connect',this.handleConnect);
      //socket.on('redirectToLogIn', this.handleRedirectToLogIn);
      socket.on('clientAuthorisation',this.handleClientAuthorisation);


    }



  }
  componentWillUnmount(){
    console.log('unmounted')
    let socket=this.state.system.socket;
    socket.removeListener('connect',this.handleConnect);
    //  socket.removeListener('redirectToLogIn', this.handleRedirectToLogIn);
    socket.removeListener('clientAuthorisation',this.handleClientAuthorisation);
  }
  render() {
    //  console.log('node env',process.env.NODE_ENV)
    //  console.log(this.state.theme)

  //  console.log(this.state)
    return (

      <AutomationStudioContext.Provider value={this.state.system}>
        <MuiThemeProvider theme={this.state.theme}>
          <CssBaseline />
          <Routes limitRoutes={false}>
            {/*<Routes limitRoutes={this.state.AuthenticationFailed}/>*/}


          </Routes>
        </MuiThemeProvider>
      </AutomationStudioContext.Provider>
    );
  }
}


export default App;
