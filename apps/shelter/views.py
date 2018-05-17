from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Users, Pets

def index(request):
    return render(request, 'shelter/index.html')

def new(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        passwordc = request.POST['passwordc']
        number = request.POST['phone']
        admin = ( request.POST.get('admin', '0') == '1' )
        result = Users.userManager.register(name, email, password, passwordc, number, admin)
        if 'UserId' in result:
            messages.success(request, 'You registered succesfully '+result['UserName']+'!')
            request.session['id'] = result['UserId']
            request.session['name'] = result['UserName']
            request.session['admin'] = result['Admin']
            return redirect('/')
        for error in result['fail']:
            messages.warning(request, error) #If register not successful, flash error message
        return redirect('/register')
    else:
        return render(request, 'shelter/loginreg.html')

def profile(request, id):
    profile = Users.userManager.filter(id=id)
    if len(profile) > 0:
        context = {
            'id': profile[0].id,
            'name': profile[0].name,
            'number': profile[0].number,
            'email': profile[0].email,
            'admin': profile[0].admin,
            'created_at': profile[0].created_at
        }
        return render(request, 'shelter/show_user.html', context)
    else:
        messages.warning(request, 'That user id does not exist')
        return redirect('/')

def showPet(request, id):
    pet = Pets.petManager.filter(id=id)
    if len(pet) > 0:
        context = {
            'id': pet[0].id,
            'name': pet[0].name,
            'species':pet[0].species,
            'info': pet[0].info,
            'pic': pet[0].pic_url
        }
        return render(request, 'shelter/show_pet.html', context)
    else:
        messages.warning(request, 'That animal id does not exist')
        return redirect('/pets')

def logout(request):
    request.session['id'] = None
    request.session['name'] = None
    request.session['admin'] = None
    messages.success(request, 'You have logged out, goodbye!')
    return redirect('/')

def login(request):
    if request.method == 'POST':
        result = Users.userManager.login(request.POST['email'], request.POST['password'])
        if 'UserId' in result:
            request.session['id'] = result['UserId']
            request.session['name'] = result['UserName']
            request.session['admin'] = result['Admin']
            messages.success(request, 'You logged in succesfully '+result['UserName']+'!')
        else:
            messages.warning(request, result['fail']) #If login not successful, flash error message
            return render(request, 'shelter/loginreg.html')
    else:
        if request.session.get('id'):
            messages.warning(request, 'You are already logged in')
        else:
            return render(request, 'shelter/loginreg.html')
    return redirect('/')

def petList(request):
    context = {'animals': Pets.petManager.adoptable()}
    return render(request, 'shelter/pets.html', context)

def adopted(request):
    context = {'animals': Pets.petManager.adopted()}
    return render(request, 'shelter/pets_adopted.html', context)

def pending_approval(request):
    if request.session.get('admin'):
        context = {'animals': Pets.petManager.pending_approval()}
        return render(request, 'shelter/pets_pending.html', context)
    else:
        return redirect('/pets')

def users(request):
    if request.session.get('admin'):
        context = {
            'users': Users.userManager.filter(admin=False).order_by('-created_at'),
            'admins': Users.userManager.filter(admin=True).order_by('-created_at')
        }
        return render(request, 'shelter/users.html', context)
    else:
        return redirect('/')

def deleteUser(request, id):
    if request.method == 'POST':
        userid = request.session.get('id')
        admin = request.session.get('admin')
        result = Users.userManager.remove(id, userid, admin)
        if 'success' in result:
            messages.success(request, 'Account deletion successful')
            if (int(userid) == int(id)):
                return redirect('/logout')
        else:
            messages.warning(request, 'Something went wrong with the delete')
    return redirect('/users')

def approvePet(request, id):
    if (request.method == 'POST') and (request.session.get('admin') == True):
        result = Pets.petManager.approve(id)
        if 'success' in result:
            messages.success(request, result['success'])
        else:
            messages.warning(request, result['fail'])
    return redirect('/pets/admin')

def deletePet(request, id):
    if request.method == 'POST':
        userid = request.session.get('id')
        admin = request.session.get('admin')
        route = request.POST['route']
        result = Pets.petManager.deletePet(id, userid, admin)
        if 'success' in result:
            messages.success(request, result['success'])
        else:
            messages.warning(request, result['fail'])
        if route == 'admin':
            return redirect('/pets/admin')
        if route == 'adopted':
            return redirect('/pets/adopted')
    return redirect('/pets')

def adoptPet(request, id):
    if request.method == 'POST' and request.session.get('admin') == True:
        result = Pets.petManager.adopt(id)
        if 'success' in result:
            messages.success(request, result['success'])
        else:
            messages.warning(request, result['fail'])
    return redirect('/pets')

def unadoptPet(request, id):
    if request.method == 'POST' and request.session.get('admin') == True:
        result = Pets.petManager.unadopt(id)
        if 'success' in result:
            messages.success(request, result['success'])
        else:
            messages.warning(request, result['fail'])
    return redirect('/pets/adopted')

def registerPet(request):
    if request.method == 'POST':
        name = request.POST['name']
        species = request.POST['species']
        info = request.POST['info']
        pic_url = request.POST['pic']
        result = Pets.petManager.register(name, species, info, Users.userManager.get(id=request.session['id']), pic_url)
        if 'success' in result:
            messages.success(request, 'You submitted a new animal!')
            messages.success(request, name+' is awaiting admin approval')
            return redirect('/pets')
        for error in result['fail']:
            messages.warning(request, error) #If register not successful, flash error message
        return redirect('/pets/new')
    else:
        if request.session.get('id'):
            return render(request, 'shelter/new_pet.html')
        else:
            messages.warning(request, 'You must be logged in to submit a pet')
            return redirect('/pets')
