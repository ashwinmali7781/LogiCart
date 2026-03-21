from django.test import TestCase, Client
from django.urls import reverse
import datetime
import json

from .models import Product, Contact, Orders, OrderUpdate


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            product_name='Test Phone',
            category='Electronics',
            price=9999,
            desc='A great test phone.',
            pub_date=datetime.date.today(),
        )

    def test_str(self):
        self.assertIn('Test Phone', str(self.product))

    def test_price_non_negative(self):
        self.assertGreaterEqual(self.product.price, 0)


class IndexViewTest(TestCase):
    def test_index_status(self):
        response = self.client.get(reverse('ShopHome'))
        self.assertEqual(response.status_code, 200)

    def test_index_template(self):
        response = self.client.get(reverse('ShopHome'))
        self.assertTemplateUsed(response, 'shop/index.html')


class SearchViewTest(TestCase):
    def setUp(self):
        Product.objects.create(
            product_name='Wireless Headphones',
            category='Electronics',
            price=2499,
            desc='Noise cancelling.',
            pub_date=datetime.date.today(),
        )

    def test_search_found(self):
        response = self.client.get(reverse('Search'), {'search': 'headphone'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wireless Headphones')

    def test_search_empty_redirects(self):
        response = self.client.get(reverse('Search'), {'search': 'x'})
        # Single char — should redirect
        self.assertEqual(response.status_code, 302)

    def test_search_no_results(self):
        response = self.client.get(reverse('Search'), {'search': 'zzznomatch'})
        self.assertEqual(response.status_code, 200)


class ProductViewTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            product_name='Smart TV',
            category='Electronics',
            price=34999,
            desc='4K display.',
            pub_date=datetime.date.today(),
        )

    def test_product_view_ok(self):
        response = self.client.get(reverse('ProductView', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart TV')

    def test_product_view_404(self):
        response = self.client.get(reverse('ProductView', args=[99999]))
        self.assertEqual(response.status_code, 404)


class ContactViewTest(TestCase):
    def test_contact_get(self):
        response = self.client.get(reverse('ContactUs'))
        self.assertEqual(response.status_code, 200)

    def test_contact_post_valid(self):
        response = self.client.post(reverse('ContactUs'), {
            'name': 'Alice', 'email': 'alice@example.com',
            'phone': '9876543210', 'desc': 'Hello there, I have a question.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Contact.objects.count(), 1)

    def test_contact_post_missing_field(self):
        response = self.client.post(reverse('ContactUs'), {
            'name': '', 'email': 'alice@example.com', 'desc': 'Message',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)


class TrackerViewTest(TestCase):
    def setUp(self):
        self.order = Orders.objects.create(
            items_json='{}', amount=500, name='Bob',
            email='bob@example.com', address='123 St', city='Delhi',
            state='Delhi', zip_code='110001', phone='9000000000',
        )
        OrderUpdate.objects.create(order=self.order, update_desc='Order placed')

    def test_tracker_get(self):
        response = self.client.get(reverse('TrackingStatus'))
        self.assertEqual(response.status_code, 200)

    def test_tracker_post_found(self):
        response = self.client.post(reverse('TrackingStatus'), {
            'orderId': self.order.order_id,
            'email': 'bob@example.com',
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['updates']), 1)

    def test_tracker_post_not_found(self):
        response = self.client.post(reverse('TrackingStatus'), {
            'orderId': 99999, 'email': 'nobody@example.com',
        })
        data = response.json()
        self.assertEqual(data['status'], 'noitem')
