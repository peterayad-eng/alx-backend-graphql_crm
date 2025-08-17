import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import Customer, Product, Order


# ----------------------------
# GraphQL Object Types
# ----------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# =======================
# Input Types
# =======================
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# =======================
# Mutations
# =======================

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")

        # Validate phone format
        if input.phone:
            phone_pattern = re.compile(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$")
            if not phone_pattern.match(input.phone):
                errors.append("Invalid phone format")

        if errors:
            return CreateCustomer(customer=None, message="Failed to create customer", errors=errors)

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully", errors=None)


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for cust in input:
                try:
                    # Reuse validation logic
                    if Customer.objects.filter(email=cust.email).exists():
                        errors.append(f"Email {cust.email} already exists")
                        continue

                    if cust.phone:
                        phone_pattern = re.compile(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$")
                        if not phone_pattern.match(cust.phone):
                            errors.append(f"Invalid phone format for {cust.email}")
                            continue

                    customer = Customer.objects.create(
                        name=cust.name,
                        email=cust.email,
                        phone=cust.phone
                    )
                    created_customers.append(customer)
                except IntegrityError as e:
                    errors.append(f"Failed to create {cust.email}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        if input.price <= 0:
            errors.append("Price must be positive")

        if input.stock is not None and input.stock < 0:
            errors.append("Stock cannot be negative")

        if errors:
            return CreateProduct(product=None, errors=errors)

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )
        return CreateProduct(product=product, errors=None)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return CreateOrder(order=None, errors=errors)

        if not input.product_ids:
            errors.append("At least one product must be provided")
            return CreateOrder(order=None, errors=errors)

        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            errors.append("Some product IDs are invalid")
            return CreateOrder(order=None, errors=errors)

        order_date = input.order_date or timezone.now()

        order = Order.objects.create(
            customer=customer,
            order_date=order_date,
            total_amount=sum([p.price for p in products])
        )
        order.products.set(products)

        return CreateOrder(order=order, errors=None)


# ----------------------------
# Root Mutation Class
# ----------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

