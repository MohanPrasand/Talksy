class Home{
    constructor(args){
        this.args = args;
    }
    
    render(){
        let cList = new ContactList(this.args.contacts, this.args.contactsAction, this.args.addAction);
        let msgs = new ChatArea(this.args.name, this.args.chats, this.args.sendAction);
        let el = `<div id="main">
                    <section id="left">
                        ${cList.render()}
                    </section>
                    <section id="right">
                        ${msgs.render()}
                    </section>
                </div>
                <div id="alertCon">
                    <div id="alert">
                        <div id="alertMsg"></div>
                        <input type="button" value="Close" onclick="closeAlert()" id="alertClose">
                    </div>
                </div>`
        return el;
    }
}
