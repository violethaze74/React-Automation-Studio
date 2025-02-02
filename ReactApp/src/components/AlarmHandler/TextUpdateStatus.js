import React from "react";
import { withStyles } from "@material-ui/core/styles";
import { fade } from '@material-ui/core/styles/colorManipulator';
import Widget from "../SystemComponents/Widgets/Widget";
import grey from '@material-ui/core/colors/grey';
import { Typography } from '@material-ui/core';
import PropTypes from 'prop-types';
const styles = (theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
  },
  TextFieldSeverity0: {
    borderRadius: 2,
    borderWidth: 1,
    padding: 1,
    borderStyle: 'solid',
    borderColor: 'rgba(0,0,0,0)',

  },
  TextFieldSeverity1: {
    borderColor: theme.palette.type === 'dark' ? grey[700] : grey[300],
    borderRadius: 2,
    borderWidth: 1,
    borderStyle: 'solid',

    padding: 1,
    //background:theme.palette.alarm.minor.main,
    background: 'linear-gradient(45deg,' + fade(theme.palette.alarm.minor.dark, theme.palette.type === 'dark' ? 0.2 : 0.1) + ' 0%, ' + (theme.palette.alarm.minor.dark) + ' 100%)'
    //  background:'linear-gradient(45deg, '+ theme.palette.background.default+ ' 1%, '+deepOrange['400'] +' 99%)'
  },
  TextFieldSeverity2: {
    borderColor: theme.palette.type === 'dark' ? grey[700] : grey[300],
    borderWidth: 1,
    borderStyle: 'solid',
    borderRadius: 2,

    padding: 1,
    //background:theme.palette.alarm.major.main,
    background: 'linear-gradient(45deg,' + fade(theme.palette.alarm.major.dark, theme.palette.type === 'dark' ? 0.2 : 0.1) + ' 0%, ' + (theme.palette.alarm.major.dark) + ' 100%)'
    //  backgroundColor:'linear-gradient(45deg, #FFFFFF 1%, #FF8E53 99%)'
    //  background:'linear-gradient(45deg, '+ theme.palette.background.default+ ' 1%, '+red['800'] +' 99%)'
  },
  majorAlarm: props => ({
    borderColor: theme.palette.type === 'dark' ? grey[700] : grey[300],
    borderWidth: 1,
    borderStyle: 'solid',
    background: props.fadeTU
      ? 'linear-gradient(45deg,' + fade(theme.palette.alarm.major.dark, theme.palette.type === 'dark' ? 0.2 : 0.1) + ' 0%, ' + (theme.palette.alarm.major.dark) + ' 100%)'
      : theme.palette.alarm.major.main,
    borderRadius: 2,
    padding: 1,
    paddingRight: 5,
    paddingLeft: 5,
    //fontWeight: 500,
  }),
  majorAlarmAcked: props => ({
    borderColor: theme.palette.type === 'dark' ? grey[700] : grey[300],
    borderWidth: 1,
    borderStyle: 'solid',
    background: props.fadeTU
      ? 'linear-gradient(45deg,' + fade(theme.palette.alarm.majorAcked.dark, theme.palette.type === 'dark' ? 0.2 : 0.1) + ' 0%, ' + (theme.palette.alarm.majorAcked.dark) + ' 100%)'
      : theme.palette.alarm.majorAcked.main,
    borderRadius: 2,
    padding: 1,
    paddingRight: 5,
    paddingLeft: 5,
    //fontWeight: 500,
  }),
  minorAlarm: props => ({
    borderColor: theme.palette.type === 'dark' ? grey[700] : grey[300],
    borderWidth: 1,
    borderStyle: 'solid',
    background: props.fadeTU
      ? 'linear-gradient(45deg,' + fade(theme.palette.alarm.minor.dark, theme.palette.type === 'dark' ? 0.2 : 0.1) + ' 0%, ' + (theme.palette.alarm.minor.dark) + ' 100%)'
      : theme.palette.alarm.minor.main,
    borderRadius: 2,
    padding: 1,
    paddingRight: 5,
    paddingLeft: 5,
    //fontWeight: 500,
  }),
  minorAlarmAcked: props => ({
    borderColor: theme.palette.type === 'dark' ? grey[700] : grey[300],
    borderWidth: 1,
    borderStyle: 'solid',
    background: props.fadeTU
      ? 'linear-gradient(45deg,' + fade(theme.palette.alarm.minorAcked.dark, theme.palette.type === 'dark' ? 0.2 : 0.1) + ' 0%, ' + (theme.palette.alarm.minorAcked.dark) + ' 100%)'
      : theme.palette.alarm.minorAcked.main,
    borderRadius: 2,
    padding: 1,
    paddingRight: 5,
    paddingLeft: 5,
    //fontWeight: 500,
  }),
  noAlarm: {
    borderRadius: 2,
    padding: 1,
    borderColor: grey[50],
    background: 'transparent',
    paddingRight: 5,
    paddingLeft: 5,
    //fontWeight: 500,
  },
});


const TextUpdateComponent = (props) => {
  const { classes } = props;
  let textFieldClassName;
  let label = props.label !== undefined ? props.label + ": " : "";
  let units = props.units !== undefined ? props.units + " " : "";
  let content;
  if (props.initialized) {
    if (props.alarmSensitive === true) {
      if (props.value === "NO_ALARM") {
        textFieldClassName = classes.noAlarm;
      }
      else if (props.value === "MINOR_ACKED") {
        textFieldClassName = classes.minorAlarmAcked;
      }
      else if (props.value === "MINOR_ALARM") {
        textFieldClassName = classes.minorAlarm;
      }
      else if (props.value === "MAJOR_ACKED" || props.value === "INVALID_ACKED" || props.value === "DISCONN_ACKED") {
        textFieldClassName = classes.majorAlarmAcked;
      }
      else if (props.value === "MAJOR_ALARM" || props.value === "INVALID" || props.value === "DISCONNECTED") {
        textFieldClassName = classes.majorAlarm;
      }
    }

    content = (
      <Typography variant={props.variant} className={textFieldClassName} >{label + props.value + " " + units}</Typography>
    );
  } else {
    content = props.formControlLabel;
  }
  return <div>{content}</div>;
}
const TextUpdateStatus = (props) => {
  return (
    <Widget {...props} component={TextUpdateComponent} />
  )
}

TextUpdateStatus.propTypes = {
  /**
  * Directive to use the  alarm severity status to alter the fields background color.
  */

 alarmSensitive: PropTypes.bool,
 /**
  * Custom PV to define the alarm severity to be used, alarmSensitive must be set to `true` and useMetadata to `false`, eg. '$(device):test$(id)'.
  */
 alarmPv: PropTypes.string,
 /**
  * If defined, then the DataConnection and
  * the widget debugging information will be displayed.
  */
 debug: PropTypes.bool,

 /**
  * Local variable initialization value.
  * When using loc:// type PVs.
  */
 initialLocalVariableValue: PropTypes.string,
 /**
  * Custom label to be used, if  usePvLabel is not defined.
  */
 label: PropTypes.string,
 /**
 * Custom PV to define the units to be used, usePvLabel must be set to `true` and useMetadata to `false`, eg. '$(device):test$(id)'.
 */
 labelPv: PropTypes.string,
 /**
  * Values of macros that will be substituted in the pv name.
  * eg. {{'$(device)':'testIOC','$(id)':'2'}}
  */
 macros: PropTypes.object,

 
 /**
  * Custom precision to round the value.
  */
 prec: PropTypes.number,
 /**
  * Custom PV to define the precision to be used, usePvPrecision must be set to `true` and useMetadata to `false`, eg. '$(device):test$(id)'.
  */
 precPv: PropTypes.string,


 
 /**
  * Custom units to be used, if usePvUnits is not defined.
  */

 units: PropTypes.string,
 /**
  * Custom PV to define the units to be used, usePvUnits must be set to `true` and useMetadata to `false`, eg. '$(device):test$(id)'.
  */
 unitsPv: PropTypes.string,
 /**
  * Directive to fill the component's label with
  * the value contained in the  pv metadata's DESC field or the labelPv value.
  * If not defined it uses the custom label as defined by the label prop.
  */
 usePvLabel: PropTypes.bool,
 /**
  * When using EPICS, the RAS pv's metadata is conventionally derived from the pyEpics PV in the pvserver. 
  * The pyEpics metadata is unfortunately static and the values used will be the intial values that pvserver receives when it connects the first time. 
  * This is sufficient in most cases except when the user wants to dynamically update the metaData.
  * In this case a direct connection can be made to all the pv fields by setting useMetadata to false. 
  * If any of the metadata pvs are defined i.e unitsPv then the PV makes a new data  connection to this alternate pv and will
  * use the value provided by this pv as the units. 
  * The same is the case for the precPV, labelPv, alarmPv, unitsPv and minPv.
  * By setting useMetadata to false also enables connection to other variables as defined by different protocols.
  */
 useMetadata: PropTypes.bool,
 
 /**
  * Directive to round the value using the precision field of the PV metadata or precPv.
  * If not defined it uses the custom precision as defined by the prec prop.
  */
 usePvPrecision: PropTypes.bool,
 /**
  * Directive to use the units contained in the   pv metdata's EGU field or unitsPv.
  *  If not defined it uses the custom units as defined by the units prop.
  */


 usePvUnits: PropTypes.bool,
 /**
  * Directive to use PV's string values.
  */
 useStringValue: PropTypes.bool,



 

 
 /** Name of the process variable,  eg. '$(device):test$(id)'*/
 pv: PropTypes.string,
 /** Array of the process variables, eg. '$(device):test$(id)'*/
 pvs: PropTypes.arrayOf(PropTypes.string),
 /**
  * Object with a string and the corresponding severity value.
  * When PV value is equal to the string, set the corresponding severity
  * in the widget's severity.
  * Example: { stringMatch: '1', severity: 2 }.
  */
 stringSeverity: PropTypes.object,
 /**
  * Directive to override alarm severity with the rules defined in the stringSeverity
  */


  useStringSeverityMatch: PropTypes.bool,
 /**
  * Material UI Typography variant.
  */
 variant: PropTypes.string,
  /**
   * Tooltip Text
   */
  tooltip:PropTypes.string,
  /**
   * Directive to show the tooltip
   */
  showTooltip:PropTypes.bool,
  /**
   *  Any of the MUI Tooltip props can applied by defining them as an object
   */

  tooltipProps:PropTypes.object,
 
};
TextUpdateStatus.defaultProps = {
 debug: false,
 variant:'body2',
 alarmSensitive: false,
 showTooltip:false
};
export default withStyles(styles, { withTheme: true })(TextUpdateStatus)
