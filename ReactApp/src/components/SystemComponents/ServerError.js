import React from 'react';



import Typography from '@material-ui/core/Typography';



const ServerError = (props) => {


    return (
        <Typography style={{ textAlign: 'center', paddingTop: '50vh' }}>{props.message?props.message:"Error the server is down"}</Typography>
    )

}

export default ServerError;
