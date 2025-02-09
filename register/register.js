const form = document.getElementById("registerForm");

let sbtn = document.getElementById("submit")

sbtn.addEventListener("click",(event)=>{
    event.preventDefault();
    let formData = new FormData(form);
    let formValues = Object.fromEntries(formData.entries())
    $.ajax({
        url:"register.py",
        type:"POST",
        data: formValues,
        datatype: "json",
        success: (res)=>{
            res = JSON.parse(res)
            if(res.status == "failed"){
                alert(res.message);
                return
            }
            alert("Registration success");
            window.location.href = "../login/"
        }
    })
})