import asyncio
from ecommerce_client import ECommerceAPIClient, ProductCreate, Address, OrderCreate, OrderItem, Payment

async def test_client():
    # Initialize client
    async with ECommerceAPIClient("http://api.example.com", api_key="test_key") as client:
        try:
            # Test listing products
            products = await client.listProducts(
                category=["electronics"],
                price_range={"min": 0, "max": 1000},
                sort="price_asc",
                page=1,
                page_size=10
            )
            print("Listed products:", products)

            # Test creating a product
            new_product = ProductCreate(
                name="Test Product",
                description="A test product",
                price=99.99,
                category="electronics",
                tags=["test", "new"],
                attributes={"color": "black"}
            )
            created_product = await client.createProduct(new_product)
            print("Created product:", created_product)

            # Test creating an order
            order = OrderCreate(
                items=[
                    OrderItem(
                        product_id=created_product.id,
                        quantity=1,
                        price_at_time=99.99
                    )
                ],
                shipping_address=Address(
                    street="123 Test St",
                    city="Test City",
                    state="TS",
                    country="Test Country",
                    postal_code="12345"
                ),
                payment=Payment(
                    method="credit_card",
                    card_token="test_token"
                )
            )
            created_order = await client.createOrder(order)
            print("Created order:", created_order)

        except Exception as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_client()) 