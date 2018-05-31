from __future__ import unicode_literals
from django.db import models
import bcrypt
import re

class UserManager(models.Manager):
    def register(self, name, email, password, passwordc, number, admin):
        errors = []
        if(password != passwordc):
            errors.append("Password fields don't match")
        if(len(password) > 7): #check if password is long enough
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        else:
            errors.append('Password must be at least 8 characters long')
        if(number and (len(number) < 7)):
            errors.append('Phone number must be at least 7 digits long, if supplied')
        if not (re.search(r'^[^.@]+@[^.@]+\.[^.@]+$', email)): #check valid email format
            errors.append('Email is not in a valid format. The correct format is myemail@somewhere.something')
        if not (re.search(r'^[a-zA-Z][a-zA-Z ]+$', name)): #check name to make sure its made up of at least 2 letters, and only letters
            errors.append('Name must contain at least 2 letters. Non-letter characters are not allowed')
        myprofile = Users.userManager.filter(email=email)
        if myprofile :
            valid = False
            errors.append('That Email address is already registered')

        if (len(errors) == 0):
            Users.userManager.create(name=name, email=email, password=password, number=number, admin=admin)
            myprofile = Users.userManager.get(email=email)
            return {'UserId': int(myprofile.id), 'UserName' : str(myprofile.name), 'Admin': admin}
        else:
            return {'fail': errors}


    def login(self, email, password):
        myprofile = Users.userManager.filter(email=email).values()
        if not myprofile:
            return {'fail' : 'That email has not been registered yet'}
        elif bcrypt.hashpw(password.encode(), myprofile[0]['password'].encode()) != myprofile[0]['password'].encode():
            return {'fail' : 'Incorrect password'}
        return {'UserId' : myprofile[0]['id'], 'UserName' : myprofile[0]['name'], 'Admin' : myprofile[0]['admin']}

    def remove(self, id, myid, admin):
        if(int(myid) == int(id)) or (admin):
            c = Users.userManager.filter(id=id)
            c.delete()
            return {'success': True}
        else:
            return {'fail' : 'Cannot remove account, you are not this user or an admin'}

class Users(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    number = models.CharField(max_length=15)
    admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    userManager = UserManager()
    objects = UserManager()

class PetManager(models.Manager):
    def register(self, name, species, info, user, pic_url=None):
        errors = []
        if len(name) < 1 :
            errors.append('New animal needs a name')
        if len(species) < 1 :
            errors.append('New animal needs a species')
        if len(info) < 30 :
            errors.append('Animal information is too short. Must be at least 30 characters long.')
        if not user :
            errors.append('New animal must have a user')
        if (len(errors) == 0):
            Pets.petManager.create(name=name, species=species, info=info, pic_url=pic_url, adopted=False, approved=False, user=user)
            return {'success': name}
        else:
            return {'fail': errors}

    def update(self, id, name, species, info, pic_url, userId, admin):
        animal = Pets.petManager.get(id=id)
        if animal:
            if (userId == animal.id or admin):
                fields = []
                errors = []
                if name:
                    fields.append('name')
                    animal.name = name
                    if len(name) < 1 :
                        errors.append('The animal needs a name')
                if species:
                    fields.append('species')
                    animal.species = species
                    if len(species) < 1 :
                        errors.append('The animal needs a species')
                if info:
                    fields.append('info')
                    animal.info = info
                    if len(info) < 30 :
                        errors.append('The animal\'s information is too short. Must be at least 30 characters long.')
                fields.append('pic_url')
                animal.pic_url = pic_url
                if (len(errors) == 0):
                    animal.save(update_fields=fields)
                    return {'success': animal.name}
                else:
                    return {'fail': errors}
            else:
                return {'fail': "You are not authorized to make changes to that pet"}
        else:
            return {'fail': "That pet wasn't found"}

    def approve(self, id):
        animal = Pets.petManager.get(id=id)
        if animal:
            animal.approved = True
            animal.save()
            return {'success': animal.name+' Approved!'}
        else:
            return {'fail': "That pet wasn't found"}

    def adopt(self, id):
        animal = Pets.petManager.get(id=id)
        if animal:
            animal.adopted = True
            animal.save()
            return {'success': animal.name+' has been adopted!'}
        else:
            return {'fail': "That pet wasn't found"}

    def unadopt(self, id):
        animal = Pets.petManager.get(id=id)
        if animal:
            animal.adopted = False
            animal.save()
            return {'success': animal.name+' has been put back in the shelter'}
        else:
            return {'fail': "That pet wasn't found"}

    def adoptable(self):
        animals = Pets.petManager.filter(adopted=False, approved=True)
        petList = []
        for animal in animals:
            petList.append({
                'id': animal.id,
                'name': animal.name,
                'species': animal.species,
                'info': animal.info
            })
        return animals

    def deletePet(self, id, userid, admin):
        animal = Pets.petManager.filter(id=id)
        if len(animal) > 0:
            if (userid == animal[0].user) or (admin == True):
                name = animal[0].name
                animal.delete()
                return {'success': name+' removed'}
            else:
                return {'fail': "You are not allowed to remove that animal unless you are the submitter or an Admin"}
        else:
            return {'fail': "That pet wasn't found"}


    def adopted(self):
        animals = Pets.petManager.filter(adopted=True).order_by('-created_at')
        petList = []
        for animal in animals:
            petList.append({
                'id': animal.id,
                'name': animal.name,
                'species': animal.species,
                'info': animal.info
            })
        return animals

    def pending_approval(self):
        animals = Pets.petManager.filter(approved=False).order_by('-created_at')
        petList = []
        for animal in animals:
            petList.append({
                'id': animal.id,
                'name': animal.name,
                'species': animal.species,
                'info': animal.info
            })
        return animals



class Pets(models.Model):
    name = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    info = models.CharField(max_length=255)
    pic_url = models.CharField(max_length=255, default=None)
    adopted = models.BooleanField(default=None)
    approved = models.BooleanField(default=None)
    user = models.ForeignKey(Users, related_name="Pets", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True) # When pet was added to DB
    updated_at = models.DateTimeField(auto_now_add=True)
    petManager = PetManager()
    objects = PetManager()
