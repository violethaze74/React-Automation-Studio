//This example is deprecated and will be removed in a future release 
import React from 'react'

import AutomationStudioContext from '../../SystemComponents/AutomationStudioContext';
import TextInput from '../../BaseComponents/TextInput';

import TextOutput from '../../BaseComponents/TextOutput';
import Slider from '../../BaseComponents/Slider';

import Grid from '@material-ui/core/Grid';

import ToggleButton from '../../BaseComponents/ToggleButton';

import Card from '@material-ui/core/Card';

import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import { Link } from 'react-router-dom'

import ThumbWheel from '../../BaseComponents/ThumbWheel';
import Close from '@material-ui/icons/Close';
//import MenuItem from '@material-ui/core/MenuItem';
console.warn("This example is deprecated and will be removed in a future release")
const styles = theme => ({
  body1: theme.typography.body1,


});

class ControlRightSteererXY extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 'showSettings': false }

  }


  handleSettingsButtonClick = () => {
    this.setState({ 'showSettings': true });
  }

  render() {
    const system = this.props.system;
    //    console.log("json stringify",JSON.stringify(system))
    const { classes } = this.props;

    return (

      <div className={classes.body1} style={{ paddingRight: 12 }}>


        {/*<TextUpdate  pv='$(device):Setpoint.NAME' macros={this.props['macros']}  />*/}
        <Grid style={{ paddingLeft: 12, paddingRight: 24, }} container spacing={2}>
          <Grid item xs={11}>

            {system.displayName + ": X-Steerer"}

          </Grid>
          <Grid item xs={1}>


            <Close fontSize="small" onClick={this.props.handleCloseEditor} />

          </Grid>
        </Grid>

        <Card style={{ padding: 12 }} >



          <Grid container
            direction="row"
            justify="flex-start"
            alignItems="center" spacing={1}>
            <Grid item xs={6}  >
              <TextInput pv={ system.devices.xDevice.deviceName + ":" + system.devices.xDevice.setpoint} prec={3} label={'X Setpoint:'} alarmSensitive={true} usePvUnits={true} usePvMinMax={true} />

            </Grid>
            <Grid item xs={6}  >
              <TextOutput style={{ marginRight: 10 }} pv={ system.devices.xDevice.deviceName + ":" + system.devices.xDevice.readback} prec={3} usePvUnits={true} alarmSensitive={true} label={'X Readback'} />


            </Grid>

            <Grid item xs={12}  >

              <Slider pv={ system.devices.xDevice.deviceName + ":" + system.devices.xDevice.setpoint} prec={3} label={'X Setpoint:'} alarmSensitive={true} usePvUnits={true} usePvMinMax={true} />
            </Grid>
            <Grid item xs={6}  >

            </Grid>
            <Grid item xs={12}  >

            </Grid>






            <Grid item xs={12}  >
              <Grid container justify="flex-start" direction="row" alignItems="center" spacing={1}>
                <Grid item xs={12} sm={12} >
                  <ThumbWheel
                    pv={ system.devices.xDevice.deviceName + ":" + system.devices.xDevice.setpoint}
                    macros={this.props['macros']}
                    prec_integer={2}
                    prec_decimal={2}
                  />

                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={4}  >
              <ToggleButton pv={ system.devices.xDevice.deviceName + ':On'} macros={this.props['macros']} labelPlacement={"top"} />





            </Grid>
            <Grid item xs={4}  >





            </Grid>
            <Grid item xs={4}  >

              <Button component={Link} to={{
                pathname: "/SettingsSteererXY",
                search: JSON.stringify(system),
                state: ["sdas"],
                data: "hello2"
              }} target="_blank" color="primary" style={{ width: "100%" }} variant='contained'>  Settings </Button>

            </Grid>


          </Grid>

        </Card>
        <div className={classes.body1} style={{ marginTop: 12 }}>

          {system.displayName + ": Y-Steerer"}
          {/*<TextUpdate  pv='$(device):Setpoint.NAME' macros={this.props['macros']}  />*/}

          <Card style={{ padding: 12 }} >



            <Grid container
              direction="row"
              justify="flex-start"
              alignItems="center" spacing={1}>
              <Grid item xs={6}  >
                <TextInput pv={ system.devices.yDevice.deviceName + ":" + system.devices.yDevice.setpoint} prec={3} label={'Y Setpoint:'} alarmSensitive={true} usePvUnits={true} usePvMinMax={true} />

              </Grid>
              <Grid item xs={6}  >
                <TextOutput style={{ marginRight: 10 }} pv={ system.devices.yDevice.deviceName + ":" + system.devices.yDevice.readback} prec={3} usePvUnits={true} alarmSensitive={true} label={'Y Readback'} />


              </Grid>

              <Grid item xs={12}  >

                <Slider pv={ system.devices.yDevice.deviceName + ":" + system.devices.yDevice.setpoint} prec={3} label={'X Setpoint:'} alarmSensitive={true} usePvUnits={true} usePvMinMax={true} />
              </Grid>
              <Grid item xs={6}  >

              </Grid>
              <Grid item xs={12}  >

              </Grid>






              <Grid item xs={12}  >
                <Grid container justify="flex-start" direction="row" alignItems="center" spacing={1}>
                  <Grid item xs={12} sm={12} >
                    <ThumbWheel
                      pv={ system.devices.yDevice.deviceName + ":" + system.devices.yDevice.setpoint}
                      macros={this.props['macros']}
                      prec_integer={2}
                      prec_decimal={2}
                    />

                  </Grid>
                </Grid>
              </Grid>
              <Grid item xs={4}  >
                <ToggleButton pv={ system.devices.yDevice.deviceName + ':On'} macros={this.props['macros']} labelPlacement={"top"} />





              </Grid>
              <Grid item xs={4}  >





              </Grid>
              <Grid item xs={4}  >

                <Button component={Link} to={{
                  pathname: "/SettingsSteererXY",
                  search: JSON.stringify(system),
                  state: ["sdas"],
                  data: "hello2"
                }} target="_blank" color="primary" style={{ width: "100%" }} variant='contained'>  Settings </Button>

              </Grid>


            </Grid>

          </Card>
        </div>

      </div>


    );
  }
}

ControlRightSteererXY.contextType = AutomationStudioContext;
export default withStyles(styles, { withTheme: true })(ControlRightSteererXY)
