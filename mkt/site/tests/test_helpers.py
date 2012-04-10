import json

import mock
from nose.tools import eq_
from pyquery import PyQuery as pq

import amo
import amo.tests
from amo.urlresolvers import reverse
from mkt.webapps.models import Webapp
from mkt.site.helpers import market_button


class TestMarketButton(amo.tests.TestCase):
    fixtures = ['webapps/337141-steamcube', 'base/users']

    def setUp(self):
        self.webapp = Webapp.objects.get(pk=337141)
        self.context = {'request': mock.Mock()}

    def test_not_webapp(self):
        self.webapp.update(type=amo.ADDON_EXTENSION)
        # TODO: raise a more sensible error.
        self.assertRaises(UnboundLocalError, market_button,
                          self.context, self.webapp)

    def test_is_webapp(self):
        doc = pq(market_button(self.context, self.webapp))
        data = json.loads(doc('a').attr('data-product'))
        eq_(data['manifestUrl'], self.webapp.manifest_url)
        eq_(data['recordUrl'], self.webapp.get_detail_url('record'))
        eq_(data['preapprovalUrl'], reverse('detail.purchase.preapproval',
                                            args=[self.webapp.app_slug]))
        eq_(data['id'], self.webapp.pk)
        eq_(data['name'], self.webapp.name)

    @mock.patch('addons.models.Addon.has_purchased')
    def test_is_premium_webapp(self, has_purchased):
        has_purchased.return_value = True
        self.make_premium(self.webapp)
        doc = pq(market_button(self.context, self.webapp))
        data = json.loads(doc('a').attr('data-product'))
        eq_(data['manifestUrl'], self.webapp.manifest_url)
        eq_(data['price'], self.webapp.premium.get_price() or '0')
        eq_(data['purchase'], self.webapp.get_purchase_url())
        eq_(data['isPurchased'], True)



