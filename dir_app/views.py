from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
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
    room_messages= Message.objects.filter(Q(room__topic__name__icontains=q))

    content_dict={'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'dir_app/home.html', content_dict) 

def LoginPage(request):
    page ='login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower( )
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User doesnot exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    content_dict= {'page':page}
    return render(request, 'dir_app/login_register.html',content_dict)

def LogoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user =form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'an error occured during registration')
    return render(request, 'dir_app/login_register.html',{'form':form})

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages =room.message_set.all().order_by('-create')
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    content_dict={'room':room, 'room_messages':room_messages,"participants":participants}
    return render(request, 'dir_app/room.html',content_dict)

def userProfile(request,pk):
    user=User.objects.get(id=pk)
    content_dict={'user':user}
    return render(request, 'dir_app/profile.html',content_dict)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    content_dict={'form':form}
    return render(request,'dir_app/room_form.html',content_dict)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You not allowed here')

    if request.method =='POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    content_dict = {'form':form}
    return render(request, 'dir_app/room_form.html', content_dict)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room =Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You not allowed here')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'dir_app/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message =Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You not allowed here')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'dir_app/delete.html', {'obj':message})

# Create your views here.
 