from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout,authenticate
from .models import Client,Snacks,Tables,Order,Payment,Contact,Otp
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
         messages.info(request,'Logged in successfully')
         return redirect('home')
      else:
         message='invalid credentials'
         messages.info(request,message)
   return render(request, 'login.html')

def logout_view(request):
   logout(request)
   messages.info(request,'Logged out successfully')
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



def orderFood(request):
   name=request.POST['fname']
   food_name=request.POST['foodname']
   table=request.POST['table']
   members=request.POST['members']
   members=int(members)
   quantity=request.POST['quantity']
   price=request.POST['tprice']
   if table=='none':
      messages.info(request,'Choose a table to continue')
      return HttpResponseRedirect(reverse('food'))
   elif checkorder(table,food_name,name):
      if Order.objects.filter(name=name,table_name=table).exists(): 
         checktable(request,name,table,members,food_name,price,quantity)
         return HttpResponseRedirect(reverse('ordertable'))
      else:
         if Order.objects.filter(table_name=table).exists():
            messages.info(request,'This table is already reserved by other')
            return HttpResponseRedirect(reverse('food'))
         else:
            checktable(request,name,table,members,food_name,price,quantity)
            return HttpResponseRedirect(reverse('food'))
   else:
      messages.info(request,'You had already booked this item for the table')
      return HttpResponseRedirect(reverse('food'))

def ordertable(request):
   name=request.user.first_name
   if Order.objects.filter(name=name).exists():
      orders=Order.objects.filter(name=name)
   else:
      orders='none'
   return render(request,'ordertable.html',{'details':orders})

def payment(request):
      fname=request.POST['fname']
      userorder=Order.objects.filter(name=fname).values_list('total_price',flat=True)
      userorder=list(userorder)
      amount=0
      for order in userorder:
         amount=order+amount
         newPayment=Payment(name=fname,total_amount=amount)
      newPayment.save()
      return HttpResponseRedirect(reverse('confirm'))

def orderdetails(request):
   name=request.user.first_name
   order=Order.objects.filter(name=name)
   client=Client.objects.filter(name=name)
   payments=Payment.objects.filter(name=name)
   random_num=random.randint(10000,99999)
   return render(request,'order_details.html',{'orders':order,'clients':client
                                               ,'payments':payments,'rand':random_num})

def confirmMessage(request):
   name=request.user.first_name
   userpayment=Payment.objects.filter(name=name)
   return render(request,'payment_alert.html',{'payments':userpayment})

def cancelOrder(request):
   name=request.user.username
   food=request.POST['foodname']
   order=Order.objects.get(name=name,food_name=food)
   addsize=order.quantity
   snack=Snacks.objects.get(food_name=food)
   snack.quantity=snack.quantity+addsize
   snack.save()
   order.delete()
   messages.info(request,'order cancelled')
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


def cancelPayment(request):
   name=request.user.first_name
   payment=Payment.objects.filter(name=name)
   payment.delete()
   messages.info(request,'payment cancelled')
   return HttpResponseRedirect(reverse('ordertable'))

def confirmPayment(request):
   name=request.user.first_name
   payment=Payment.objects.filter(name=name)
   order=Order.objects.filter(name=name)
   payment.delete()
   order.delete()
   messages.info(request,'paid successfully')
   return HttpResponseRedirect(reverse('home'))

def updateOrder(request):
   name=request.user.username
   foodname=request.POST['foodname']
   price=Snacks.objects.get(food_name=foodname).price
   size=Snacks.objects.get(food_name=foodname).quantity
   order=Order.objects.get(name=name,food_name=foodname)
   max=size+order.quantity
   return render(request,'updateOrder.html',{'food':order,'price':price,'size':max})

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
   messages.info(request,'order updated')
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
   if Order.objects.filter(name=name):
      orders=Order.objects.filter(name=name)
   else:
      orders='none'
   return render(request,'cart.html',{'orders':orders})

def indianFood(request):
   foods=Snacks.objects.filter(category='Indian')
   return render(request,'indian.html',{'foods':foods})

def arabianFood(request):
   foods=Snacks.objects.filter(category='Arabian')
   return render(request,'arabian.html',{'foods':foods})

def europeanFood(request):
   foods=Snacks.objects.filter(category='European')
   return render(request,'european.html',{'foods':foods})

def drinks(request):
   foods=Snacks.objects.filter(category='Drinks')
   return render(request,'drinks.html',{'foods':foods})

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
   client=Client.objects.get(username=username)
   otp=Otp.objects.get(email=username)
   logout(request)
   otp.delete()
   client.delete()
   user.delete()
   return redirect(reverse('register'))
   

#--------------------------------------------------Helper functions------------------------------------------------------------------
def checkorder(table,food,name):
   order=Order.objects.filter(table_name=table,food_name=food,name=name)
   if order.exists():
      return False
   else:
      return True
   
def checktable(request,name,table,members,food,price,quantity):
   table_quantity=Tables.objects.filter(table_name=table).values_list('quantity',flat=True)
   for tabquant in table_quantity:
      tabquant=int(tabquant)
      if members<=tabquant:
         totalprice=float(price)*int(quantity)
         oldorder=Order.objects.filter(name=name,food_name=food,table_name=table)
         oldorder.delete()
         updateorder=Order(name=name,food_name=food,table_name=table,members=members
                           ,quantity=quantity,total_price=totalprice)
         updateorder.save()
         messages.info(request,'order successfully')
      else:
         messages.info(request,'Members are higher than the reserved seat')

def send_email(email,otp):
   otp=str(otp)
   send_mail(
            'VERIFICATION CODE',
            'Your otp for this session:- AC-'+otp,
            settings.EMAIL_HOST_USER,  
            [email],
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
   table='T11'
   members=1
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
      messages.info(request,'added to cart successfully')

def update_credentials(request):
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

    return render(request, 'update_credentials.html')
 