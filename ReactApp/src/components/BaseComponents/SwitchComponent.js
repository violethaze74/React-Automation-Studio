import React from "react";
import { withStyles } from "@material-ui/core/styles";
import { FormControlLabel, Switch } from "@material-ui/core";
import Widget from "../SystemComponents/Widgets/Widget";
import PropTypes from 'prop-types';
const styles = (theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
  },
  FormControl: {
    width: "100%",
    height: "100%",
    marginTop: "auto",
    marginBottom: "auto",
    marginLeft: "auto",
    marginRight: "auto",
  },
});

/* eslint-disable eqeqeq */
const SwitchInternalComponent = (props) => {
  console.warn("Deprecated use Switch instead")

  /**
   * Save switch state.
   * @param {Event} event
   */
 const handleButtonChange=(event)=> {
    let value = event.target.checked ? 1 : 0;
    props.handleImmediateChange(value);
  }

 
    return (
      <FormControlLabel
        key={props.pvName}
        className={props.classes.FormControl}
        disabled={props.disabled}
        label={props.label}
        labelPlacement={props.labelPosition}
        control={
          <Switch
            onChange={handleButtonChange}
            checked={props.value == 1}
            color={props.onColor}
            {... props.muiSwitchProps}
          />
        }
      />
    );
  }
  /* eslint-disable eqeqeq */
/**
 * **Deprecated  Use the Switch instead**. The SwitchComponent component is a wrapper on a Material-UI Selection Control component.
 * The Selection Control component is implemented with zero margins and enabled to grow to the width of its parent container.<br/><br/>
 * The margins and spacing must be controlled from the parent component.<br/><br/>
 * Material-UI Selection Control Demos:
 * https://material-ui.com/demos/selection-controls/<br/><br/>
 * Material-UI Switch API:
 * https://material-ui.com/api/switch/
 */
const SwitchComponent =(props)=>{
  return (
    <Widget {...props} component={SwitchInternalComponent} usePvMinMax={false} usePvPrecision={false} min={undefined} max={undefined} prec={undefined} />
       
    
  )
}

SwitchComponent.propTypes = {
  /** Name of the process variable,  eg. '$(device):test$(id)'*/
  pv: PropTypes.string.isRequired,
  /** Values of macros that will be substituted in the pv name eg. {{'$(device)':'testIOC','$(id)':'2'}}*/
  macros: PropTypes.object,

  /** local variable initialization value*/
  initialLocalVariableValue: PropTypes.string,
  /** If defined, then the DataConnection debugging information will be displayed*/
  debug: PropTypes.bool,
  /** label placement*/
  labelPlacement: PropTypes.oneOf(['start', 'top', 'bottom', 'end']),
  /** Custom label to be used, if  `usePvLabel` is not defined. */
  label: PropTypes.string,
  /**
 * Custom on color to be used, must be derived from Material UI theme color's.
 */
  onColor: PropTypes.string,
  /**
   * Directive to fill the component's label with
   * the value contained in the  pv metadata's DESC field or the labelPv value.
   * If not defined it uses the custom label as defined by the label prop.
   */
  usePvLabel: PropTypes.bool,
   /**
  * Custom PV to define the units to be used, usePvLabel must be set to `true` and useMetadata to `false`, eg. '$(device):test$(id)'.
  */
 labelPv: PropTypes.string,
 /** Any of the MUI Switch Props can applied by defining them as an object
   * 
   */
  muiSwitchProps: PropTypes.object
  

}
SwitchComponent.defaultProps = {
  onColor: 'primary',
  debug: false,
}
export default withStyles(styles, { withTheme: true })(SwitchComponent)

