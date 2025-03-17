let contacts = [];
let userChats = {'':[]};
let idChat = {};
let currChat = '';
let usernm = sessionStorage.getItem("username");
let tkn = sessionStorage.getItem("token");

function closeAlert(){
    document.getElementById("alertCon").style.scale = 0;
}

function showAlert(msg){
    document.getElementById("alertMsg").innerText = msg;
    document.getElementById("alertCon").style.scale = 1;
    document.getElementById("alertClose").focus();

}

function addContact(){
    nc = document.getElementById("newContact").value;
    document.getElementById("newContact").value = "";
    if(nc=="") return;
    for(t = 0; t<contacts.length; t++)
        if(contacts[t] == nc){
            showAlert("Contact already exists")
            return;
        }
    ws.send(JSON.stringify({sender: usernm, token: tkn, type:"userExist", username: nc}));
}

function formatDate(millis){
    let dt = new Date(millis);
    let day = String(dt.getDate()).padStart(2, '0');
    let month = String(dt.getMonth()+1).padStart(2, '0');
    let year = dt.getFullYear();
    return `${day}/${month}/${year}`;
}

function formatTime(millis){
    let dt = new Date(millis);
    let hr = String(dt.getHours()).padStart(2, '0');
    let mn = String(dt.getMinutes()).padStart(2, '0');
    let m = 'am'
    if(hr >= 12){
        m = 'pm'
        if(hr!=12)
            hr = hr - 12;
    }
    else{
        if(hr==0)
            hr = 12;
    }
        
    return `${hr}:${mn} ${m}`;
}

function showChat(e){
    let name = e.target.id;
    if(name==currChat)
        return;
    currChat = name;
    mainRender();
}

const ws = new WebSocket("ws://"+window.location.hostname+":50");

ws.onopen = ()=>{
    ws.send(JSON.stringify({type:"init", username: usernm, token: tkn}));
}

ws.onmessage = (res)=>{
    res = JSON.parse(res.data);
    if(res.type=="message"){
        res.date = formatDate(res.time)
        res.time = formatTime(res.time);
        let user = res.sender==usernm? res.receiver: res.sender;
        contacts = contacts.filter((e)=>{return e != user});
        contacts = [user, ...contacts];
        res.author = res.sender;
        if(res.sender==usernm)
            res.type = "send";
        else
            res.type = "receive";
        if(!userChats[user])
            userChats[user] = [];
        userChats[user].push(res);
        idChat[res.msg_id] = res;
            
        mainRender();
    }
    else if(res.type=="status"){
        idChat[res.msg_id].status = res["status"];
        mainRender();
    }

    else if(res.type=="userExist"){
        if(res.status==1){
            contacts=[res.username, ...contacts];
            userChats[res.username] = [];
            mainRender();
        }
        else{
            showAlert("Username does not exist");
        }
    }
}

function sendMessage(){
    let msg = document.getElementById("messageInput").value;
    let rec = currChat;
    let res = {sender: usernm, token: tkn, type:"message", receiver: rec, message: msg, time: Date.now(), msg_id: Date.now()+usernm, status:0};
    ws.send(JSON.stringify(res));
    res.date = formatDate(res.time);
    res.time = formatTime(res.time);
    res.author = usernm;
    res.type = "send";
    if(!userChats[rec])
        userChats[rec] = []
    userChats[rec].push(res);
    idChat[res.msg_id] = res;
    contacts = contacts.filter((e)=>{return e != rec});
    contacts = [rec, ...contacts];
    mainRender()
    return 1;
}

function mainRender(){
    let args = {"contacts":contacts, contactsAction:"showChat(event)", addAction: "addContact()", name: currChat, chats: userChats[currChat], sendAction: "sendMessage()"};
    let el = new Home(args);
    document.body.innerHTML = el.render();
    return 1;
}

mainRender();