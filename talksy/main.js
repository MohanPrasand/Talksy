window.addEventListener("mousemove",(e)=>{
    let x = e.clientX;
    let y = e.clientY;
    let d = document.createElement("DIV");
    d.id = "trail";
    d.style.left = x + "px";
    d.style.top = y + "px";
    document.getElementById("welcome").appendChild(d);
    setTimeout(2000, ()=>{
        document.getElementById("welcome").removeChild(d);
    })
})