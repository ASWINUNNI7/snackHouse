from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout,authenticate
from .models import Client,Snacks,Order,Contact,Otp,Tables,BookTable
import random
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
def index(request):
  return render(request,'nouser.html')

def about(request):
  return render(request,'about.html')

def contact(request):
  if request.method=='POST':
     name=request.POST['name']
     username=request.POST['username']
     message=request.POST['message']
     newcontact=Contact(name=name,username=username,message=message)
     newcontact.save()
     messages.info(request,'Message is saved,our staff will contact you shortly')
  return render(request,'contact.html')

def login_page(request):
  return render(request,'login.html')

def register_page(request):
  if request.method == 'POST':
     name=request.POST['name']
     mobile=request.POST['mobile']
     username=request.POST['username']
     password1=request.POST['password1']
     password2=request.POST['password2']
     if password1==password2:
        if User.objects.filter(username=username).exists():
           messages.info(request,'email has been taken')
        else:
           user=User.objects.create_user(username=username,password=password1,first_name=name)
           client=Client(name=name,mobile=mobile,username=username,password=password1)
           code=generate_code()
           newOtp=Otp(otp=code,email=username)
           newOtp.save()
           user.save()
           client.save()
           send_email(username,code)
           messages.info(request,'otp send to your given mail')
           login(request,user)
           return redirect('otpPage')
     else:
        messages.info(request,'password not match')
        return redirect('register')
  return render(request, 'register.html')

def login_view(request):
   if request.method == 'POST':
      username=request.POST['username']
      password=request.POST['password']
      user=authenticate(username=username,password=password)
      if user is not None:
         login(request,user)
         return redirect('home')
      else:
         message='invalid credentials'
         messages.info(request,message)
   return render(request, 'login.html')

def logout_view(request):
   logout(request)
   return redirect('index')

def home(request):
   return render(request,'home.html')

def habout(request):
   return render(request,'habout.html')

def hcontact(request):
   if request.method=='POST':
     name=request.POST['name']
     username=request.POST['username']
     message=request.POST['message']
     newcontact=Contact(name=name,username=username,message=message)
     newcontact.save()
     messages.info(request,'Message is saved,our staff will contact you shortly')
   return render(request,'hcontact.html')

def food(request):
   foods=Snacks.objects.all()
   return render(request,'food.html',{'foods':foods})

def orderdetails(request):
   name=request.user.username
   cname=request.user.first_name
   order=Order.objects.filter(name=name)
   client=Client.objects.filter(name=cname)
   random_num=random.randint(10000,99999)
   booktable=BookTable.objects.get(name=name)
   total=0.0
   for item in order:
         total=total+item.total_price
   if request.method == 'POST':
        if 'ok_pay' in request.POST:  
            order.delete() 
            booktable.delete() 
            total=str(total)
            send_mail(
            'Bill Payment',
            'Your bill of Rs. '+total+' has been successfully paid \n Visit Again!!',
            from_email='AL Cafe Arabia <'+settings.EMAIL_HOST_USER+'>',
            recipient_list=[name],
            fail_silently=False
        )
            messages.success(request, "Payment successful!")
            return redirect('home')  
        
        elif 'update_order' in request.POST: 
            return redirect('cart')  
   return render(request,'order_details.html',{'orders':order,'clients':client
                                               ,'rand':random_num, 'total': total})


def cancelOrder(request):
   name=request.user.username
   food=request.POST['foodname']
   order=Order.objects.get(name=name,food_name=food)
   addsize=order.quantity
   snack=Snacks.objects.get(food_name=food)
   snack.quantity=snack.quantity+addsize
   snack.save()
   order.delete()
   return HttpResponseRedirect(reverse('cart'))

def cancelAllorder(request):
   name=request.user.username
   orders=Order.objects.filter(name=name)
   for order in orders:
      addsize=order.quantity
      food=order.food_name
      snack=Snacks.objects.get(food_name=food)
      snack.quantity=snack.quantity+addsize
      snack.save()
      order.delete()
   messages.info(request,'All orders cancelled')
   return redirect(reverse('cart'))

def updateOrder(request):
   name=request.user.username
   foodname=request.POST['foodname']
   price=Snacks.objects.get(food_name=foodname).price
   size=Snacks.objects.get(food_name=foodname).quantity
   order=Order.objects.get(name=name,food_name=foodname)
   max=size+order.quantity
   return render(request,'updateorder.html',{'food':order,'price':price,'size':max})

def updateOrderFood(request):
   name=request.user.username
   fname=request.POST['foodname']
   quantity=request.POST['fquantity']
   quantity=int(quantity)
   order=Order.objects.get(food_name=fname,name=name)
   snack=Snacks.objects.get(food_name=fname)
   if order.quantity<quantity:
      size=quantity-order.quantity
      snack.quantity=snack.quantity-size
   else:
      size=order.quantity-quantity
      snack.quantity=snack.quantity+size
   order.quantity=quantity
   totalprice=quantity*snack.price
   order.total_price=totalprice
   snack.save()
   order.save()
   return redirect(reverse('cart'))

def otpPage(request):
   if request.method == 'POST':
      email=request.POST['mail']
      otp=request.POST['otp']
      otp=int(otp)
      details=Otp.objects.get(email=email)
      generateOtp=details.otp
      if otp==generateOtp:
         details.delete()
         messages.info(request,'successfully registered')
         return render(request,'home.html')
      else :
         messages.info(request,'invalid otp')
   return render(request,'otp.html')

def cart(request):
   name=request.user.username
   total=0.0
   if Order.objects.filter(name=name):
      orders=Order.objects.filter(name=name)
      for order in orders:
         total=total+order.total_price
   else:
      orders='none'
   return render(request,'cart.html',{'orders':orders, 'total': total})

def indianFood(request):
   email=request.user.username
   if BookTable.objects.filter(name=email).exists():
      bookTable=BookTable.objects.get(name=email)
   else:
      bookTable='none'
   foods=Snacks.objects.filter(category='Indian')
   return render(request,'indian.html',{'foods':foods,'table':bookTable})

def nonIndianFood(request):
   foods=Snacks.objects.filter(category='Indian')
   return render(request,'nonIndian.html',{'foods':foods})

def arabianFood(request):
   email=request.user.username
   if BookTable.objects.filter(name=email).exists():
      bookTable=BookTable.objects.get(name=email)
   else:
      bookTable='none'
   foods=Snacks.objects.filter(category='Arabian')
   return render(request,'arabian.html',{'foods':foods,'table':bookTable})

def nonArabianFood(request):
   foods=Snacks.objects.filter(category='Arabian')
   return render(request,'nonArabian.html',{'foods':foods})

def europeanFood(request):
   email=request.user.username
   if BookTable.objects.filter(name=email).exists():
      bookTable=BookTable.objects.get(name=email)
   else:
      bookTable='none'
   foods=Snacks.objects.filter(category='European')
   return render(request,'european.html',{'foods':foods,'table':bookTable})

def nonEuropeanFood(request):
   foods=Snacks.objects.filter(category='European')
   return render(request,'nonEuropean.html',{'foods':foods})

def drinks(request):
   email=request.user.username
   if BookTable.objects.filter(name=email).exists():
      bookTable=BookTable.objects.get(name=email)
   else:
      bookTable='none'
   foods=Snacks.objects.filter(category='Drinks')
   return render(request,'drinks.html',{'foods':foods,'table':bookTable})

def nonDrinks(request):
   foods=Snacks.objects.filter(category='Drinks')
   return render(request,'nonDrinks.html',{'foods':foods})

def indianOrder(request):
   url='indianFood'
   order(request,url)
   return redirect(reverse(url))



def arabianOrder(request):
   url='arabianFood'
   order(request,url)
   return redirect(reverse(url))

def europeanOrder(request):
   url='europeanFood'
   order(request,url)
   return redirect(reverse(url))

def drinksOrder(request):
   url='drinks'
   order(request,url)
   return redirect(reverse(url))

def otpBack(request):
   username=request.user.username
   user=User.objects.get(username=username)
   client=Client.objects.get(username= username)
   otp=Otp.objects.get(email=username)
   logout(request)
   otp.delete()
   client.delete()
   user.delete()
   return redirect(reverse('register'))
   
def tables(request):
   email=request.user.username
   name=request.user.first_name
   if request.method=='POST':
      table=request.POST['table']
      members=request.POST['members']
      members=int(members)
      if table == 'default':
         messages.info(request,'Choose a table')
      else:
         tablesize=Tables.objects.get(table_name=table).quantity
         if members>tablesize:
            messages.info(request,'Members are higher than the selected seats')
         else:
            bookTable=BookTable(name=email,table=table,members=members)
            bookTable.save()
            send_mail(
                  'Table Booking',
                  'Hi '+name+','+'\nYour Table-'+table+' has been booked',
                  from_email='AL Cafe Arabia <'+settings.EMAIL_HOST_USER+'>',
                  recipient_list=[email],
                  fail_silently=False
            )
            return redirect('home')
   btables = BookTable.objects.all().values_list('table', flat=True)  
   tablelist = Tables.objects.exclude(table_name__in=btables)       
   tlist = list(tablelist)  
   return render(request,'tables.html',{'tables':tlist})

def tableDetails(request):
   email=request.user.username
   if BookTable.objects.filter(name=email).exists():
      bookTable1=BookTable.objects.get(name=email)
   else:
      bookTable1='none'
   return render(request,'table_details.html',{'tables':bookTable1})

def cancelTable(request):
   username=request.user.username
   fname=request.user.first_name
   bookTable=BookTable.objects.get(name=username)
   table=bookTable.table
   if Order.objects.filter(name=username).exists():
      messages.info(request,'Pay/cancel existing orders to cancel table')
      return redirect('tableDetails')
   send_mail(
               'Table Cancelled',
               'Hi '+fname+','+'\nYour Table-'+table+' has been cancelled',
               from_email='AL Cafe Arabia <'+settings.EMAIL_HOST_USER+'>',
               recipient_list=[username],
               fail_silently=False
         )
   bookTable.delete()
   return redirect('home')
   
def update_credentials(request):
    requser=request.user.username
    client=Client.objects.get(username=requser)
    clientmob=client.mobile
    if request.method == 'POST':
        current_user = request.user
        name = request.POST['name']
        mobile = request.POST['mobile']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username=username).exclude(pk=current_user.pk).exists():
                messages.info(request, 'Username has been taken')
            else:
                user = User.objects.get(pk=current_user.pk)
                user.first_name = name
                user.username = username
                user.set_password(password1)
                user.save()

                client = Client.objects.get(username=current_user.username)
                client.name = name
                client.mobile = mobile
                client.username = username
                client.password = password1
                client.save()
                messages.info(request, 'Your credentials have been updated successfully')
                return redirect('index')  
            messages.info(request, 'Passwords do not match')
    return render(request, 'update_credentials.html',{'mob':clientmob})
 
def profileview(request):
    current_user = request.user
    client = Client.objects.get(username=current_user.username)
    clientmob = client.mobile
    if request.method == 'GET':
        name = current_user.first_name
        username = current_user.username
        email = current_user.email
        mobile = clientmob
    return render(request, 'profileview.html', {'name': name, 'username': username, 'email': email, 'mobile': mobile})
#--------------------------------------------------Helper functions------------------------------------------------------------------

def send_email(email,otp):
   otp=str(otp)
   send_mail(
            'VERIFICATION CODE',
            'Your otp for this session:- AC-'+otp,
            from_email='AL Cafe Arabia <'+settings.EMAIL_HOST_USER+'>',
            recipient_list=[email],
            fail_silently=False
        )

def generate_code():
   code=random.randint(1000,9999)
   return code

def order(request,url):
   food_name=request.POST['foodname']
   food_image=request.POST['foodimg']
   category=request.POST['fcategory']
   fquantity=request.POST['fquantity']
   fquantity=float(fquantity)
   fprice=request.POST['fprice']
   fprice=float(fprice)
   name=request.user.username
   table=BookTable.objects.get(name=name).table
   members=BookTable.objects.get(name=name).members
   totalPrice=fprice*fquantity
   newOrder=Order(name=name,food_name=food_name,quantity=fquantity,table_name=table,
                  members=members,total_price=totalPrice,food_image=food_image,category=category)
   checkOrder=Order.objects.filter(name=name,food_name=food_name)
   food=Snacks.objects.get(food_name=food_name)
   food.quantity=food.quantity-fquantity
   if checkOrder.exists():
      messages.info(request,'already you ordered this item,please update it')
   else:
      food.save()
      newOrder.save()
      messages.info(request,'item added to cart')

