import React, { Component } from 'react';

import withStyles from '@material-ui/core/styles/withStyles';
import AutomationStudioContext from '../SystemComponents/AutomationStudioContext';
import RedirectToLogIn from '../SystemComponents/RedirectToLogin.js';
import SideBar from '../SystemComponents/SideBar';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';


import DataConnection from '../SystemComponents/DataConnection';
import Typography from '@material-ui/core/Typography';

import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import AlarmList from './AlarmList';
import AlarmTable from './AlarmTable';

import ListItemIcon from '@material-ui/core/ListItemIcon';
import IconButton from '@material-ui/core/IconButton';
import MoreVertIcon from '@material-ui/icons/MoreVert';
import ContactPhoneIcon from '@material-ui/icons/ContactPhone';
import InputIcon from '@material-ui/icons/Input';
import NotInterestedIcon from '@material-ui/icons/NotInterested';

function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

// Styles
const styles = theme => ({
    root: {
        padding: theme.spacing(1),
        // paddingLeft: theme.spacing(8),
        overflowX: "hidden",
        overflowY: "hidden",
        paddingTop: 0
    },
    card: {
        padding: theme.spacing(2),
        height: "100%",
        overflowX: "default",
        overflowY: "default",
    },
    center: {
        margin: 'auto',
        width: '100%',
        height: '100%'

    },
    button: {
        marginTop: '10px',
        paddingTop: '10px',
        width: '100%',

    },
    appBar: {
        zIndex: theme.zIndex.drawer + 1,
    }
});
class AlarmHandler extends Component {
    constructor(props) {
        super(props);
        // to connect to all PVs before updating state
        this.alarmPVDict = {}
        this.areaPVDict = {}
        this.state = {
            moreVertMenuShow: false,
            moreVertAchorEl: null,
            alarmDebug: false,
            alarmAckField: '',
            alarmAckFieldTrig: false,
            alarmIOCPVPrefix: null,
            alarmIOCPVSuffix: null,
            alarmPVDict: {},
            areaPVDict: {},
            alarmRowSelected: {},
            alarmContextOpen: {},
            areaAlarms: {},
            areaContextOpen: {},
            areaEnabled: {},
            areaMongoId: {},
            areaNames: [],
            areaSelectedIndex: null,
            areaSelectedName: '',
            areaSubAreaOpen: {},
            areaSubAreaMongoId: {},
            contextMouseX: null,
            contextMouseY: null,
            lastAlarm: null,
            loadAlarmTable: {
                alarmPV: false,
            },
            lastArea: null,
            loadAlarmList: {
                areaPV: false,
            }
        }

        this.logout = this.logout.bind(this);
    }

    logout() {
        localStorage.removeItem('jwt');

    }

    handleDoNothing = () => {

    }

    // handleSetAckField = (value) => {
    //     const alarmAckField = this.state.alarmAckField
    //     if (alarmAckField === '') {
    //         // console.log("set alarmAckField", value)
    //         this.setState({ alarmAckField: value })
    //     }
    // }

    handleMoreVertClick = (event) => {
        this.setState({ moreVertAchorEl: event.currentTarget })
    }

    handleMoreVertClose = (event) => {
        this.setState({ moreVertAchorEl: null })
    }

    handleAlarmTesting = (event) => {
        this.setState(prevState => {
            return {
                ...prevState,
                alarmDebug: !prevState.alarmDebug
            }
        })
        this.handleMoreVertClose()
    }

    handleSimplePrint = (value, pvname) => {
        // console.log(pvname, value)
    }

    handleAreaPVChange = (value, pvname) => {
        let areaName = pvname.replace("pva://", "")
        areaName = areaName.replace(this.state.alarmIOCPVPrefix, "")

        // console.log(areaName)

        // still connecting to pvs
        if (!this.state.loadAlarmList.areaPV) {
            this.areaPVDict[areaName] = value
            if (this.state.lastArea === areaName) {
                const loadAlarmList = { ...this.state.loadAlarmList }
                loadAlarmList.areaPV = true
                this.setState({ loadAlarmList: loadAlarmList })
                this.setState({ areaPVDict: this.areaPVDict })
            }
        }
        // all pvs connected
        else {
            const areaPVDict = { ...this.state.areaPVDict }
            areaPVDict[areaName] = value
            this.setState({ areaPVDict: areaPVDict })
        }
    }

    handleAlarmPVChange = (value, pvname) => {
        // console.log(pvname)
        let epicsPVName = pvname.replace("pva://", "")
        epicsPVName = epicsPVName.replace(this.state.alarmIOCPVPrefix, "")
        epicsPVName = epicsPVName.replace(this.state.alarmIOCPVSuffix, "")

        // console.log(epicsPVName, value)

        // still connecting to pvs
        if (!this.state.loadAlarmTable.alarmPV) {
            this.alarmPVDict[epicsPVName] = value
            if (this.state.lastAlarm === epicsPVName) {
                const loadAlarmTable = { ...this.state.loadAlarmTable }
                loadAlarmTable.alarmPV = true
                this.setState({ loadAlarmTable: loadAlarmTable })
                this.setState({ alarmPVDict: this.alarmPVDict })
            }
        }
        // all pvs connected
        else {
            const alarmPVDict = { ...this.state.alarmPVDict }
            alarmPVDict[epicsPVName] = value
            this.setState({ alarmPVDict: alarmPVDict })
        }
    }

    handleAckAllAreaAlarms = (event, index) => {
        // console.log('Ack all alarms for', index)
        const alarmAckFieldTrig = !this.state.alarmAckFieldTrig
        this.handleListItemContextClose(event, index)
        this.setState({ alarmAckField: index, alarmAckFieldTrig: alarmAckFieldTrig })
    }

    handleTableItemCheck = (event, index, alarm, field, value) => {
        // console.log(index, alarm, field, value)

        let socket = this.context.socket;
        let jwt = JSON.parse(localStorage.getItem('jwt'));
        if (jwt === null) {
            jwt = 'unauthenticated'
        }

        const ALARM_DATABASE = "ALARM_DATABASE"
        const dbName = "demoAlarmDatabase"
        const colName = "pvs"
        const dbURL = "mongodb://" + ALARM_DATABASE + ":" + dbName + ":" + colName

        const id = this.state.areaMongoId[index]
        let newvalues = null

        // Check if it is a subArea
        // console.log(index)
        if (index.includes("-")) {
            const subAreaId = this.state.areaSubAreaMongoId[index] + ".pvs." + alarm + "." + field
            newvalues = { '$set': { [subAreaId]: value } }
        }
        else {
            const subAreaId = "pvs." + alarm + "." + field
            newvalues = { '$set': { [subAreaId]: value } }
        }

        // console.log(newvalues)

        socket.emit('databaseUpdateOne', { dbURL: dbURL, 'id': id, 'newvalues': newvalues, 'clientAuthorisation': jwt }, (data) => {
            //  console.log("ackdata", data);
            if (data == "OK") {
                socket.emit('databaseBroadcastRead', { dbURL: dbURL + ':Parameters:{}', 'clientAuthorisation': jwt }, (data) => {
                    if (data !== "OK") {
                        console.log("ackdata", data);
                    }
                })
            } else {
                console.log("TableItemCheck unsuccessful")
            }
        })

    }

    handleTableItemRightClick = (event, index) => {
        event.preventDefault();
        const areaAlarmNameArray = index.split('-')
        let areaName = null
        if (areaAlarmNameArray.length > 2) {
            areaName = areaAlarmNameArray[0] + "-" + areaAlarmNameArray[1]
        }
        else {
            areaName = areaAlarmNameArray[0]
        }
        if (this.state.areaEnabled[areaName] && this.state.areaAlarms[index]["enable"]) {
            const alarmContextOpen = { ...this.state.alarmContextOpen }
            alarmContextOpen[index] = true

            const alarmRowSelected = { ...this.state.alarmRowSelected }
            alarmRowSelected[index] = true

            const contextMouseX = event.clientX - 2
            const contextMouseY = event.clientY - 2

            this.setState({ alarmContextOpen: alarmContextOpen, alarmRowSelected: alarmRowSelected, contextMouseX: contextMouseX, contextMouseY: contextMouseY })
        }
    }

    handleAlarmContextClose = (event, index) => {
        const alarmContextOpen = { ...this.state.alarmContextOpen }
        alarmContextOpen[index] = false

        const alarmRowSelected = { ...this.state.alarmRowSelected }
        alarmRowSelected[index] = false

        this.setState({ alarmRowSelected: alarmRowSelected, alarmContextOpen: alarmContextOpen })
    }

    handleAlarmAcknowledge = (event, index) => {
        // console.log("Ack alarm:", index)
        const alarmAckFieldTrig = !this.state.alarmAckFieldTrig
        this.handleAlarmContextClose(event, index)
        this.setState({ alarmAckField: index, alarmAckFieldTrig: alarmAckFieldTrig })
    }

    handleEnableDisableArea = (event, index, value) => {
        // console.log('Enable/Disable area', index)

        let socket = this.context.socket;
        let jwt = JSON.parse(localStorage.getItem('jwt'));
        if (jwt === null) {
            jwt = 'unauthenticated'
        }

        const ALARM_DATABASE = "ALARM_DATABASE"
        const dbName = "demoAlarmDatabase"
        const colName = "pvs"
        const dbURL = "mongodb://" + ALARM_DATABASE + ":" + dbName + ":" + colName

        const id = this.state.areaMongoId[index]
        let newvalues = null

        // Check if it is a subArea
        // console.log(index)
        if (index.includes("-")) {
            const subAreaId = this.state.areaSubAreaMongoId[index] + ".enable"
            newvalues = { '$set': { [subAreaId]: value } }
        }
        else {
            newvalues = { '$set': { "enable": value } }
        }

        // console.log(newvalues)


        socket.emit('databaseUpdateOne', { dbURL: dbURL, 'id': id, 'newvalues': newvalues, 'clientAuthorisation': jwt }, (data) => {
            // console.log("ackdata", data);
            if (data == "OK") {
                socket.emit('databaseBroadcastRead', { dbURL: dbURL + ':Parameters:{}', 'clientAuthorisation': jwt }, (data) => {
                    if (data !== "OK") {
                        console.log("ackdata", data);
                    }
                })
            } else {
                console.log("Enable/Disable area unsuccessful")
            }
        })

        this.handleListItemContextClose(event, index)

    }

    handleListItemContextClose = (event, index) => {
        // console.log("close context")
        const areaContextOpen = { ...this.state.areaContextOpen }
        areaContextOpen[index] = false
        this.setState({ areaContextOpen: areaContextOpen })
    }

    handleListItemRightClick = (event, index) => {
        // console.log("right click")
        event.preventDefault();

        const areaContextOpen = { ...this.state.areaContextOpen }
        areaContextOpen[index] = true

        const contextMouseX = event.clientX - 2
        const contextMouseY = event.clientY - 2

        this.setState({ areaContextOpen: areaContextOpen, contextMouseX: contextMouseX, contextMouseY: contextMouseY })
    }

    handleListItemClick = (event, index) => {
        // console.log("left click")
        // console.log(index)
        const areaSubAreaOpen = {
            ...this.state.areaSubAreaOpen,
        }
        Object.keys(areaSubAreaOpen).map(areaKey => {
            if (areaKey !== index) {
                areaSubAreaOpen[areaKey] = false
            }

        })

        if (index === this.state.areaSelectedIndex || !this.state.areaSelectedIndex.includes(index)) {
            areaSubAreaOpen[index] = !this.state.areaSubAreaOpen[index]
        }

        let areaSelectedName = index.split('-')
        if (areaSelectedName.length > 1) {
            areaSelectedName = areaSelectedName[0] + " > " + areaSelectedName[1]
        }
        else {
            this.setState({ areaSubAreaOpen: areaSubAreaOpen })
        }

        // console.log(this.state.areaSubAreaOpen)
        this.setState({ areaSelectedIndex: index, areaSelectedName: areaSelectedName })
    };

    handleNewDbPVsList = (msg) => {
        const data = JSON.parse(msg.data);
        // console.log(data)
        const areaNames = []
        if (isEmpty(this.state.alarmRowSelected)) {
            // console.log('Only once OR for local UI vars')
            let lastAlarm = ""
            const areaContextOpen = {}
            const alarmContextOpen = {}
            const alarmRowSelected = {}
            const areaMongoId = {}
            const areaSubAreaMongoId = {}
            const areaSubAreaOpen = {
                ...this.state.areaSubAreaOpen,
            }

            data.map((area, index) => {
                areaContextOpen[area["area"]] = false
                if (index === 0) {
                    // Open first area on start up or refresh page
                    areaSubAreaOpen[area["area"]] = true
                }
                else {
                    areaSubAreaOpen[area["area"]] = false
                }
                areaMongoId[area["area"]] = area["_id"]["$oid"]
                // Map alarms in area
                Object.keys(area["pvs"]).map(alarmKey => {
                    alarmContextOpen[`${area["area"]}-${alarmKey}`] = false
                    alarmRowSelected[`${area["area"]}-${alarmKey}`] = false
                    lastAlarm = area["pvs"][alarmKey]["name"]
                })
                Object.keys(area).map(areaKey => {
                    if (areaKey === "area") {
                        areaNames.push({ "area": area[areaKey] })
                    }
                    else if (areaKey.includes("subArea")) {
                        areaContextOpen[`${area["area"]}-${area[areaKey]["name"]}`] = false
                        areaSubAreaMongoId[`${area["area"]}-${area[areaKey]["name"]}`] = areaKey
                        areaMongoId[`${area["area"]}-${area[areaKey]["name"]}`] = area["_id"]["$oid"]
                        // Map alarms in subarea
                        Object.keys(area[areaKey]["pvs"]).map(alarmKey => {
                            alarmContextOpen[`${area["area"]}-${area[areaKey]["name"]}-${alarmKey}`] = false
                            alarmRowSelected[`${area["area"]}-${area[areaKey]["name"]}-${alarmKey}`] = false
                            lastAlarm = area[areaKey]["pvs"][alarmKey]["name"]
                        })
                        if (areaNames[index]["subAreas"]) {
                            areaNames[index]["subAreas"].push(area[areaKey]["name"])
                        }
                        else {
                            // console.log(areaNames[index])
                            areaNames[index]["subAreas"] = [area[areaKey]["name"]]
                        }
                    }
                })
            })
            if (!this.state.areaSelectedIndex) {
                // console.log("First mount update selection")
                const areaSelectedIndex = areaNames[0]["area"]
                const areaSelectedName = areaNames[0]["area"]
                this.setState({ areaSubAreaOpen: areaSubAreaOpen, areaSelectedIndex: areaSelectedIndex, areaSelectedName: areaSelectedName })
            }
            // console.log(lastAlarm)
            this.setState({ lastAlarm })
            this.setState({ alarmRowSelected: alarmRowSelected, alarmContextOpen: alarmContextOpen })
            this.setState({ areaMongoId: areaMongoId, areaSubAreaMongoId: areaSubAreaMongoId })
            this.setState({ areaNames: areaNames, areaContextOpen: areaContextOpen })
        }

        const areaAlarms = {}
        const areaEnabled = {}
        let lastArea = ""

        data.map((area, index) => {
            // map all alarms in area
            Object.keys(area).map(areaKey => {
                if (areaKey === "pvs") {
                    Object.keys(area[areaKey]).map(alarm => {
                        areaAlarms[`${area["area"]}-${alarm}`] = area[areaKey][alarm]
                    })
                }
            })
            areaEnabled[area["area"]] = area["enable"]
            lastArea = area["area"]
            Object.keys(area).map(areaKey => {
                if (areaKey.includes("subArea")) {
                    // Area enabled for subArea includes parent area
                    areaEnabled[`${area["area"]}-${area[areaKey]["name"]}`] = area[areaKey]["enable"] && areaEnabled[area["area"]]
                    lastArea = `${area["area"]}-${area[areaKey]["name"]}`
                    // map all alarms in subArea
                    Object.keys(area[areaKey]).map(subAreaKey => {
                        if (subAreaKey === "pvs") {
                            Object.keys(area[areaKey][subAreaKey]).map(alarm => {
                                areaAlarms[`${area["area"]}-${area[areaKey]["name"]}-${alarm}`] = area[areaKey][subAreaKey][alarm]
                            })
                        }
                    })
                }
            })
        })

        // console.log(lastArea)

        this.setState({ areaAlarms: areaAlarms, areaEnabled: areaEnabled, lastArea: lastArea })

        let displayAlarmTable = true
        for (const [key, value] of Object.entries(this.state.loadAlarmTable)) {
            // console.log(key, value)
            displayAlarmTable = displayAlarmTable && value
        }
        if (!displayAlarmTable) {
            this.loadAlarmTable()
        }

        let displayAlarmList = true
        for (const [key, value] of Object.entries(this.state.loadAlarmList)) {
            // console.log(key, value)
            displayAlarmList = displayAlarmList && value
        }
        if (!displayAlarmList) {
            this.loadAlarmList()
        }
    }

    handleDbConfig = (msg) => {
        const data = JSON.parse(msg.data)[0];
        this.setState({ alarmIOCPVPrefix: data["alarmIOCPVPrefix"], alarmIOCPVSuffix: data['alarmIOCPVSuffix'] })
    }

    componentDidMount() {
        // console.log('[AlarmHander] componentDidMount')
        let socket = this.context.socket;
        let jwt = JSON.parse(localStorage.getItem('jwt'));

        if (jwt === null) {
            jwt = 'unauthenticated'
        }

        const ALARM_DATABASE = "ALARM_DATABASE"
        const dbName = "demoAlarmDatabase"
        let colName = "pvs"
        let dbURL = "mongodb://" + ALARM_DATABASE + ":" + dbName + ":" + colName + ":Parameters:{}"

        socket.emit('databaseBroadcastRead', { dbURL: dbURL, 'clientAuthorisation': jwt }, (data) => {

            if (data !== "OK") {
                console.log("ackdata", data);
            }
        });
        socket.on('databaseData:' + dbURL, this.handleNewDbPVsList);

        colName = "config"

        dbURL = "mongodb://" + ALARM_DATABASE + ":" + dbName + ":" + colName + ":Parameters:{}"

        socket.emit('databaseBroadcastRead', { dbURL: dbURL, 'clientAuthorisation': jwt }, (data) => {

            if (data !== "OK") {
                console.log("ackdata", data);
            }
        });
        socket.on('databaseData:' + dbURL, this.handleDbConfig);

    }

    loadAlarmTable = () => {
        const timer = setTimeout(() => {
            console.log('Auto load alarm table')
            const loadAlarmTable = this.state.loadAlarmTable
            for (const [key, value] of Object.entries(loadAlarmTable)) {
                loadAlarmTable[key] = true
            }
            this.setState({ loadAlarmTable: loadAlarmTable })
        }, 10000);
        return () => clearTimeout(timer);
    }

    loadAlarmList = () => {
        const timer = setTimeout(() => {
            console.log('Auto load alarm list')
            const loadAlarmList = this.state.loadAlarmList
            for (const [key, value] of Object.entries(loadAlarmList)) {
                loadAlarmList[key] = true
            }
            this.setState({ loadAlarmList: loadAlarmList })
        }, 10000);
        return () => clearTimeout(timer);
    }

    render() {
        const { classes } = this.props;
        const { areaSelectedName } = this.state;

        let alarmPVs = null
        if (this.state.alarmIOCPVPrefix !== null) {
            alarmPVs = Object.keys(this.state.areaAlarms).map(alarmKey => (
                <DataConnection
                    key={alarmKey}
                    pv={'pva://' + this.state.alarmIOCPVPrefix + this.state.areaAlarms[alarmKey]["name"] + this.state.alarmIOCPVSuffix}
                    handleInputValue={this.handleAlarmPVChange}
                />
            ))
        }

        let ackPV = null
        if (this.state.alarmIOCPVPrefix !== null) {
            ackPV = (
                <DataConnection
                    pv={'pva://' + this.state.alarmIOCPVPrefix + "ACK_PV"}
                    handleInputValue={this.handleDoNothing}
                    outputValue={this.state.alarmAckField}
                    debug={false}
                    newValueTrigger={this.state.alarmAckFieldTrig}
                />
            )
        }

        let areaPVs = null
        if (this.state.alarmIOCPVPrefix !== null) {
            areaPVs = Object.keys(this.state.areaEnabled).map(areaName => (
                <DataConnection
                    key={areaName}
                    pv={'pva://' + this.state.alarmIOCPVPrefix + areaName}
                    handleInputValue={this.handleAreaPVChange}
                />
            ))
        }

        let displayAlarmTable = true
        for (const [key, value] of Object.entries(this.state.loadAlarmTable)) {
            // console.log(key, value)
            displayAlarmTable = displayAlarmTable && value
        }

        let displayAlarmList = true
        for (const [key, value] of Object.entries(this.state.loadAlarmList)) {
            // console.log(key, value)
            displayAlarmList = displayAlarmList && value
        }


        // console.log(this.state.alarmIOCPVPrefix)

        return (
            <React.Fragment>
                {alarmPVs}
                {areaPVs}
                {ackPV}

                <div id="test" className={classes.root}>
                    <div
                        style={{
                            display: 'flex',
                            paddingTop: 20,
                        }}
                    >
                        <SideBar />
                        <div style={{ textAlign: 'center', fontSize: 16, fontWeight: 'bold', flexGrow: 1 }}>ALARM HANDLER</div>
                        <IconButton aria-label="display more actions" color="inherit" onClick={event => this.handleMoreVertClick(event)}>
                            <MoreVertIcon />
                        </IconButton>
                        <Menu
                            id="simple-menu"
                            anchorEl={this.state.moreVertAchorEl}
                            keepMounted
                            open={Boolean(this.state.moreVertAchorEl)}
                            onClose={this.handleMoreVertClose}
                        >
                            <MenuItem onClick={this.handleDoNothing}>
                                <ListItemIcon >
                                    <ContactPhoneIcon fontSize="small" />
                                </ListItemIcon>
                                <Typography variant="inherit">Configure user notification</Typography>
                            </MenuItem>
                            <MenuItem onClick={this.handleAlarmTesting}>
                                <ListItemIcon >
                                    {this.state.alarmDebug
                                        ? <NotInterestedIcon fontSize="small" />
                                        : <InputIcon fontSize="small" />
                                    }
                                </ListItemIcon>
                                <Typography variant="inherit">
                                    {this.state.alarmDebug
                                        ? "Disable alarm testing/debug"
                                        : "Enable alarm testing/debug"
                                    }</Typography>

                            </MenuItem>
                        </Menu>
                    </div>

                    <Grid
                        container
                        direction="row"
                        justify="flex-start"
                        alignItems="stretch"
                        spacing={2}
                        style={{ paddingLeft: 50 }}
                    >

                        {displayAlarmList
                            ? <Grid item xs={2}>
                                <Card className={classes.card}>
                                    <Grid
                                        container
                                        direction="row"
                                        justify="flex-start"
                                        alignItems="stretch"
                                        spacing={2}>
                                        <Grid item xs={12}>
                                            <div style={{ paddingTop: 16, fontSize: 16, fontWeight: 'bold' }}>Alarm Areas</div>
                                        </Grid>
                                        <Grid item xs={12}>
                                            {this.state.areaNames ?
                                                <AlarmList
                                                    areaPVDict={this.state.areaPVDict}
                                                    ackAllAreaAlarms={this.handleAckAllAreaAlarms}
                                                    areaContextOpen={this.state.areaContextOpen}
                                                    areaEnabled={this.state.areaEnabled}
                                                    areaNames={this.state.areaNames}
                                                    areaSubAreaOpen={this.state.areaSubAreaOpen}
                                                    areaSelectedIndex={this.state.areaSelectedIndex}
                                                    contextMouseX={this.state.contextMouseX}
                                                    contextMouseY={this.state.contextMouseY}
                                                    enableDisableArea={this.handleEnableDisableArea}
                                                    listItemClick={this.handleListItemClick}
                                                    listItemRightClick={this.handleListItemRightClick}
                                                    listItemContextClose={this.handleListItemContextClose}
                                                />
                                                : "No data from database"}
                                        </Grid>
                                    </Grid>
                                </Card>
                            </Grid>
                            : <Grid item xs={2}>
                                <Card className={classes.card}>
                                    <div style={{ fontSize: 16, fontWeight: 'bold' }}>
                                        CONNECTING TO PVs...
                                    </div>
                                </Card>
                            </Grid>}
                        {displayAlarmTable ?
                            <Grid item xs={10} style={{ paddingRight: 32 }}>
                                <Card className={classes.card}>
                                    <Grid
                                        container
                                        direction="row"
                                        justify="flex-start"
                                        alignItems="stretch"
                                        spacing={2}>
                                        <Grid item xs={12}>
                                            <div style={{ paddingTop: 16, fontSize: 16, fontWeight: 'bold' }}>{areaSelectedName}</div>
                                        </Grid>
                                        <Grid item xs={12}>
                                            {this.state.areaNames
                                                ? <AlarmTable
                                                    debug={this.state.alarmDebug}
                                                    alarmPVDict={this.state.alarmPVDict}
                                                    alarmRowSelected={this.state.alarmRowSelected}
                                                    alarmAcknowledge={this.handleAlarmAcknowledge}
                                                    alarmContextClose={this.handleAlarmContextClose}
                                                    alarmContextOpen={this.state.alarmContextOpen}
                                                    areaSelectedIndex={this.state.areaSelectedIndex}
                                                    areaAlarms={this.state.areaAlarms}
                                                    contextMouseX={this.state.contextMouseX}
                                                    contextMouseY={this.state.contextMouseY}
                                                    itemChecked={this.handleTableItemCheck}
                                                    areaEnabled={this.state.areaEnabled}
                                                    tableItemRightClick={this.handleTableItemRightClick}
                                                />
                                                : "No data from database"}
                                        </Grid>
                                    </Grid>
                                </Card>
                            </Grid>
                            :
                            <Grid item xs={10} style={{ paddingRight: 32 }}>
                                <Card className={classes.card}>
                                    <div style={{ fontSize: 16, fontWeight: 'bold' }}>
                                        CONNECTING TO PVs...
                                    </div>
                                </Card>
                            </Grid>
                        }

                    </Grid>
                    <RedirectToLogIn />
                </div>
            </React.Fragment >
        )
    }
}

AlarmHandler.contextType = AutomationStudioContext;

export default withStyles(styles, { withTheme: true })(AlarmHandler);
