from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

from datetime import datetime, timedelta
from .models import Room,Message 

def index(request):
    rooms=Room.objects.all()
    return render(request,'medchat/index.html',{'rooms':rooms})


@login_required
def room_view(request, room_name):
    # Get or create the chat room object
    chat_room, created = Room.objects.get_or_create(name=room_name)

    # Fetch all messages associated with the room
    messages = Message.objects.filter(room=chat_room).order_by('timestamp')

    
    def group_messages_by_date(messages):
        grouped_messages = []
        current_date = None
        yesterday = None

        for message in messages:
            # Get the date of the message
            message_date = message.timestamp.date()

            # Get current date
            today = datetime.now().date()

            # Get yesterday's date
            if today:
                yesterday = today - timedelta(days=1)

            if message_date != current_date:
                if message_date == yesterday:
                    date_label = f"{message_date.strftime('%A')} (Yesterday)"
                elif message_date == today:
                    date_label = "Today"
                else:
                    date_label = message_date.strftime('%A, %d %B %Y')

                grouped_messages.append({'date_label': date_label, 'messages': []})
                current_date = message_date

            # Append the message to the last group
            grouped_messages[-1]['messages'].append(message)

        return grouped_messages


    # Group messages by date
    grouped_messages = group_messages_by_date(messages)

    # Prepare the context to pass to the template
    context = {
        'room_name': room_name,
        'grouped_messages': grouped_messages,  # Pass grouped messages to the template
        'room': chat_room,
        #'current_user': request.user,  # Pass the current user to the template
    }

    # Render the template with the context
    return render(request, 'medchat/room.html', context)
