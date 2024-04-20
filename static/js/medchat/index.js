console.log('You are at Index.js ')

document.querySelector("#roomInput").focus()

//Submit if user presses the enter keyup
document.querySelector("#roomInput").onkeyup=function(e){
    if(e.keyCode===13){
        //13 represents enter key 
        document.querySelector("#roomSubmit").click();
    }
}

//Redirect to room entered 
document.querySelector('#roomSubmit').onclick=function(){
    let roomName=document.querySelector("#roomInput").value;
    console.log(roomName)
    window.location.pathname="medchat/"+roomName + "/"
}

//Redirect also for to room selection 
document.querySelector("#roomSelect").onchange=function(){
    let roomName=document.querySelector("#roomSelect").value.split(" (")[0];
    console.log(roomName)
    window.location.pathname="medchat/"+roomName + "/";
}