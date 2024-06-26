from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages, auth
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.text import slugify
from django.views.decorators.csrf import requires_csrf_token
from vendor.models import Vendor

# Create your views here.

#Restrict the vendor from acessing the customer page
def check_role_vendor(user):
      if user.role == 1:
            return True
      else:
            raise PermissionDenied


#Restrict the customer from acessing the vendor page
def check_role_customer(user):
      if user.role == 2:
            return True
      else:
            raise PermissionDenied



def registerUser(request):
    if request.user.is_authenticated: # user is already logged in or not 
        messages.warning(request, 'You are already logged in')
        return redirect('myAccount')
    elif request.method == 'POST':
        # print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # create the user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role=User.CUSTOMER
            # user.save()
            
            
            # create the user using create_user method 
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user  = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,email=email, password=password)
            user.role = User.CUSTOMER
            user.save()
            
            # send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            
            # messages 
            messages.success(request, 'your account registered successfully')
            print('User is created')
            return redirect('registerUser')
        
        else:
            print('invalid form')
            print(form.errors)
            
    else:
        
    
        form = UserForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated: # user is already logged in or not 
        messages.warning(request, 'You are already logged in')
        return redirect('myAccount')
    elif request.method == 'POST':

        # store the data and create the user 
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user  = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)  # commit false mins - 
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']   
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)  # create the slug for the vendor
            user_profile = UserProfile.objects.get(user=user)  #
            vendor.user_profile = user_profile  # vendor user profile to connect the vendor 
            vendor.save()
            
            # Send verification email
            mail_subject = 'Please Activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)  # send verification email
            
            messages.success(request, 'Your account has been registered successfully! please wai for the approval.')
            return redirect('registerVendor')
            
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    
    context = {
        'form': form,
        'v_form': v_form,
    }
    
    return render(request, 'accounts/registerVendor.html',context)




def activate(request, uidb64, token):
    # activate the user by setting the is_active status to True 
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=None
        
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request, 'Congratulation! your account has been activated!')
        return redirect('myAccount')
    
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')





@requires_csrf_token
def login(request):
    if request.user.is_authenticated: # user is already logged in or not 
        messages.warning(request , 'You are already logged in')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']  # fetch the email address using the post request 
        password = request.POST['password'] # fetch the password using the post request
        
        user = auth.authenticate(email=email,password=password)   # authenticate the email and password 
        if user is not None:
            auth.login(request,user)  # allow the user to login 
            messages.success(request, 'You are logged in')
            return redirect('myAccount')
            
        else:
            messages.error(request , 'Invalid login credentials')  # user is not logged in
            return redirect('login')
    return render(request, 'accounts/login.html')




@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out')   # inf mins color is blue 
    return redirect('login')




@login_required(login_url='login')
def myAccount(request):
    user = request.user 
    redirectURl = detectUser(user)
    return redirect(redirectURl)






@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request, 'accounts/customerdashboard.html')




@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendordashboard.html')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            
            
            # send the reset password email 
            mail_subject = 'Reset your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user,mail_subject, email_template)
            
            messages.success(request,'Password reset link has been sent to your email address')
            return redirect('login')
        
        else:
            messages.error(request,'Account does not exist')
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired')
        return redirect('myAccount')


        
      #validate the user by decoding the token  and user pk
        
        
        
        


def reset_password(request):
      if request.method == 'POST':
          password = request.POST['password']
          confirm_password = request.POST['confirm_password']

          if password == confirm_password:
              pk = request.session.get('uid')
              user = User.objects.get(pk=pk)
              user.set_password(password)
              user.is_active = True
              user.save()
              messages.success(request, 'password reset successful')
              return redirect('login')
          else:
              messages.error(request, 'Password do not match!')
              return redirect('reset_password')
      return render (request, 'accounts/reset_password.html')