class DateBox{
    constructor(dt){
        this.dt = dt;
    }

    render(){
        return `<div class="dateBox">${this.dt}</div>`
    }
}

class Message{
    constructor(type, author, message, time, status){
        this.author = author;
        this.message = message;
        this.time = time;
        this.status = status;
        this.type = type;
    }

    render(){
        return `<div class=${this.type}>
                    <div class="sender">${this.author}</div>
                    <div class="message">${this.message}</div>
                    ${this.type=="send"? `<div class="status">${this.status==0? "sending...": (this.status==1? "sent": (this.status==2? "delivered": (this.status==3?"seen":"")))}</div>`:''}
                    <div class="time">${this.time}</div>
                </div>`
    }
}

class ChatBox{
    constructor(chats){
        this.chats = chats;
    }

    render(){
        let ldt = -1;
        let fn = `<div id="chatBox">
                    ${this.chats.map(ch=>{
                        let chc = new Message(ch.type, ch.author, ch.message, ch.time, ch.status);
                        if(ldt != ch.date){
                            ldt = ch.date;
                            let l = new DateBox(ch.date);
                            return l.render()+chc.render();
                        }
                        return chc.render();
                    })}
                </div>`
        fn = fn.replaceAll(',', '');
        return fn;
    }
}

class Profile{
    constructor(name){
        this.name = name;
    }

    render(){
        return `<div id="profile">
                    ${this.name}
                </div>`
    }
}

class MessageWriter{
    constructor(action){
        this.action = action;
    }

    render(){
        return `<div id="messageWriter">
                    <input type="text" name="message" id="messageInput" placeholder="Enter your message here" maxlength="50">
                    <button type="submit" id="messageSend" onclick="${this.action}">Send</button>
                </div>`
    }
}

class ChatArea{
    constructor(name, chats, action){
        this.name = name;
        this.chats = chats;
        this.action = action;
    }

    render(){
        if(this.name.length==0)
            return '';

        let prof = new Profile(this.name);
        let chatbx = new ChatBox(this.chats);
        let msgwrt = new MessageWriter(this.action);

        return `<div id="chatArea">
                    ${prof.render()}
                    ${chatbx.render()}
                    ${msgwrt.render()}
                </div>`;
    }
}