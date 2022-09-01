import React from 'react/lib/ReactWithAddons';
import { serverCache, apiUrls } from '../data/server.js';
import { copyToClipboard } from './editfiles.jsx';

const FileToken = React.createClass({
    getInitialState() {
        return {
            fetching: false,
            token: null,
            zipFile : false
        }
    },
   
    getUrl(bucket,name,token) {
        return apiUrls.tempFileAccessLink(bucket,name,token)
    },
    

    render() {
        if (!this.props) {
            return null
        }
        let url=""
        let file_name="files.zip"
        if (!this.props.zipFile){
            url=this.getUrl(this.props.file.bucket, this.props.file.key, this.props.token)     
            file_name=this.props.file.key     
        } 
        else {
            url = this.getUrl(this.props.buckets[0], "files.zip", this.props.token) + "&all=1"
        } 
        
        return(
            <button type="button" className="btn btn-default btn-xs remove" onClick={() => {copyToClipboard(window.location.origin + url ); alert("'"+file_name +"' temporary link copied to clipboard!") }}
                title="Copy Temporary Access Link">
                <i className="glyphicon glyphicon-link" />
            </button>
        )
        

    }
})

export default FileToken;