let IP = "192.168.171.204"
    const ws = new WebSocket(`ws://${IP}:50`);
    let eastablished = false;
    let id=sessionStorage.getItem("username");
    let tkn = sessionStorage.getItem("token")
    document.getElementById("idno").innerText = id;

    function constructRow(data){
        let row = document.createElement("tr");
        row.innerHTML = `<td>${data.sender}</td><td>${data.receiver}</td><td>${data.message}</td><td>${data.msg_id}</td><td id="status">${data.status}</td>`;
        row.id = data.msg_id;
        return row;
    }

    ws.onopen = (event) => {
        req = {type:"init",username:id, token:tkn}
        ws.send(JSON.stringify(req))
    }

    
    ws.onmessage = (event)=>{
        let data = JSON.parse(event.data)
        if(data.type == "message"){
            document.getElementById("msg").appendChild(constructRow(data));
        }
        else if(data.type == "status"){
            let r = document.getElementById(data.msg_id);
            r = r.querySelector("#status");
            r.innerText = data.status;
        }
    }
    
    
    document.getElementById("send").addEventListener("click",(event)=>{
        rec = document.getElementById("rec_id").value;
        msg = document.getElementById("s_msg").value;
        
        res = {type:"message",sender:id, receiver:rec, message:msg, msg_id: Date.now()+id, time: Date.now(), token:tkn, status:0};
        ws.send(JSON.stringify(res));
        document.getElementById("msg").appendChild(constructRow(res));
    });