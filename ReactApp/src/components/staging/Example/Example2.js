import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import EpicsBinaryOutDebug from '../../../components/GroupedComponents/EpicsBinaryOutDebug';
import EpicsAnalogOutDebug from '../../../components/GroupedComponents/EpicsAnalogOutDebug';
import EpicsMbboDebug from '../../../components/GroupedComponents/EpicsMbboDebug';
import TextUpdate from '../../../components/BaseComponents/TextUpdate';
import TextInput from '../../../components/BaseComponents/TextInput';
import TextOutput from '../../../components/BaseComponents/TextOutput';
import Meter from '../../../components/BaseComponents/Gauge';
import SimpleSlider from '../../../components/BaseComponents/SimpleSlider';
import GraphY from '../../../components/BaseComponents/GraphY';
import SelectionList from '../../../components/BaseComponents/SelectionList';
import StyledIconIndicator from '../../../components/BaseComponents/StyledIconIndicator';
import Grid from '@material-ui/core/Grid';
import DataConnection from '../../../components/SystemComponents/DataConnection';
import SwitchComponent from '../../../components/BaseComponents/SwitchComponent';
import SelectionInput from '../../../components/BaseComponents/SelectionInput';
import ToggleButton from '../../../components/BaseComponents/ToggleButton';
import ActionButton from '../../../components/BaseComponents/ActionButton';
import ThumbWheel from '../../../components/BaseComponents/ThumbWheel';
import Card from '@material-ui/core/Card';
import SideBar from '../../../components/SystemComponents/SideBar';
import AppBar from '@material-ui/core/AppBar';
import lime from '@material-ui/core/colors/lime';
const styles = theme => ({
  root: {
    padding: 0,
    spacing: 0,
    direction: 'row',
    alignItems: 'stretch',
    justify: "flex-start",
    overflowX: "hidden",
    overflowY: "hidden",
  },

});
class Example2 extends React.Component {


  render() {
    //  console.log("state: ",this.state);

    return (
      <React.Fragment>
        <SideBar />
        <div >
          <Grid
            style={{ padding: 8 }}
            container item
            direction="row"
            justify="center"
            spacing={1}
            alignItems="stretch"
          >
            <Grid item xs={6}  >
              <StyledIconIndicator
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'homepc',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bLight',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bLight'
                onColor='primary'
                offColor='default'
                labelPlacement={'end'}
              //useStringValue={true}

              />
            </Grid>
            <Grid item xs={6}  >
              <ToggleButton
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'homepc',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bLightON',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bLightON'
                
                custom_selection_strings={["OFF", "ON"]}
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <ToggleButton
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'homepc',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bLightON',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bLightON'
                
                custom_selection_strings={["OFF", "ON"]}
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <TextInput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bSweeperEn0',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bSweeperEn0'
                //useStringValue={true}
                debug={false}
              />
            </Grid>

            <Grid item xs={6}  >
              <TextInput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bTestBool1',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bTestBool1'
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <ToggleButton
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bSweeperEn0',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bSweeperEn0'
                custom_selection_strings={["OFF", "ON"]}
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <StyledIconIndicator
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bTestBool1',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bTestBool1'
                onColor='primary'
                offColor='default'
                labelPlacement={'end'}
              //useStringValue={true}

              />
            </Grid>
            <Grid item xs={6}  >
              <ToggleButton
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bTestBool1',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bTestBool1'
                onColor='primary'
                offColor='default'

                custom_selection_strings={["OFF", "ON"]}
              //useStringValue={true}

              />
            </Grid>
            <Grid item xs={6}  >
              <StyledIconIndicator
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bTestBool1',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bTestBool1'
                onColor='primary'
                offColor='default'
                labelPlacement={'end'}
              //useStringValue={true}

              />
            </Grid>

            <Grid item xs={6}  >
              <StyledIconIndicator
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bTest1',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bTest1'
                onColor='primary'
                offColor='default'
                labelPlacement={'end'}
              //useStringValue={true}

              />
            </Grid>
            <Grid item xs={6}  >
              <StyledIconIndicator
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bTest1',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bTest1'
                onColor='primary'
                offColor='default'
                labelPlacement={'end'}
              //useStringValue={true}

              />
            </Grid>
            <Grid item xs={6}  >
              <StyledIconIndicator
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.bTest1',
                  '$(PLC_TYPE)': "BOOL"

                }}
                label='GVL001.bTest1'
                onColor='primary'
                offColor='default'
                labelPlacement={'end'}
              //useStringValue={true}

              />
            </Grid>

            <Grid item xs={6}  >
              <TextInput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.iTestInt1',
                  '$(PLC_TYPE)': "INT"

                }}
                label='GVL001.iTestInt1'
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <TextInput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.iTestLint1',
                  '$(PLC_TYPE)': "LINT"

                }}
                label='GVL001.iTestLint1'
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <TextInput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.amplitude',
                  '$(PLC_TYPE)': "INT"

                }}
                label='GVL001.amplitude'
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <TextOutput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)[$(ARRAY_SIZE)]'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.sin0',
                  '$(PLC_TYPE)': "INT",
                  '$(ARRAY_SIZE)': "100"

                }}
                label='GVL001.sin0'
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <SimpleSlider
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.amplitude',
                  '$(PLC_TYPE)': "INT"

                }}
                label='GVL001.amplitude'
                min={0}
                max={32767}
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6} >
              <div style={{ height: '25vh', width: '100%', }}>
                <
                  GraphY
                  pvs={['ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)[$(ARRAY_SIZE)]', 'ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV2):$(PLC_TYPE)[$(ARRAY_SIZE)]']}
                  macros={{
                    '$(PLC_ID)': 'ipcsweeperdev1',
                    '$(PLC_PORT)': '851',
                    '$(PLC_PV)': 'GVL001.sin0',
                    '$(PLC_PV2)': 'GVL001.cos0',
                    '$(PLC_TYPE)': "INT",
                    '$(ARRAY_SIZE)': "100"

                  }}
                  legend={['GVL001.sin0']}
                  ymin={-32767}
                  ymax={32767}
                  lineColor={[this.props.theme.palette.secondary.main, lime['400']]}
                />
              </div>
            </Grid>
            <Grid item xs={6} >
              <div style={{ height: '25vh', width: '100%', }}>
                <
                  GraphY
                  pvs={['ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)[$(ARRAY_SIZE)]', 'ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV2):$(PLC_TYPE)[$(ARRAY_SIZE)]']}
                  macros={{
                    '$(PLC_ID)': 'ipcsweeperdev1',
                    '$(PLC_PORT)': '851',
                    '$(PLC_PV)': 'GVL001.adc0',
                    '$(PLC_PV2)': 'GVL001.adc1',
                    '$(PLC_TYPE)': "INT",
                    '$(ARRAY_SIZE)': "100"

                  }}
                  legend={['GVL001.adc0', 'GVL001.adc1']}
                  ymin={-32767}
                  ymax={32767}
                  lineColor={[this.props.theme.palette.secondary.main, lime['400']]}
                />
              </div>
            </Grid>
            <Grid item xs={6} >
              <div style={{ height: '25vh', width: '100%', }}>
                <
                  GraphY
                  pvs={['ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)[$(ARRAY_SIZE)]', 'ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV2):$(PLC_TYPE)[$(ARRAY_SIZE)]']}
                  macros={{
                    '$(PLC_ID)': 'ipcsweeperdev1',
                    '$(PLC_PORT)': '851',
                    '$(PLC_PV)': 'GVL001.adc0',
                    '$(PLC_PV2)': 'GVL001.adc1',
                    '$(PLC_TYPE)': "INT",
                    '$(ARRAY_SIZE)': "100"

                  }}
                  legend={['GVL001.adc0', 'GVL001.adc1']}

                  lineColor={[this.props.theme.palette.secondary.main, lime['400']]}
                />
              </div>
            </Grid>
            <Grid item xs={6}  >
              <TextInput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.iTestReal1',
                  '$(PLC_TYPE)': "REAL"

                }}
                label='GVL001.iTestReal1'
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}  >
              <TextInput
                pv='ads://$(PLC_ID):$(PLC_PORT):$(PLC_PV):$(PLC_TYPE)'
                macros={{
                  '$(PLC_ID)': 'ipcsweeperdev1',
                  '$(PLC_PORT)': '851',
                  '$(PLC_PV)': 'GVL001.iTestLreal1',
                  '$(PLC_TYPE)': "LREAL"

                }}
                label='GVL001.iTestLreal1'
                //useStringValue={true}
                debug={false}
              />
            </Grid>
            <Grid item xs={6}>
              <TextOutput
                pv='pva://$(device):test3'
                macros={{ '$(device)': 'testIOC' }}
                usePvLabel={true} usePrecision={true}
                prec={3} alarmSensitive={true}
              />
            </Grid>
            <Grid item xs={3}  >
              <TextInput
                pv='pva://$(device):amplitude'
                macros={{ '$(device)': 'testIOC' }}
                usePvLabel={true}
                usePrecision={true}
                prec={3}
                alarmSensitive={true}
              />
            </Grid>
            <Grid item xs={3}>
              <TextOutput
                pv='pva://$(device):test3'
                macros={{ '$(device)': 'testIOC' }}
                usePvLabel={true} usePrecision={true}
                prec={3} alarmSensitive={true}
              />
            </Grid>

            <Grid item xs={3}  >
              <TextInput
                pv='pva://$(device):amplitude'
                macros={{ '$(device)': 'testIOC' }}
                usePvLabel={true}
                usePrecision={true}
                prec={3}
                alarmSensitive={true}
              />
            </Grid>
            <Grid item xs={3}>
              <TextOutput
                pv='pva://$(device):test3'
                macros={{ '$(device)': 'testIOC' }}
                usePvLabel={true} usePrecision={true}
                prec={3} alarmSensitive={true}
              />
            </Grid>



            <Grid item xs={12} >
              <div style={{ height: '50vh', width: '96vw', }}>
                <GraphY pvs={['pva://testIOC:test4', 'pva://testIOC:test5']} legend={['Sine Wave', 'Amplitude']} lineColor={[this.props.theme.palette.secondary.main, lime['400']]} />
              </div>
            </Grid>
            <Grid item xs={12}  >
              <SimpleSlider
                pv='pva://$(device):amplitude'
                macros={{ '$(device)': 'testIOC' }}
                usePvMinMax={true}
                min={1000}
                max={500}
                usePvLabel={true}
              />
            </Grid>
          </Grid>
        </div>
      </React.Fragment>
    );
  }
}

Example2.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles, { withTheme: true })(Example2);
