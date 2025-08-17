import os
import sys
import django

# Add project directory to path
sys.path.append('/workspaces/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed():
    print("Starting database seeding...")
    
    # Create some customers
    customer1, _ = Customer.objects.get_or_create(
        email="alice@example.com",
        defaults={'name': "Alice", 'phone': "+1234567890"}
    )
    customer2, _ = Customer.objects.get_or_create(
        email="bob@example.com", 
        defaults={'name': "Bob", 'phone': "123-456-7890"}
    )
    customer3, _ = Customer.objects.get_or_create(
        email="carol@example.com",
        defaults={'name': "Carol"}
    )
    
    # Create some products
    product1, _ = Product.objects.get_or_create(
        name="Laptop",
        defaults={'price': 999.99, 'stock': 10}
    )
    product2, _ = Product.objects.get_or_create(
        name="Phone", 
        defaults={'price': 499.99, 'stock': 20}
    )
    product3, _ = Product.objects.get_or_create(
        name="Tablet",
        defaults={'price': 299.99, 'stock': 15}
    )
    
    print(f"Created customers: {Customer.objects.count()}")
    print(f"Created products: {Product.objects.count()}")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()

