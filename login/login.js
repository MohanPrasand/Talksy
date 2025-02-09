let sbtn = document.getElementById("submit")
let user = document.getElementById("username")
let passw = document.getElementById("pswd")
let err = document.getElementById("error")
let p = 1;

sbtn.addEventListener("click",(event) =>{
    event.preventDefault();

    $.ajax({
        url:"login.py",
        type: "POST",
        data: {username: user.value, password: passw.value},
        datatype: "json",
        success: (res) => {
                res = JSON.parse(res);
                p = res;
                if(res.status == "failed"){
                    err.innerHTML = res.message;
                }
                else{
                    sessionStorage.setItem("username", user.value);
                    sessionStorage.setItem("token", res.token);
                    window.location.href = "../chat";
                }
            },
        error: (res) => {
            err.innerHTML = res;
        }
    })

})