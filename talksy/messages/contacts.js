class Contact{
    constructor(name, action){
        this.name = name;
        this.action = action;
    }
    
    render(){
        return `<div class="contact" id="${this.name}" onclick="${this.action}">
                <span class="contactprofileName">${this.name}</span>
                </div>`
    }
}

class ContactList{
    constructor(contacts, caction, aaction){
        this.contacts = contacts;
        this.caction = caction;
        this.aaction = aaction;
    }

    alterContacts(contacts){
        this.contacts = contacts;
    }

    render(){
        let inner = this.contacts.map(c=>{
            let cn = new Contact(c, this.caction);
            return cn.render();
        });

        let addcon = new AddContact(this.aaction)
        
        let el =`<div id="contactList">
                    <div id="clist">
                        ${inner}
                    </div>
                    ${addcon.render()}
                </div>`;
        el = el.replaceAll(',','');
        return el;
    }
}

class AddContact{
    constructor(action){
        this.action = action;
    }

    render(){
        return `<div id="addContact">
                    <input type="text" id="newContact" placeholder="Add a contact">
                    <input type="button" id="addBtn" value="Add" onclick="${this.action}">
                </div>`;
    }
}