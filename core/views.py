from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import *
from .models import *
from .models import Customer as User

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.views import PasswordResetView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
ONUNE_GELEN_GIRSIN_MI = True


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


# CEM BUNU AÇ KAPA YAPARAK AUTH GEREKENSINIMI KONTROL ET

class UserApiView(APIView):

    def post(self, request, *args, **kwargs):
        user_email = request.data.get('email', None)
        user_password = request.data.get('password', None)
        if user_email is None or user_password is None:
            return Response({'detail': 'Email or Password fields must be not empty.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not validateEmail(user_email):
                return Response({'detail': 'Please enter a valid email.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # valid email.
                # TODO: add more fields
                user = User.objects.create(
                    email=user_email,)
                user.set_password(user_password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                """
                mail_subject = 'CEMAL - Activate Your Account'
                message = render_to_string('emails/verify-email.txt', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = user_email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                """ 
                s_user = UserSerializer(user)
                return Response(s_user.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        s_user = UserSerializer(request.user)
        return Response(s_user.data)


class MyPasswordResetView(PasswordResetView):
    api_posted_email = None

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(**kwargs)
        f = context['form']
        print(request.POST.get('email'))
        print(kwargs)


class PasswordResetApi(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        email = request.data.get('email')
        prv = MyPasswordResetView.as_view(api_posted_email=email)(request)
        print('PASS API::', email)
        print('PASS API:: prv ', prv)
        pass


def signup(request):
    if request.method == 'POST':
        print("request.post")
        print(request.POST)
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'CEMAL - Activate Your Account'
            message = render_to_string('emails/verify-email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the admin')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # TODO: add django message and redirect to success page
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


class HomepageView(TemplateView):
    template_name = "core/index.html"


class CompanyViewSet(viewsets.ModelViewSet):
    """API endpoint that allows companies to be viewed or edited."""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    if not ONUNE_GELEN_GIRSIN_MI:
        permission_classes = [permissions.IsAuthenticated]


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    if not ONUNE_GELEN_GIRSIN_MI:
        permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # .filter(pk=request.user.id)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


class CatalogViewSet(viewsets.ModelViewSet):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    if not ONUNE_GELEN_GIRSIN_MI:
        permission_classes = [permissions.IsAuthenticated]


class ShoppingListApiView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = ShoppingListSerializer
        queryset = ShoppingList.objects.filter(customer=request.user.id, is_deleted_offline=False)
        serializer = serializer(queryset, many=True,
                                context={'request': request})
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        sl_id = request.data.get('id', None)
        if sl_id is not None:
            sl_obj = ShoppingList.objects.filter(pk=sl_id)
            sl_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail':'You have to give me an id.'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        # ShoppingList ShoppingListItem
        # TODO: VALID DATA?
        # just use serializers.
        shopping_lists = request.data
        response = None
        if len(shopping_lists) == 0:
                return Response({}, status=status.HTTP_200_OK)
        for sl in shopping_lists:
            id = sl.get('id', None)
            name = sl.get('name', None)
            customer = sl.get('customer', None)
            is_deleted_offline = sl.get('is_deleted_offline', None)
            shopping_list_items = sl.get('shopping_list_items', None)
            sl_obj = None
            sl_data = {'name': name, 'customer': customer, 'is_deleted_offline':is_deleted_offline}
            if id is not None:
                sl_data.update({'id': id})
                sl_obj = ShoppingList.objects.get(pk=sl_data['id'])
                # updating Shopping List
                if is_deleted_offline and sl_obj is not None:
                    # we have to delete it
                    sl_obj.delete()
                else:
                    # just update the name
                    sl_obj.name = sl_data['name']
                    sl_obj.save()
            else:
                # creating Shopping list bc there was no id
                print('creating Shopping list bc there was no id')
                """
                sl_obj = ShoppingListSerializer(
                    data=sl_data, context={'request': request})
                if sl_obj.is_valid():
                    print('sl - obj valid')
                    sl_obj = sl_obj.save()
                """

                sl_obj = ShoppingList.objects.create(
                    name=sl_data['name'],
                    customer=request.user
                )
                created_sl_serializer = ShoppingListSerializer(sl_obj, context={'request':request})
                response = Response(created_sl_serializer.data, status=status.HTTP_201_CREATED)
                

            if shopping_list_items is not None:
                for sl_item in shopping_list_items:

                    # burada
                    sli_id = sl_item.get('id', None)
                    sli_sl_id = sl_item.get('shopping_list', None)
                    sli_text = sl_item.get('text', None)
                    sli_visible = sl_item.get('is_visible', None)
                    sli_company_id = sl_item.get('company', None)
                    sli_checked = sl_item.get('is_checked', None)

                    sli_data = {'shopping_list': sl_obj.id, 'text': sli_text,
                                'is_visible': sli_visible, 'company': sli_company_id, 'is_checked': sli_checked}

                    if sli_id is None:
                        # yaratmamız ve gerek, ve
                        sli_obj = ShoppingListItemSerializer(data=sli_data)
                        if sli_obj.is_valid():
                            sli_obj.save()
                    else:
                        # existing sli, so we have to update
                        sli_obj = ShoppingListItem.objects.get(pk=sli_id)
                        sli_obj.text = sli_text
                        sli_obj.is_visible = sli_visible
                        sli_obj.is_checked = sli_checked
                        sli_obj.company_id = sli_company_id
                        sli_obj.save()

        print('response', response)
        if response is not None and len(shopping_lists) == 1:
            # if there was one obj creation, return the id of it
            return response
        else:
            return Response(status=status.HTTP_200_OK)


class ShoppingListItemViewSet(viewsets.ModelViewSet):
    queryset = ShoppingListItem.objects.filter(is_visible=True).order_by("is_checked")
    serializer_class = ShoppingListItemSerializer
    if not ONUNE_GELEN_GIRSIN_MI:
        permission_classes = [permissions.IsAuthenticated]


"""

class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(customer=request.user.id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        print('getting the list of : ', user)
        return ShoppingList.objects.filter(customer=user.id)

    if not ONUNE_GELEN_GIRSIN_MI:
        permission_classes = [permissions.IsAuthenticated]

"""
