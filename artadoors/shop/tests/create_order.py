from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from shop.models import Cart, Order, OrderItem, Product, SizeOption, HandleOption, Category

class OrderViewTest(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед выполнением тестов."""
        self.client = Client()
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Создаем категорию для продукта (чтобы избежать ошибки внешнего ключа)
        self.category = Category.objects.create(title='Тестовая категория')
        
        # Создаем тестовый продукт
        self.product = Product.objects.create(
            name='Тестовый продукт',
            category=self.category,
            base_price=100.00,
        )
        
        # Создаем опции для товара (без лишних аргументов)
        self.size_option = SizeOption.objects.create(product=self.product, size_name='Размер 1', price_increase=200)
        self.handle_option = HandleOption.objects.create(products=self.product, handle_name='Ручка 1', price_increase=100)
        
        # Создаем URL для страницы заказа
        self.order_url = reverse('shop:order')
    
    def test_order_creation_anonymous_user(self):
        """Проверка оформления заказа для анонимного пользователя."""
        session = self.client.session
        session['session_key'] = self.client.session.session_key
        session.save()

        print(self.product, self.size_option, self.handle_option, self.product.base_price)
        
        # Создаем корзину для анонимного пользователя
        Cart.objects.create(
            session_key=session['session_key'],
            product=self.product,
            size_option=self.size_option,
            handle_option=self.handle_option,
            threshold='да',
            opening_side='левая',
            quantity=1,
            price=self.product.base_price
        )

        # Отправляем POST-запрос с данными
        response = self.client.post(self.order_url, {
            'last_name': 'Иванов',
            'first_name': 'Иван',
            'phone': '1234567890',
            'email': 'test@example.com',
            'address': 'Москва',
            'delivery_method': 'company1',
            'payment_method': 'card',
            'action': 'checkout'
        })

        print("Cart items:", Cart.objects.all())
        for cart_item in Cart.objects.all():
            print(f"Product: {cart_item.product}, Size: {cart_item.size_option}, Handle: {cart_item.handle_option}, Price: {cart_item.price}, threshold: {cart_item.threshold}")
        
        print("Order items:", OrderItem.objects.all())
        print("Orders:", Order.objects.all())
        
        # Проверяем, что заказ создан
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertRedirects(response, reverse('shop:cart'))

        order = Order.objects.first()
        self.assertEqual(order.last_name, 'Иванов')
        self.assertEqual(order.first_name, 'Иван')
        self.assertEqual(order.phone, '1234567890')
        self.assertEqual(order.email, 'test@example.com')
        self.assertEqual(order.address, 'Москва')
        self.assertEqual(order.delivery_method, 'company1')
        self.assertEqual(order.payment_method, 'card')
        self.assertEqual(order.status, 'В обработке')
    
        # Проверяем данные элементов заказа
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.size_option, self.size_option)
        self.assertEqual(order_item.handle_option, self.handle_option)
        self.assertEqual(order_item.threshold, 'да')
        self.assertEqual(order_item.opening_side, 'левая')
        self.assertEqual(order_item.quantity, 1)
    
    def test_order_creation_authenticated_user(self):
        """Проверка оформления заказа для авторизованного пользователя."""
        self.client.login(username='testuser', password='password')
        
        # Создаем корзину для пользователя
        Cart.objects.create(
            user=self.user,
            product=self.product,
            size_option=self.size_option,
            handle_option=self.handle_option,
            threshold='да',
            opening_side='правая',
            quantity=2,
            price=self.product.base_price
        )
        
        # Отправляем POST-запрос
        response = self.client.post(self.order_url, {
            'last_name': 'Петров',
            'first_name': 'Петр',
            'phone': '0987654321',
            'email': 'user@example.com',
            'address': 'Санкт-Петербург',
            'delivery_method': 'company2',
            'payment_method': 'cash',
            'action': 'checkout'
        })
        
        # Проверяем, что заказ создан
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertRedirects(response, reverse('shop:cart'))
    
    def test_order_form_invalid(self):
        """Проверка отправки формы с некорректными данными (пустые поля)."""
        response = self.client.post(self.order_url, {
            'last_name': '',  # Пустая фамилия
            'first_name': '',  # Пустое имя
            'phone': '',  # Пустой телефон
            'email': 'invalid-email',  # Неправильный email
            'address': '',  # Пустой адрес
            'delivery_method': '',  # Нет способа доставки
            'payment_method': '',  # Нет способа оплаты
            'action': 'checkout'
        })
        
        # Проверяем, что заказ не был создан
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
