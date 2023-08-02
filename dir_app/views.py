from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Room, Topic
from .forms import RoomForm

# rooms =[
#     {'id':1,'name':'Barbie fans'},
#     {'id':2,'name':'Ken fans'},
#     {'id':1,'name':'Fans of both'},

# ]

def home(request):
    q = request.GET.get('q') if request.GET.get('q')!=None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    topics=Topic.objects.all()
    room_count = rooms.count()

    content_dict={'rooms':rooms, 'topics':topics, 'room_count':room_count}
    return render(request, 'dir_app/home.html', content_dict) 

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User doesnot exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    content_dict= {}
    return render(request, 'dir_app/login_register.html',content_dict)

def room(request,pk):
    room = Room.objects.get(id=pk)
    content_dict={'room':room}
    return render(request, 'dir_app/room.html',content_dict)

def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    content_dict={'form':form}
    return render(request,'dir_app/room_form.html',content_dict)

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.method =='POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    content_dict = {'form':form}
    return render(request, 'dir_app/room_form.html', content_dict)

def deleteRoom(request,pk):
    room =Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'dir_app/delete.html', {'obj':room})

# Create your views here.
 