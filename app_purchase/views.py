from django.shortcuts import render, redirect
from . models import Cart, CartItem, Identifier, OrderItem, Order
from app_product.models import Product
from app_reference.models import SDEK_Office
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, id):
    product=Product.objects.get(id=id)
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        #cart=Cart.objects.get(cart_id=request.session)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        #cart = Cart.objects.create(cart_id=request.session)
        #cart.save()
    try:
        cart_item = CartItem.objects.get(product=product.name, cart=cart)
        cart_item.quantity+=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product.name,
            article=product.article,
            image=product.image_1,
            cart=cart,
            quantity=1,
            price=product.site_retail_price,
        )

    return redirect('cart_detail')

def cart_detail(request):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        #cart=Cart.objects.get(cart_id=request.session)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    cart=Cart.objects.get(cart_id=cart)
    cart_items=CartItem.objects.filter(cart=cart).order_by('product')
    total=0
    for item in cart_items:
        sub_total=item.quantity*item.price
        total+=sub_total
        

    context = {
        'cart_items' : cart_items,
        'total': total,
    }

    return render (request, 'cart/cart.html', context)

def add_cart_item(request, id):
    cart_item=CartItem.objects.get(id=id)
    cart_item.quantity+=1
    cart_item.save()
    return redirect ('cart_detail')

def remove_cart_item(request, id):
    cart_item=CartItem.objects.get(id=id)
    if cart_item.quantity > 1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect ('cart_detail')

def delete_cart_item(request, id):
    cart_item=CartItem.objects.get(id=id)
    cart_item.delete()
    return redirect ('cart_detail')

def purchase_product(request):
    if request.method == "POST":
        check_boxes=request.POST.getlist("checkbox", None)
        # identifier=Identifier.objects.create()
        order=Order.objects.create()
        for value in check_boxes:
            cart_item=CartItem.objects.get(id=value)
            order_item=OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                article=cart_item.article,
                image=cart_item.image,
                price=cart_item.price,
                quantity=cart_item.quantity,
                sub_total=cart_item.price*cart_item.quantity,

            )
        order_items=OrderItem.objects.filter(order=order).order_by('product')
        sum=0
        for item in order_items:
            sum+=item.sub_total
        order.sum=sum
        order.save()
        return redirect ('order',  order.id)
    
def order(request, order_id):
    countries=['Россия', 'Казахстан', 'Белоруссия']
    # sdek_offices=SDEK_Office.objects.filter(country_code__in=['KZ', 'RU', 'BY']).order_by('-country_code')
 

    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items,
        'countries': countries,
        # 'sdek_offices': sdek_offices,
    }

    return render (request, 'cart/order_page.html', context)
 
