import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';


import Grid from '@material-ui/core/Grid';



import SideBar from '../SystemComponents/SideBar';
import Settings from '../SystemComponents/Settings';
import AppBar from '@material-ui/core/AppBar';

import MoreVertRoundedIcon from '@material-ui/icons/MoreVertRounded';

import Toolbar from '@material-ui/core/Toolbar';

import AutomationStudioContext from '../SystemComponents/AutomationStudioContext';
import Card from '@material-ui/core/Card';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
const systemName = 'testIOC';




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



class AllUsers extends React.Component {
  constructor(props) {
    super(props);
    
  
    let database   = this.props.database;
    let collection = this.props.collection;
    
    let dbListBroadcastReadUsersURL = 'mongodb://' + database + ':' + collection + ':' + 'users'+':Parameters:""';
    let dbListBroadcastReadUagsURL = 'mongodb://' + database + ':' + collection + ':' + 'UAGS'+':Parameters:""';
    this.state = {
      
      dbListBroadcastReadUsersURL:dbListBroadcastReadUsersURL,
      dbListBroadcastReadUagsURL:dbListBroadcastReadUagsURL,
      tabValue: 0,
      users:[],
      userGroups:[],
     



    }

    this.handleNewDbUsersList=this.handleNewDbUsersList.bind(this);
    this.handleNewDbUagsList=this.handleNewDbUagsList.bind(this);

  }



  handleNewDbUsersList=(msg)=>{
    let data = JSON.parse(msg.data);
    this.setState({users:data})
    //console.log(data)
  }
  handleNewDbUagsList=(msg)=>{
    let data = JSON.parse(msg.data);
    this.setState({userGroups:data[0].userGroups})
    //console.log(data)
  }
  handleTabChange = (event, value) => {
    this.setState({ tabValue: value });
  };
  getDateTime=(timestamp)=>{
    let date=new Date(parseFloat(timestamp*1000))
   
    return date.toUTCString()
  }

  getUAGs=(UAGS,username)=>{
    let UagKeys=Object.keys(UAGS);
    let uag;
    let uagString="";
    for (uag in UagKeys){
      let usernames;
      for (usernames in UAGS[UagKeys[uag]]['usernames']){
        if ((username==UAGS[UagKeys[uag]]['usernames'][usernames])||(UAGS[UagKeys[uag]]['usernames'][usernames])=='*'){
         // console.log(UAGS[UagKeys[uag]]['usernames'][usernames])
          uagString=uagString.length>0?uagString+', '+UagKeys[uag].toString():UagKeys[uag].toString();
        }
      }

    }

    console.log("UAGS",UAGS)
    console.log("username",username)
   
    return uagString
  }
  componentDidMount(){
    let socket = this.context.socket;



    let jwt = JSON.parse(localStorage.getItem('jwt'));
    if (jwt === null) {
      jwt = 'unauthenticated'
    }
    
    socket.emit('databaseBroadcastRead', { dbURL: this.state.dbListBroadcastReadUsersURL, 'clientAuthorisation': jwt }, (data) => {

      if (data !== "OK") {
        console.log("ackdata", data);
      }
    });
    socket.emit('databaseBroadcastRead', { dbURL: this.state.dbListBroadcastReadUagsURL, 'clientAuthorisation': jwt }, (data) => {

      if (data !== "OK") {
        console.log("ackdata", data);
      }
    });
    socket.on('databaseData:' + this.state.dbListBroadcastReadUsersURL, this.handleNewDbUsersList);
    socket.on('databaseData:' + this.state.dbListBroadcastReadUagsURL, this.handleNewDbUagsList);
  }

  render() {
    //      console.log("state: ",this.state);
    //console.log('displayHarps',this.state.displayHarps)
    console.log(this.context.userData)
    const { classes } = this.props;
    const topTabValue = this.state.topTabValue;
    const sideTabValue = this.state.sideTabValue;
    const users=this.state.users;
    const userGroups=this.state.userGroups;
    return (
      <React.Fragment>
        
        <div style={{ "overflowX": "hidden", 'overflowY': 'hidden' }}>
          <Grid
            style={{ marginTop: 0, padding: 8 }}
            container
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            spacing={0}
          >



            <Grid item xs={12} sm={12} md={12} lg={12} >

            <Card>
              
              <Table className={classes.table} stickyHeader size="small" aria-label="sticky table">
                    <TableHead>
                      <TableRow>
                      <TableCell align="center">Index</TableCell>
                        <TableCell align="center">Username</TableCell>
                        <TableCell align="center">UAGS</TableCell>
                        <TableCell align="center">Email</TableCell>
                        
                        <TableCell align="center">Password Last Updated On</TableCell>
                        

                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {users.map((user,index)=>(
                        <TableRow key={index.toString()}>
                          <TableCell align="center">{index+1}</TableCell>
                          <TableCell align="center">{user.username}</TableCell>
                          <TableCell align="center">{this.getUAGs(userGroups,user.username)}</TableCell>
                          <TableCell align="center">{user.email}</TableCell>
                          <TableCell align="center">{this.getDateTime(user.timestamp)}</TableCell>
                        </TableRow>
                      )
                      )
                      }
                    </TableBody>
                </Table>
            </Card>
          


            </Grid>

          </Grid>




        </div>
      </React.Fragment>




    );
  }
}

AllUsers.propTypes = {
  classes: PropTypes.object.isRequired,
};
AllUsers.contextType = AutomationStudioContext;
export default withStyles(styles)(AllUsers);
//export default AllUsers;
