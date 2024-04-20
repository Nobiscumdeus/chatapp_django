console.log("Room.js")

console.log(currentUser)

const roomName=JSON.parse(document.getElementById('roomName').textContent);

let chatLog=document.querySelector("#chatLog");
let userListElement = document.querySelector('#userList');

let chatMessageInput=document.querySelector("#chatMessageInput");


let chatMessageSend=document.querySelector("#chatMessageSend");
let onlineUsersSelector=document.querySelector("#onlineUsersSelector");


function onlineUsersSelectorAdd(value){
    if(document.querySelector("option[value='" +value+ "']")) return;
    let newOption=document.createElement("option");
    newOption.value=value;
    newOption.innerHTML=value;
    onlineUsersSelector.appendChild(newOption);

}

function onlineUsersSelectorRemove(value){
    let oldOption=document.querySelector("option[value='" + value + "']");
    if(oldOption !== null) oldOption.remove();

}


//Focus chat message when a user opens the page 
chatMessageInput.focus();

//Submit if the user presses the enter key 
chatMessageInput.onkeyup=function(e){
    if(e.keyCode===13){
        //Enter key 
       
        chatMessageSend.click();
        
    }
};

//Clear the 'chatMessageInput' and forward the message 
chatMessageSend.onclick=function(){
    console.log("Send has been clicked automatically ")
  
    if(chatMessageInput.value.length===0)return;
    chatSocket.send(JSON.stringify({
        "message":chatMessageInput.value,
        
    }));
    chatMessageInput.value=""; 
}


//Making our WebSocket connection 
let chatSocket=null
function connect(){
    chatSocket=new WebSocket("ws://"+window.location.host + "/ws/chat/" + roomName + "/")
    
    

    chatSocket.onopen=function(e){
        console.log("Successfully connected to the web socket!!!");
    }

    chatSocket.onclose=function(e){
        console.log('WebSocket connection closed, reconnecting ...')
        setTimeout(function(){
            console.log("Reconnecting...");
            connect();
        },2000);
    }

    chatSocket.onmessage=function(e){
        const data=JSON.parse(e.data);
        console.log(data);

        switch(data.type){
            case "chat_message":
                displayChatMessage(data.message,data.user);
                break;
            case "user_list_update":
                const userList = data.user_list;
                if(userList){
                    console.log(userList)
                }else{
                    console.log("Nothing to show")
                }
                
                displayUserList(userList);
                break;

                
            default:
                console.error("Unknown message type!!!")
                break;
        }
        //Automatically scrolling chat to the bottom 
        chatLog.scrollTop=chatLog.scrollHeight;

    };

   
   
    function displayChatMessage(message, user) {
        var messageClass = user === currentUser ? "sender-message" : "receiver-message";
        var arrowClass = user === currentUser ? "arrow-right" : "arrow-left"; // Adjust arrow orientation based on message sender
        var htmlMessage = '<div class="message-box ' + messageClass + '">' +
            '<div class="sender-name">' + user + '</div>' +
            '<div class="message-content">' + message + '</div>' +
            '<div class="date">' + getFormattedDateTime() + '</div>' +
           // '<div class="arrow"></div>' + //Include the arrow class here 
            '<div class="arrow ' + arrowClass + '"></div>'
            '</div>';
        chatLog.innerHTML += htmlMessage;
        chatLog.scrollTop = chatLog.scrollHeight;
    }
    
    function displayUserList(userList) {
        // Clear existing user list
        //const userListElement = document.getElementById('userList');
        userListElement.innerHTML = '';
    
        // Add users to the list
        userList.forEach(function(user) {
            const listItem = document.createElement('li');
            listItem.textContent = user;
            userListElement.appendChild(listItem);
        });
    
        // Update select options (if needed)
        const selectElement = document.getElementById('onlineusersSelector');
        selectElement.innerHTML = '';
        userList.forEach(function(user) {
            const option = document.createElement('option');
            option.value = user;
            option.textContent = user;
            selectElement.appendChild(option);
        });
    }
    

    
    function getFormattedDateTime() {
        var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        
        var currentDate = new Date();
        var year = currentDate.getFullYear();
        var month = months[currentDate.getMonth()];
        var day = currentDate.getDate();
        var hours = currentDate.getHours();
        var minutes = currentDate.getMinutes();
        var ampm = hours >= 12 ? 'p.m.' : 'a.m.';
        hours = hours % 12;
        hours = hours ? hours : 12; // Handle midnight (0 hours)
        var formattedHours = (hours < 10 ? '0' : '') + hours; // Add leading zero if needed
        var formattedMinutes = (minutes < 10 ? '0' : '') + minutes; // Add leading zero if needed
        var formattedDateTime = month + ' ' + day + ', ' + year + ' ' + formattedHours + ':' + formattedMinutes + ' ' + ampm;
        return formattedDateTime;
    }
    
    chatSocket.onerror=function(err){
        console.log("Ooops!!! An error occurred  " + err.message);
        console.log("Closing Web socket ");
        chatSocket.close();
    }
};
connect();