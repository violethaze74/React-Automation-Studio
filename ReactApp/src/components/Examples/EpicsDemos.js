import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import Typography from '@material-ui/core/Typography';
import EpicsBinaryOutDebug from '../GroupedComponents/EpicsBinaryOutDebug';
import EpicsAnalogOutDebug from '../GroupedComponents/EpicsAnalogOutDebug';
import EpicsStringOutDebug from '../GroupedComponents/EpicsStringOutDebug';
import EpicsMbboDebug from '../GroupedComponents/EpicsMbboDebug';

import TextOutput from '../BaseComponents/TextOutput';
import Slider from '../BaseComponents/Slider';
import GraphY from '../BaseComponents/GraphY';
import ArrayContainer from '../CompoundComponents/ArrayContainer';
import Grid from '@material-ui/core/Grid';

import Card from '@material-ui/core/Card';

import MobileDemo2 from './Mobile/MobileDemo2';
import TraditionalLayout from '../UI/Layout/ComposedLayouts/TraditionalLayout.js';

function TabContainer(props) {
  return (
    <Typography component="div" style={{ padding: 8 * 1, paddingTop: 36 }}>
      {props.children}
    </Typography>
  );
}

TabContainer.propTypes = {
  children: PropTypes.node.isRequired,
};

const styles = theme => ({
  root: {
    flexGrow: 1,
    width: '100%',
    backgroundColor: theme.palette.background.paper,
  },
  card: {
    padding: theme.spacing(2),
  },
});



class EpicsDemos extends React.Component {
  state = {
    value: 0,
  };

  handleChange = (event, value) => {
    this.setState({ value });
  };

  render() {
    const { classes } = this.props;
    const { value } = this.state;

    return (


      <div >
        <TraditionalLayout
          title="EPICS PV Demos"
          denseAppBar
          alignTitle="center"
          tabs={['Main', 'Analog PVs', 'Binary PVs', "MBBO/I PVs", "Array PVs", "String PVs"]}
          handleTabChange={this.handleChange}
          tabValue={value}

        />

        {value === 0 &&

          <MobileDemo2 nosidebar />

        }

        {value === 1 && <TabContainer key='TabContainer1'>
          <Grid container spacing={1}>

            <Grid item xs={12} sm={6} lg={3}>
              <Card className={classes.card}>
                <EpicsAnalogOutDebug macros={{ '$(device)': 'testIOC:amplitude' }} />
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} lg={3} >
              <Card className={classes.card}>
                <EpicsAnalogOutDebug macros={{ '$(device)': 'testIOC:test1' }} />
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} lg={3} >
              <Card className={classes.card}>
                <EpicsAnalogOutDebug macros={{ '$(device)': 'testIOC:test2' }} />
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} lg={3} >
              <Card className={classes.card}>
                <EpicsAnalogOutDebug macros={{ '$(device)': 'testIOC:time' }} />
              </Card>
            </Grid>
          </Grid>
        </TabContainer>
        }

        {value === 2 && <TabContainer key='TabContainer2'>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} lg={3}>
              <Card className={classes.card}>
                <EpicsBinaryOutDebug macros={{ '$(device)': 'testIOC:BO1' }} />
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} lg={3} >
              <Card className={classes.card}>
                <EpicsBinaryOutDebug macros={{ '$(device)': 'testIOC:BO2' }} />
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>

            </Grid>
            <Grid item xs={12} sm={6} lg={3}>

            </Grid>

          </Grid>

        </TabContainer>
        }
        {value === 3 && <TabContainer key='TabContainer3'>
          <Grid container spacing={3}>

            <Grid item xs={12} sm={6} lg={3}>
              <Card className={classes.card}>
                <EpicsMbboDebug macros={{ '$(device)': 'testIOC:mbboTest1' }} />
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <Card className={classes.card}>
                <EpicsMbboDebug macros={{ '$(device)': 'testIOC:mbboTest1' }} custom_selection_strings={['text 1', 'text 4']} />
              </Card>
            </Grid>


          </Grid>

        </TabContainer>
        }
        {value === 4 && <TabContainer key='TabContainer4'>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={12} >
              <div style={{ height: '25vh' }}>
                <GraphY pvs={['testIOC:test4', 'testIOC:test5']} legend={['Sine Wave ', 'Amplitude']} />
              </div>

            </Grid>
            <Grid item xs={12} sm={6} >
              <div style={{ height: '25vh' }}>
                <GraphY pvs={['testIOC:test4']} legend={['Sine Wave']} lineColor={[this.props.theme.palette.reactVis.lineColors[1]]} />
              </div>

            </Grid>
            <Grid item xs={12} sm={6}>
              <div style={{ height: '25vh' }}>
                <GraphY pvs={['testIOC:test5']} legend={['Amplitude of Sine Wave Circular Buffer']} lineColor={[this.props.theme.palette.reactVis.lineColors[1]]} />
              </div>

            </Grid>
            <Grid item xs={12} sm={6}>
              <TextOutput pv='$(device):test4' macros={{ '$(device)': 'testIOC' }} label={'Sine Wave Circular Buffer'} />

            </Grid>
            <Grid item xs={12} sm={6} >

              <TextOutput pv='$(device):test5' macros={{ '$(device)': 'testIOC' }} label={'Amplitude of Sine Wave Circular Buffer'} />
            </Grid>
            <Grid item xs={12} sm={6} >
              <ArrayContainer
                label="First 3 samples of Sine Wave Circular Buffer using ArrayContainer"
                registersLabel={["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]}
                spacing={1}
                visibleItemsCount={3}
                maxItemsCount={10}
              >
                <TextOutput pv='$(device):test4' macros={{ '$(device)': 'testIOC' }}/>
              </ArrayContainer>
            </Grid>
            

            <Grid item xs={12} >
              <Slider pv='$(device):amplitude' macros={{ '$(device)': 'testIOC' }} usePvMinMax={true} min={1000} max={500} usePvLabel={true} />
            </Grid>
            <Grid item xs={6} >

            </Grid>
          </Grid>

        </TabContainer>
        }
        {value === 5 && <TabContainer key='TabContainer5'>

          <Grid container spacing={3}>

            <Grid item xs={12} sm={6} lg={3}>
              <Card className={classes.card}>

                <EpicsStringOutDebug macros={{ '$(device)': 'testIOC:stringtest1' }} />
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <Card className={classes.card}>

                <EpicsStringOutDebug macros={{ '$(device)': 'testIOC:stringtest2' }} />
              </Card>
            </Grid>
          </Grid>

        </TabContainer>
        }







      </div>
    );
  }
}

EpicsDemos.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles, { withTheme: true })(EpicsDemos);
