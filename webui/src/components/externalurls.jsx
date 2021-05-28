import React from 'react/lib/ReactWithAddons';
const urlRegex = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/
import { List } from 'immutable';

export const ExternalUrls = React.createClass({
    getInitialState() {
        const values = this.props.record.getIn(['community_specific', this.props.communitySchemaId, 'external_url']) || List(['']);
        return {
            values,
            errors: values.map(function() {return false})
        }
    },

    validate(val, index) {
        if (!urlRegex.test(val)) {
            this.state.errors[index] = true;
        } else {
            this.state.errors[index] = false;
            let r = this.props.record.setIn(['community_specific', this.props.communitySchemaId, 'external_url'], this.state.values);
            this.props.setRecord(r)
        }
    },

    setter(val, index) {
        let values = this.state.values;
        values = values.setIn([index], val)
        this.setState({values}, () => { this.validate(val, index) })
    },

    btnAddRemove(e, i) {
        this.setState(i == 0 ? {values: this.state.values.concat('')} :  {values: this.state.values.splice(i), errors: this.state.errors.splice(i)})
    },
    btnClear(ev) {
        ev.preventDefault();
        this.setState({values: List(['']), errors: [false]})
        let r = this.props.record.deleteIn(['community_specific', this.props.communitySchemaId, 'external_url']);
        this.props.setRecord(r);
    },
    render() {
        const id = 'external_urls';
        const arrstyle =  {
            paddingLeft:'10px',
            borderLeft:'1px solid black',
            borderRadius:'4px',
        };
        const title = 'External file URLs';
        return (
            <div className="row" key={id} style={{marginBottom:'0.5em'}}>
                <div key={id} style={{marginBottom:'0.5em'}} title={title}>
                    <label htmlFor={id} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                        <span style={{float:'right', color:'black'}}>
                            {title}
                        </span>
                    </label>
                    <div className={"col-sm-9"} style={arrstyle} onFocus={onfocus} onBlur={onblur}>
                        <div className="container-fluid" style={{paddingLeft:0, paddingRight:0}}>
                            {this.state.values.map((val, i) =>{
                                const value_str = ""+(val || "");
                                const validClass = (this.state.errors[i]) ? " invalid-field " : "";
                                return (
                                    <div className="container-fluid" key={i}>
                                        <div className="row" key={i} style={{marginBottom:'0.5em'}}>
                                        <input type="text" className={"form-control"+ validClass}
                                            value={value_str} onChange={event => this.setter(event.target.value, i)} />
                                            <div className={"col-sm-offset-10 col-sm-2"} style={{paddingRight:0}}>
                                                { i == 0 ?
                                                    <btn className="btn btn-default btn-xs" style={{float:'right'}} onClick={ev => this.btnClear(ev)}
                                                        title="Clear all entries for this field">
                                                        <span><span className="glyphicon glyphicon-remove-sign" aria-hidden="true"/> Clear </span>
                                                    </btn>
                                                    : false
                                                }
                                                <btn className="btn btn-default btn-xs" style={{float:'right'}} onClick={ev => this.btnAddRemove(ev, i)}
                                                    title={(i == 0 ? "Add new entry" : "Remove this entry") + " for this field"}>
                                                    {i == 0 ?
                                                        <span><span className="glyphicon glyphicon-plus-sign" aria-hidden="true"/> Add </span> :
                                                        <span><span className="glyphicon glyphicon-minus-sign" aria-hidden="true"/> Remove </span>
                                                    }
                                                </btn>
                                            </div>
                                        </div>
                                </div> )})}
                        </div>
                    </div>
                </div>
        </div>
        )
    }
})

export const ExternalUrlsRec = (props) => {
    if (!props.urls) {
        return null
    } else
    return (
        <div className="well">
            <div className="row">
                <h3 className="col-sm-9">
                    { 'External file URLs' }
                </h3>
            </div>
        <div className='fileList'>
            { props.urls.map((url) => (
                <div className='row'>
                    <div className='col-sm-12'>
                        <a>{ url }</a>
                    </div>
                </div>
            )) }
            </div>
        </div>
    )
}