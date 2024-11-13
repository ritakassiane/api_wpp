from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Product, Order, OrderItem
from .serializers import ProductSerializer
from django.db import transaction
import decimal

@api_view(['POST'])
@transaction.atomic
def process_sale(request):
    data = request.data

    # Verifique e crie o cliente, se necessário
    customer_data = data.get("customer")
    customer, created = Customer.objects.get_or_create(
        email=customer_data["email"],
        defaults={
            "name": customer_data["name"],
            "phone": customer_data["phone_number"],
        }
    )

    # Processa cada produto no pedido e cria, se não existir
    products_data = data.get("products", [])
    product_instances = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data["name"],
            defaults={
                "price": decimal.Decimal(product_data["price"].replace("R$", "").replace(",", ".").strip()),
            }
        )
        product_instances.append(product)

    # Cria o pedido associado ao cliente
    order = Order.objects.create(
        customer=customer,
        price=decimal.Decimal(data["total_price"].replace("R$", "").replace(",", ".").strip()),
    )

    # Cria os itens do pedido
    for product_data, product in zip(products_data, product_instances):
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,  # Defina a quantidade conforme necessário
            item_price=decimal.Decimal(product_data["price"].replace("R$", "").replace(",", ".").strip())
        )

    return Response({"message": "Sale processed successfully"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_product(request):
    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
