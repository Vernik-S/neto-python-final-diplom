from my_app.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter
from orders.celery import app
from django.core.mail import EmailMultiAlternatives


@app.task
def send_mail(title, message, from_, to_):
    msg = EmailMultiAlternatives(
        # title:
        title,
        # message:
        message,
        # from:
        from_,
        # to:
        to_
    )
    msg.send()

@app.task
def do_import(data):
    shop, _ = Shop.objects.get_or_create(name=data['shop'])
    for category in data['categories']:
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)
        category_object.save()
    ProductInfo.objects.filter(shop_id=shop.id).delete()
    for item in data['goods']:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

        product_info = ProductInfo.objects.create(product_id=product.id,
                                                  external_id=item['id'],
                                                  model=item['model'],
                                                  price=item['price'],
                                                  price_rrc=item['price_rrc'],
                                                  quantity=item['quantity'],
                                                  shop_id=shop.id)
        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(product_info_id=product_info.id,
                                            parameter_id=parameter_object.id,
                                            value=value)