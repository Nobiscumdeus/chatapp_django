import json
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Room
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room  # Import your Room model
from .models import Message
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist 
from asgiref.sync import async_to_sync




class ChatConsumer(AsyncWebsocketConsumer):
    active_users = set()  # Use a set to store active users

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ChatConsumer.active_users is None:
            ChatConsumer.active_users = []
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user=None #Newly added for authentication 
       
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        #self.room =Room.objects.get(name=self.room_name)
       
        # Fetch Room asynchronously
        self.room = await self.get_room(self.room_name)
        self.user=self.scope.get('user')
        # Add the user to the active users set
        self.active_users.add(self.user.username)

        # Send the updated user list to all clients
        await self.send_user_list_update()
        
       
        #Newly added for authentication 
        if self.user and self.user.is_authenticated:
            if not self.room:
                await self.close()
                return 
            await self.accept() #Proceed with the logic 
        else:
            await self.close()
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
    async def disconnect(self, close_code):
        #Remove the user from the list 
        self.active_users.remove(self.user.username)

        # Send the updated user list to all clients
        await self.send_user_list_update()

        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username=self.user.username
       
        rooms=self.room
        content=message
        username=self.scope['user'] ##---------------- Newly added ----------------------
        roomname = self.scope['url_route']['kwargs']['room_name'] ##------Newly added --------
       
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user':self.user.username, #Newly added as part of authentication 
                'message': message
            }
        )
        await self.create_message(username,roomname,content) ##---------- Newly added ---------
        #Message.objects.create(user=self.user,room=self.room,content=message) #Newly added for updated to message models
    
    
    async def send_user_list_update(self):
        # Send updated user list to all clients
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list_update',
                'user_list': list(self.active_users),
            }
        )

    async def user_list_update(self, event):
        await self.send(text_data=json.dumps(event))
        
        user_list = event['user_list']
        print("User list here",user_list)
        await self.send(text_data=json.dumps({
            'type': 'user_list_update',
            'user_list': user_list,
        }))
        


    async def chat_message(self, event):
        # Send the message back to the WebSocket
        await self.send(text_data=json.dumps(event))
    

    async def create_message(self, username, roomname, content):
        # Fetch the user instance asynchronously
        try:
            user = await sync_to_async(User.objects.get)(username=username)
        except User.DoesNotExist:
            # Handle the case where the user does not exist
            # For example, you can log an error or return an appropriate response
            return
        
        # Define a synchronous function to fetch the Room instance
        @sync_to_async
        def get_room_instance(room_name):
            try:
                return Room.objects.get(name=room_name)
            except ObjectDoesNotExist:
                return None  # Return None if room does not exist
        
        # Fetch the Room instance asynchronously
        room = await get_room_instance(roomname)
        
        if room is None:
            # Handle the case where the room does not exist
            # For example, you can log an error or return an appropriate response
            return
        
        # Define a synchronous function to create the Message instance
        @sync_to_async
        def create_message_instance(user, room, content):
            return Message.objects.create(user=user, room=room, content=content)
        
        # Create the Message instance asynchronously
        await create_message_instance(user, room, content)
        # You may choose to log the creation of the message or perform other actions here
          
    
    @database_sync_to_async
    def get_room(self, room_name):
        try:
            return Room.objects.get(name=room_name)
        except Room.DoesNotExist:
            return None
    

        
      