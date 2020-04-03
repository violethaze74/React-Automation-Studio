import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import EpicsBinaryOutDebug from '../GroupedComponents/EpicsBinaryOutDebug';
import EpicsAnalogOutDebug from '../GroupedComponents/EpicsAnalogOutDebug';
import EpicsMbboDebug from '../GroupedComponents/EpicsMbboDebug';
import TextUpdate from '../BaseComponents/TextUpdate';
import TextInput from '../BaseComponents/TextInput';
import TextOutput from '../BaseComponents/TextOutput';
import SimpleSlider from '../BaseComponents/SimpleSlider';


import Grid from '@material-ui/core/Grid';
import EpicsPV from '../SystemComponents/EpicsPV';

import SwitchComponent from '../BaseComponents/SwitchComponent';
import SelectionInput from '../BaseComponents/SelectionInput';
import HarpRangeSelection from '../SiteSpecificComponents/iThembaLABS/CompoundComponents/HarpRangeSelection';
import ToggleButton from '../BaseComponents/ToggleButton';
import ActionButton from '../BaseComponents/ActionButton';
import ActionFanoutButton from '../BaseComponents/ActionFanoutButton';
import ThumbWheel from '../BaseComponents/ThumbWheel';

import ControlRightEx1 from '../ControlScreens/GridComponents/ControlRightEx1'
import ControlRightSteererXY from '../ControlScreens/GridComponents/ControlRightSteererXY'
import ControlRightSlitXY from '../ControlScreens/GridComponents/ControlRightSlitXY'
import ControlRightSinglePS from '../ControlScreens/GridComponents/ControlRightSinglePS'


import ControlTopHarpEx1 from '../ControlScreens/GridComponents/ControlTopHarpEx1'

import ControlBottomHarp1 from '../ControlScreens/GridComponents/ControlBottomHarp1'
import HarpGraph from '../SiteSpecificComponents/iThembaLABS/CompoundComponents/HarpGraph';
//import SideBar from './sidebar/SideBar';
//import Settings from './settings/Settings';
import AppBar from '@material-ui/core/AppBar';

import MoreVertRoundedIcon from '@material-ui/icons/MoreVertRounded';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import LoadSave from '../loadSaveComponent/LoadSave';


const systemName='testIOC';




const styles = theme => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing(2)
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
});

const VerticalTabs = withStyles(theme => ({
  flexContainer: {
    flexDirection: 'column'
  },
  indicator: {
    display: 'none',
  }
}))(Tabs)

function TabContainer(props) {
  return (
    <Typography component="div" style={{ padding: 8 * 0 }}>
      {props.children}
    </Typography>
  );
}

class LoadSaveExample extends React.Component {
  constructor(props) {
    super(props);
    let device='testIOC';
    this.state={'editorType':'PS',
    'displayEditor':false,
    'editorMacros':{'$(device)':""},
    'editorSystem':{},
    device:device,
    topTabValue:0,
    sideTabValue:0,
    displaySettings:false,



  }
  this.handlePsOnClick= this.handlePsOnClick.bind(this);
  this.handleOnSystemClick= this.handleOnSystemClick.bind(this);
  this.handhandleRFSystemsClickel=this.handleRFSystemsClick.bind(this);

}

handlePsOnClick(name){

  //  console.log("in control test1 clicked "+name.toString());
  this.setState({['editorType']:'PS',
  ['displayEditor']:true,
  ['editorMacros']:{'$(device)':name}});

  //  this.setState({ ['clicked']: 1});
}
handleOnSystemClick=(system)=>{
  console.log(system)
  this.setState({['editorType']:system.editorType,
  ['displayEditor']:true,
  ['editorSystem']:system,
  ['editorMacros']:{'$(device)':""}});
  //  console.log("in control test1 clicked "+name.toString());
  //    this.setState({['editorType']:'PS',
  //    ['displayEditor']:true,
  //    ['editorMacros']:{'$(device)':name}});

  //  this.setState({ ['clicked']: 1});
}

handleRFSystemsClick=(system,event)=>{
  console.log(system)
  this.setState({device:system})
}
handleSideTabChange = (event, value) => {
  this.setState({ sideTabValue:value,displayEditor:false });
};
handleCloseEditor=()=>{
  this.setState({
    ['displayEditor']:false,}
  );

  //  this.setState({ ['clicked']: 1});
}

render() {
  //      console.log("state: ",this.state);
  //console.log('displayHarps',this.state.displayHarps)

  const { classes } = this.props;
  const topTabValue  = this.state.topTabValue;
  const sideTabValue  = this.state.sideTabValue;
  return (
<React.Fragment>
  <AppBar style={{position:'sticky'}} color='inherit' >

    <Toolbar>
      {/* <SideBar handleRFSystemsClick ={this.handleRFSystemsClick}/> */}


      <h3 >{this.state.device}</h3>
      <Tabs  aria-label="simple tabs example" value={sideTabValue} onChange={this.handleSideTabChange}>
        
        <Tab label="Load/Save" />
        
      </Tabs>
      <div style={{
        flexGrow: 1
      }}></div>


        {/* <Settings handleRFSystemsClick ={this.handleRFSystemsClick}/> */}

    </Toolbar>
  </AppBar>
  <div style={{"overflowX": "hidden",'overflowY':'hidden'}}>
    <Grid
      style={{marginTop:0,padding:8}}
      container
      direction="row"
      justify="flex-start"
      alignItems="flex-start"
      spacing={0}
    >



      <Grid item xs={12} sm={12} md={12} lg={12} >
      
        {sideTabValue==0&&<LoadSave key={" "+this.state.device} macros={{'$(device)':this.state.device}}/>}
       
      </Grid>
      {/* <Grid item xs={12} sm={4} md={4} lg={3}>
        {((this.state['displayEditor']===true) &&(this.state['editorMacros']['$(device)']==='testIOC:PS1'))&&<ControlRightEx1 macros={this.state['editorMacros']} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorMacros']['$(device)']==='testIOC:PS2'))&&<ControlRightEx1 macros={this.state['editorMacros']} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorMacros']['$(device)']==='testIOC:PS3'))&&<ControlRightEx1 macros={this.state['editorMacros']}  handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorMacros']['$(device)']==='testIOC:PS4'))&&<ControlRightEx1 macros={this.state['editorMacros']} handleCloseEditor={this.handleCloseEditor} />}
        {((this.state['displayEditor']===true) &&(this.state['editorMacros']['$(device)']==='testIOC:STR1:X'))&&<ControlRightEx1 macros={this.state['editorMacros']}  handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='EditorIntegerRF'))&&<EditorIntegerRF  key={'editor-key'+this.state.editorSystem.systemName+this.state.editorSystem.displayName} system={this.state.editorSystem} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='EditorRFLevel'))&&<EditorRFLevel  key={'editor-key'+this.state.editorSystem.systemName+this.state.editorSystem.displayName} system={this.state.editorSystem} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='EditorRFButton'))&&<EditorRFButton  key={'editor-key'+this.state.editorSystem.systemName+this.state.editorSystem.displayName} system={this.state.editorSystem} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='EditorRFPhase'))&&<EditorRFPhase  key={'editor-key'+this.state.editorSystem.systemName+this.state.editorSystem.displayName} system={this.state.editorSystem} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='EditorRFGraph'))&&<EditorRFGraph  key={'editor-key'+this.state.editorSystem.systemName+this.state.editorSystem.displayName} system={this.state.editorSystem} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='steererXY'))&&<ControlRightSteererXY key={'editor-key'+this.state.editorSystem.systemName} system={this.state.editorSystem}  handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='singlePS'))&&<ControlRightSinglePS key={'editor-key'+this.state.editorSystem.systemName} system={this.state.editorSystem} handleCloseEditor={this.handleCloseEditor}/>}
        {((this.state['displayEditor']===true) &&(this.state['editorType']==='slitxy'))&&<ControlRightSlitXY key={'editor-key'+this.state.editorSystem.systemName} system={this.state.editorSystem} handleCloseEditor={this.handleCloseEditor}/>}
      </Grid> */}
    </Grid>




  </div>
</React.Fragment>




  );
}
}

LoadSaveExample.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(LoadSaveExample);
//export default LoadSaveExample;
