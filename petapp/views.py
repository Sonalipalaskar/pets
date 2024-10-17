from django.shortcuts import render,redirect
from petapp.models import Pet,Cart,User,Profile,Order
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Q
import razorpay
from django.core.mail import send_mail

# Create your views here.
categories = Pet.objects.values("type").distinct()



def home(request):
    # print('after login in home:',request.user.is_authenicated)
    context={}
    data = Pet.objects.all()
    context['pets']= data
    categories = Pet.objects.values('type').distinct()
    print(categories)
    context['text']=categories
    return render(request,'index.html',context)
   

def register(request):
    if request.method=='GET':
         return render(request,'register.html')
    else:
        context={}
        u = request.POST['username']
        e = request.POST['email']
        p = request.POST['password']
        cp = request.POST['confirmpassword']
        

        if u==' ' or e==' ' or p==' ' or cp==' ':
            context['error']='please fill all details'
            return render(request,'register.html',context)
        elif p != cp:
            context['error']='password and confirm password must be same'
            return render(request,'register.html',context)
        elif User.objects.filter(username=u).exists():
            context['error']='Username already exist!! kindly use different username'
            return render(request,'register.html',context)
        else:
            user= User.objects.create(username=u,email=e)
            user.set_password(p)
            user.save() # password encryption
            # context['success']='Registered successfully!! please login'
            # return render(request,'login.html',context)
            messages.success(request,'Registered successfully !! please Login')
            return redirect('/login')
        

def userLogin(request):
    if request.method=="GET":
        return render(request,'login.html')
    else:
        context={}
        u = request.POST['username']
        p = request.POST['password']
        user= authenticate(username=u, password=p)
        if user is None:
            print("wrong details")
            context['error']='kindly enter correct details to login'
            return render(request,'login.html',context)
        else:
            print('successful authenication')
            print(request.user.is_authenticated)
            login(request,user)
            messages.success(request,'Logged in successfully!!')
            return redirect('/')
        
def userLogout(request):
    logout(request)        
    return redirect('/')

def aboutUs(request):
    return render(request,'aboutus.html')

def contactUs(request):
    return render(request,'contactus.html')

def petDetails(request,petid):
    data = Pet.objects.get(id = petid)
    context = {}
    context['pet'] = data
    return render(request,'details.html',context)

def searchBycategory(request,searchBy):
    data = Pet.objects.filter(type = searchBy)
    context ={}
    context['pets']=data
    return render(request,'index.html',context)

def searchByRange(request):
    minprice= request.GET['min']
    maxprice= request.GET['max']
    c1= Q(price__gte = minprice)
    c2 = Q(price__lte = maxprice)
    data = Pet.objects.filter(c1 & c2)
    context = {}
    context['pets']=data
    return render(request,'index.html',context)

def sortPetsByPrice(request,dir):
    if  dir == 0:
        col='price'
    else:
        col='-price'
    data = Pet.objects.all().order_by(col)  
    context={}      
    context['pets']=data
    return render(request,'index.html',context)

def addToCart(request,petid):
    userid = request.user.id
    if userid:    
     
     pet = Pet.objects.get(id=petid)
     cart = Cart.objects.create(petid = pet, uid = request.user)
     cart.save()
     messages.success(request,'pet added to cart sucessfully')
     return redirect('/')
    else:
        messages.error(request,'Please login')
        return redirect('/login')
    
def showMyCart(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    context={}
    context['cartlist'] = data
    count = len(data)
    total =0
    for cart in data:
        total += cart.petid.price*cart.quantity
    context['count']=count
    context['total']=total
    return render(request,'cart.html',context)

def removeCart(request,cartid):
    cart=Cart.objects.filter(id = cartid)
    cart.delete()
    messages.success(request,'pet removed from cart sucessfully')
    return redirect('/mycart')

def updateQuantity(request,cartid,oprn):
    if oprn =='incr':
      cart = Cart.objects.filter(id = cartid)
      qty = cart[0].quantity
      cart.update(quantity = qty+1)
      return redirect('/mycart')
    else:
        cart = Cart.objects.filter(id = cartid)
        qty = cart[0].quantity
        cart.update(quantity = qty-1)
        return redirect('/mycart')
    
def confirmOrder(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    context={}
    context['cartlist'] = data
    count = len(data)
    total = 0
    for cart in data:
        total += cart.petid.price*cart.quantity
    context['count'] = count
    context['total'] = total
    # context['types'] = categories
    # context['profile']= Profile.objects.get(id = userid)
    return render(request,'confirmorder.html',context)
   
def addProfile(request):
    if request.method=="GET":
        return render(request,'profile.html')
    else:
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        m = request.POST['mobile']
        a = request.POST['address']

        userid = request.user.id
        user = User.objects.filter(id = userid)
        user.update(first_name=fn, last_name=ln)

        profile = Profile.objects.create(id = user[0], mobile = m, address = a)
        profile.save()
        messages.success(request,'Profile Updated Succefully !!')
        return redirect('/')

def addProfile(request):
    if request.method== "GET":
        return render(request,'profile.html')
    else:
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        m = request.POST['mobile']
        a = request.POST['address']

        userid = request.user.id
        user = User.objects.filter(id = userid)
        user.update(first_name=fn, last_name=ln)

        profile = Profile.objects.create(id = user[0] , mobile = m, address = a)
        profile.save()
        messages.success(request,'Profile updated sucessfully !!')
        return redirect('/')
    
def makePayment(request):
      
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    total =0
    for cart in data:
        total += cart.petid.price*cart.quantity
    client = razorpay.Client(auth=("rzp_test_QPXTPF1KYwWdC0", "QrLzjZkppijznBLWFiAnmDSt"))

    data = { "amount": total*100, "currency": "INR", "receipt": "" }
    payment = client.order.create(data=data)
    context={}
    context['data'] = payment
    return render(request,'pay.html',context)



def placeorder(request,ordid):
    userid = request.user.id
    # user = User.objects.get(id = userid)
    cartlist = Cart.objects.filter(uid = userid)
    for cart in cartlist:
        # pet = Pet.objects.get(id = cart.petid)
        order = Order.objects.create(orderid= ordid, userid = cart.uid, petid = cart.petid ,quantity = cart.quantity)
        order.save()
    cartlist.delete()  
    msg= "Thanks you for placing the order .you order id is:"+ordid
    send_mail(
        "order placed sucessfully",
        msg,
        "sonalipalaskar598@gmail.com",
        [request.user.email],
        fail_silently=False,
    )
    messages.success(request,'order placed sucessfully')
    return redirect('/')


   
        

                  
 



    