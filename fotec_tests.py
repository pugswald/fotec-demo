import fotec
import json
import os
import sys
import unittest

test_data = { 'user': { 'name':'tester', 'device':'Q9Q0L44G31ZCFI82', 'pin':'4321'},
              'cards': [{ 'name': "Visa 1", 'bank': "Chase" , 'network': "Visa" , 'last_four': '7418' },
                      { 'name': "Visa 2", 'bank': "Wells Fargo", 'network': "Visa" , 'last_four': '3438'},
                      { 'name': "MC 1", 'bank': "HSBC", 'network': "Mastercard" , 'last_four': '2293'},
                      { 'name': "MC 2", 'bank': "Citigroup", 'network': "Mastercard" , 'last_four': '9823'},
                      ]
            }

class FotecTestCase(unittest.TestCase):
    
    def setUp(self):
        fotec.app.config['DATABASE'] = os.path.join(fotec.app.root_path, 'test.db')
        self.db_fd = open(fotec.app.config['DATABASE'], 'w')
        fotec.app.config['TESTING'] = True
        self.app = fotec.app.test_client()
        fotec.init_db()
        fotec.create_user(test_data['user']['name'],test_data['user']['device'],test_data['user']['pin'])
        for card in test_data['cards']:
            fotec.add_card(test_data['user']['device'],test_data['user']['pin'],card)
     
    def tearDown(self):
        self.db_fd.close()
        
    def test_card(self):
        rc = self.app.get('/card?device=%s&pin=%s'%(test_data['user']['device'],test_data['user']['pin']))
        # ID comes back so matching all cards is a bear, just checking the first matches the first entered
        self.assertEqual(json.loads(rc.data)['data'][0]['name'],test_data['cards'][0]['name']) 
        rc = self.app.get('/card?device=%s&pin=%s'%(test_data['user']['device'],'badpinhere'))
        self.assertEqual(json.loads(rc.data),fotec.AUTH_FAILURE) # ID comes back so it may not match

    def test_pay(self):
        have_approval = False
        have_tx_fail = False
        while not have_approval or not have_tx_fail:
            rc = self.app.post('/pay', data=dict(
                device = test_data['user']['device'],
                pin = test_data['user']['pin'],
                card_id = 1,
                amount = 42.13,
                merchant = fotec.VALID_MERCHANTS[0]))
            result = json.loads(rc.data)
            if 'error' in result:
                self.assertEqual(result,fotec.TRANSACTION_FAILURE)
                have_tx_fail = True
            else:
                self.assertIn('approval',result.keys())
                have_approval = True
        # TODO: Test bad inputs
 

if __name__ == '__main__':
    unittest.main()
        
        