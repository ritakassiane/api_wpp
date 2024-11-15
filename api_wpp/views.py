from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Product, Order, OrderItem
from .serializers import ProductSerializer
from django.db import transaction
import decimal
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
import requests

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

    if created:
        user_url = reverse('customer_page', args=[customer.id])
        return Response(
            {"message": "Customer created", "customer_url": request.build_absolute_uri(user_url)},
            status=status.HTTP_201_CREATED,
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

def customer_page(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        # Você pode renderizar uma página HTML personalizada
        return render(request, 'customer_page.html', {"customer": customer})
    except Customer.DoesNotExist:
        return HttpResponse("Customer not found", status=404)
    

def connect_instance(request, customer_id):
    if request.method == "POST":
        customer = get_object_or_404(Customer, id=customer_id)

        # Obter os dados do formulário
        phone = request.POST.get("phone")
        webhook_url = request.POST.get("webhookUrl")

        # Dados para o POST na API externa
        url = "https://evolution.karolnaturais.pt/instance/create"
        payload = {
            "instanceName": customer.name,
            "number": phone,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
            "reject_call": True,
            "groupsIgnore": True,
            "alwaysOnline": True,
            "readMessages": True,
            "readStatus": True,
            "syncFullHistory": False,
            "webhookUrl": webhook_url,
            "webhookByEvents": True,
            "webhookBase64": True,
        }
        headers = {
            "apikey": "14bef9be8d234edce9e2fd15c64ddcf7",
            "Content-Type": "application/json"
        }

        # Enviar a solicitação para a API externa
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            # Parse do JSON para extrair os campos necessários
            data = response.json()
            instance_name = data.get("instance", {}).get("instanceName", "N/A")
            pairing_code = data.get("qrcode", {}).get("pairingCode", "N/A")
            qr_code_base64 = data.get("qrcode", {}).get("base64", "")

            # Renderizar a página com os dados
            return render(
                request,
                "connect_instance.html",
                {
                    "instance_name": instance_name,
                    "pairing_code": pairing_code,
                    "qr_code_base64": qr_code_base64,
                },
            )
        else:
            return render(
                request,
                "connect_instance.html",
                {
                    "error": "Erro ao criar a conexão. Tente novamente.",
                    "details": response.text,
                },
            )

    return JsonResponse({"error": "Método não permitido"}, status=405)
    if request.method == "POST":
        customer = get_object_or_404(Customer, id=customer_id)

        # Obter os dados do formulário
        phone = request.POST.get("phone")
        webhook_url = request.POST.get("webhookUrl")

        # Dados para o POST na API externa
        url = "https://evolution.karolnaturais.pt/instance/create"
        payload = {
            "instanceName": customer.name,
            "number": phone,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
            "reject_call": True,
            "groupsIgnore": True,
            "alwaysOnline": True,
            "readMessages": True,
            "readStatus": True,
            "syncFullHistory": False,
            "webhookUrl": webhook_url,
            "webhookByEvents": True,
            "webhookBase64": True,
        }
        headers = {
            "apikey": "14bef9be8d234edce9e2fd15c64ddcf7",
            "Content-Type": "application/json"
        }

        # Enviar a solicitação para a API externa
        response = requests.post(url, json=payload, headers=headers)

        # Retornar a resposta ao usuário
        if response.status_code == 200:
            return JsonResponse({"message": "Conexão criada com sucesso!", "response": response.json()})
        else:
            return JsonResponse({"message": "Erro ao criar a conexão", "details": response.text}, status=400)

    return JsonResponse({"error": "Método não permitido"}, status=405)

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
