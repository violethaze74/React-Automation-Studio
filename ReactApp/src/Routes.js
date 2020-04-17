import React, { Component } from 'react';
import ReactDOM from 'react-dom';

import { Route, BrowserRouter, Switch } from 'react-router-dom'
import App from './App';
//import * as serviceWorker from './serviceWorker';
import EpicsDemos from './components/Examples/EpicsDemos';
import Help from './components/docs/Help';
import MobileDemo2 from './components/Examples/Mobile/MobileDemo2';
import MobileDemo1 from './components/Examples/Mobile/MobileDemo1';

import Main from './Main';
import ControlTestHarp1 from './components/ControlScreens/ControlTestHarp1';

import AlarmHandler from './components/AlarmHandler/AlarmHandler';

import ControlTableExample from './components/ControlScreens/ControlTableExample';
import ComponentsWithMultiplePVs from './components/Examples/ComponentsWithMultiplePVs';
import Staging from './components/staging/Staging';
import Example from './components/staging/Example/Example';
import Example1 from './components/staging/Example/Example1';
import Example2 from './components/staging/Example/Example2';
import Example3 from './components/staging/Example/Example3';
import Test3D from './components/Experimental/Test3D';
import Probe from './components/SettingsPages/Probe';
import SettingsSteererXY from './components/SettingsPages/SettingsSteererXY';
import SettingsSinglePS from './components/SettingsPages/SettingsSinglePS';
import LoadSaveExample from './components/Examples/LoadSaveExample.js';
import Administrator from './components/Administrator/Administrator.js';
import UserProfile from './components/SystemComponents/UserProfile';
import AutomationStudioContext from './components/SystemComponents/AutomationStudioContext';
import LogIn from './LogIn';
import { Redirect } from 'react-router-dom'

class Routes extends Component {
  constructor(props) {
    super(props);
    this.state={};
  }
render(){
  return(
  <BrowserRouter >

    <Switch>

      <Route exact path="/" component={Main} />


      {process.env.REACT_APP_EnableLogin === 'true' &&
        <Route exact path="/LogIn" component={LogIn} />
      }
      <Route path="/SettingsSinglePS" component={SettingsSinglePS} />
      <Route path="/SettingsSteererXY" component={SettingsSteererXY} />
      <Route path="/Probe" component={Probe} />

      <Route path="/MobileDemo2" component={MobileDemo2} />
      <Route path="/MobileDemo1" component={MobileDemo1} />

      <Route path="/ControlTestHarp1" component={ControlTestHarp1} />

      <Route path="/ControlTableExample" component={ControlTableExample} />
      <Route path="/LoadSaveExample" component={LoadSaveExample} />
      
      <Route exact path="/Administrator" >
              {process.env.REACT_APP_IncludeAdministrator && this.context.userData.roles.includes('admin') ?<Administrator/>:<Redirect to="/"/> }
      </Route>
      <Route path="/UserProfile" component={UserProfile} />
      <Route path="/EpicsDemos" component={EpicsDemos} />
      <Route path="/Help" component={Help} />
      <Route path="/Staging" component={Staging} />

      <Route path="/Test3D" component={Test3D} />
      <Route path="/ComponentsWithMultiplePVs" component={ComponentsWithMultiplePVs} />
      <Route path="/Example" component={Example} />
      <Route path="/Example1" component={Example1} />
      <Route path="/Example2" component={Example2} />
      <Route path="/Example3" component={Example3} />

      <Route path="/AlarmHandlerDemo" component={AlarmHandler} />






    </Switch>

  </BrowserRouter>
)
    }
  };
  Routes.contextType = AutomationStudioContext;
  export default Routes;