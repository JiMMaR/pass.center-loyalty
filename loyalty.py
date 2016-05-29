import os.path, logging, sys, time
try:
	import ujson as json
except ImportError:
	try:
		import simplejson as json
	except ImportError:
		import json
try:
	import requests
except ImportError:
	pass


__version_info__ = ('0', '1')
__version__ = '.'.join(__version_info__)

__allowed_images__ = ['icon', 'logo', 'strip', 'thumbnail', 'background', 'footer']

logger = logging.getLogger('passcenter')

class LoyaltyPass(object):
	"""Provide methods to access the loyalty program apis """
	app_key = None
	base_url = None
	debug = True

	__instance = None

	def __init__(self, app_key, base="https://pass.center/api/%s/loyalty", version="v1", debug=False):

		self.base_url = base % version
		self.session = requests.session()

		if app_key is None and 'PASS_APPKEY' in os.environ :
			app_key = os.environ['PASS_APPKEY']

		if app_key is None:
			raise PassCenterException('You must provide a pass App Key')

		self.app_key = app_key
		self.debug = debug


	@classmethod
	def start(cls, *args, **kwargs):
		if not cls.__instance:
			cls.__instance = cls(*args, **kwargs)
		return cls.__instance


	######################### Loyalty Program #########################
	def list_programs(self):
		"""Return a lists of all the programs for the current appkey."""
		resource = '/programs'
		return self.__call('get', resource)


	def show_program(self, program_id):
		"""Return a program's contents."""
		if not program_id:
			raise PassCenterException('A program id must be passed')
		resource = '/programs/%s' % program_id
		return self.__call('get',resource)


	def create_program_from_dictionary(self, dictionary,cardtype='custom'):
		"""Create a new program with the attributes from a dictionary and return the card's Json."""
		resource = '/programs%s' % ('?type=%s' % cardtype if cardtype else '')
		return self.__call('post', resource, dictionary)


	def create_program_from_attributes(self, name, country, language, company, address, phone, email,
									   description=None, website=None, terms=None, scannerType="Browser", cardtype='custom',):
		"""Create a new program.

		By calling create_program_from_dictionary
		(use the dictionary method for attributes that are not available)"""
		dictionary = {'name'		:name,
					  'description'	:description,
					  'country'		:country,
					  'language'	:language,
					  'company'		:company,
					  'address'		:address,
					  'website'		:website,
					  'phone'		:phone,
					  'email'		:email,
					  'terms'		:terms,
					  'scannerType'	:scannerType,
					  }
		return self.create_program_from_dictionary(dictionary,cardtype)


	def update_program_from_dictionary(self, program_id, dictionary):
		"""Update a program with values from dictionary """
		resource = '/programs/%s' % program_id
		return self.__call('put', resource, dictionary)


	def show_icon(self, program_id):
		"""Return the icon url in a json"""
		resource = '/programs/%s/icon' % program_id
		return self.__call('get',resource)


	def update_icon(self, program_id, icon):
		"""Update the program's icon """
		resource = '/programs/%s/icon' % program_id
		multipart = True
		files = [('image', icon)]
		content = files
		return self.__call('put', resource, content, multipart)


	def change_pass_type(self, passtype):
		"""Change the pass type for the program.

		Only do it after the initial setup.
		Changing it at a later point in time will render previously generated cards unusable."""
		resource = '/programs/%s/passtype' % program_id
		dictionary = {'passType':passtype}
		return self.__call('put',resource,dictionary)


	def show_card(self, program_id):
		"""Return the program's card's Json. """
		if not program_id:
			raise PassCenterException('A program id must be passed')
		resource = '/programs/%s/card' % program_id
		return self.__call('get',resource)


	def update_card_from_dictionary(self, program_id, dictionary):
		"""Update the program's card.

		Use show_card as a template dictionary then change it """
		resource = '/programs/%s/card' % program_id
		return self.__call('put',resource,dictionary)


	def list_card_images(self, program_id):
		"""List the card images (except icon). """
		resource = '/programs/%s/card/images' % program_id
		return self.__call('get', resource)


	def show_card_image(self, program_id, image_type):
		"""Return the specific card image."""
		if image_type not in __allowed_images__:
			logger.warn('Image type %s not available. Image will be ignored.' % image_type)
			return
		resource = '/programs/%s/card/images/%s' % (program_id,image_type)
		return self.__call('get', resource)


	def update_card_image(self, program_id, image_type, image):
		"""Update or create a card image."""
		if image_type not in __allowed_images__:
			logger.warn('Image type %s not available. Image will be ignored.' % image_type)
			return
		resource = '/programs/%s/card/images/%s' % (program_id,image_type)
		multipart = True
		files = [('image', image)]
		content = files
		return self.__call('post', resource, content, multipart)


	def delete_card_image(self, program_id, image_type):
		"""Delete a card image."""
		if image_type not in __allowed_images__:
			logger.warn('Image type %s not available. Image will be ignored.' % image_type)
			return
		resource = '/programs/%s/card/images/%s' % (program_id,image_type)
		return self.__call('delete', resource)


	######################### Loyalty Offers #########################
	def list_offers(self, program_id):
		"""List loyalty offers."""
		resource = '/programs/%s/offers' % program_id
		return self.__call('get', resource)


	def show_offer(self, program_id, offer_id):
		"""Show a loyalty offer."""
		resource = '/programs/%s/offers/%s' % (program_id, offer_id)
		return self.__call('get', resource)


	def create_offer_from_dictionary(self, program_id, dictionary):
		"""Create an offer from a dictionary."""
		resource = '/programs/%s/offers' % program_id
		return self.__call('post', resource, dictionary)


	def create_offer_from_attributes(self, program_id, name, description=None, start_date=None, end_date=None,
									auto_claim=False, auto_claim_overwrite=False, notify=False, notify_message=None, points_min=0,
									points_cost=0, points_max=None, limit_per_customer=None, availability_count=None):
		"""Create an offer from the passed attributes.

		Uses create_offer_from_dictionary"""
		dictionary = {'name'				:name,
					  'description'			:description,
					  'startDate'			:start_date,
					  'endDate'				:end_date,
					  'autoClaim'			:auto_claim,
					  'autoClaimOverwrite'	:auto_claim_overwrite,
					  'notify'				:notify,
					  'notify_message'		:notify_message,
					  'pointsMin'			:points_min,
					  'pointsCost'			:points_cost,
					  'pointsMax'			:points_max,
					  'limitPerCustomer'	:limit_per_customer,
					  'availabilityCount'	:availability_count,
					  }
		return self.create_offer_from_dictionary(program_id, dictionary)


	def update_offer_from_dictionary(self, program_id, offer_id, dictionary):
		"""Update an existing offer with the values from the dictionary."""
		resource = '/programs/%s/offers/%s' % (program_id, offer_id)
		return self.__call('post', resource, dictionary)


	def delete_offer(self, program_id, offer_id):
		"""Delete an offer.

		Only DRAFT offers can be deleted"""
		resource = '/programs/%s/offers/%s' % (program_id, offer_id)
		return self.__call('delete', resource)


	def publish_offer(self, program_id, offer_id):
		"""Publish an offer."""
		resource = '/programs/%s/offers/%s/publish' % (program_id, offer_id)
		return self.__call('post', resource)


	def cancel_offer(self, program_id, offer_id):
		"""Cancel an offer."""
		resource = '/programs/%s/offers/%s/cancel' % (program_id, offer_id)
		return self.__call('post', resource)


	def show_offer_card(self, program_id, offer_id):
		"""Return an offer card."""
		resource = '/programs/%s/offers/%s/card' % (program_id, offer_id)
		return self.__call('get', resource)


	def update_offer_card_from_dictionary(self, program_id, offer_id, dictionary):
		"""Update the offer's card.

		Use show_offer_card as a template dictionary then change it """
		resource = '/programs/%s/offers/%s/card' % (program_id, offer_id)
		return self.__call('put',resource,dictionary)
		

	def list_offer_card_images(self, program_id, offer_id):
		"""List the offer card images (except icon). """
		resource = '/programs/%s/offers/%s/card/images' % (program_id, offer_id)
		return self.__call('get', resource)


	def show_offer_card_image(self, program_id, offer_id, image_type):
		"""Return the specific offer card image."""
		if image_type not in __allowed_images__:
			logger.warn('Image type %s not available. Image will be ignored.' % image_type)
			return
		resource = '/programs/%s/offers/%s/card/images/%s' % (program_id, offer_id, image_type)
		return self.__call('get', resource)


	def update_offer_card_image(self, program_id, offer_id, image_type, image):
		"""Update or create an offer card image."""
		if image_type not in __allowed_images__:
			logger.warn('Image type %s not available. Image will be ignored.' % image_type)
			return
		resource = '/programs/%s/offers/%s/card/images/%s' % (program_id, offer_id, image_type)
		multipart = True
		files = [('image', image)]
		content = files
		return self.__call('post', resource, content, multipart)


	def delete_offer_card_image(self, program_id, offer_id, image_type):
		"""Delete an offer card image."""
		if image_type not in __allowed_images__:
			logger.warn('Image type %s not available. Image will be ignored.' % image_type)
			return
		resource = '/programs/%s/offers/%s/card/images/%s' % (program_id, offer_id, image_type)
		return self.__call('delete', resource)


	######################### Loyalty Customers #########################
	def list_customers(self, program_id):
		"""Return a List of all the customers under a certain program_id."""
		if not program_id:
			raise PassCenterException('A program id must be passed')
		resource = '/programs/%s/customers' % program_id
		return self.__call('get',resource)


	def show_customer(self, program_id, customer_id):
		"""Return the customer's json for a program_id and a customer_id """
		if not program_id:
			raise PassCenterException('A program id must be passed')
		resource = '/programs/%s/customers/%s' % (program_id,customer_id)
		return self.__call('get',resource)


	def create_customer_from_dictionary(self, program_id, dictionary):
		"""Create a new customer."""
		resource = '/programs/%s/customers' % program_id
		return self.__call('post',resource, dictionary)


	def create_customer_from_attributes(self, program_id, first_name=None, last_name=None,
										email=None, phone=None, points=0):
		"""Create a new customer.

		Uses create_customer_from_dictionary to make the call"""

		dictionary = {'firstName'	:first_name,
					  'lastName'	:last_name,
					  'email'		:email,
					  'phone'		:phone,
					  'points'		:points,
					  }
		return self.create_customer_from_dictionary(program_id, dictionary)


	def update_customer_from_dictionary(self, program_id, customer_id, dictionary):
		"""Update a customer's info."""
		resource = '/programs/%s/customers/%s' % (program_id, customer_id)
		return self.__call('put', resource, dictionary)


	def reward_points(self, program_id, customer_id, points=1):
		"""Add points to a customer."""
		resource = '/programs/%s/customers/%s/points/add' % (program_id, customer_id)
		dictionary = {'points':points}
		return self.__call('post', resource, dictionary)


	def delete_customer(self, program_id, customer_id):
		"""Delete a customer."""
		resource = '/programs/%s/customers/%s' % (program_id, customer_id)
		return self.__call('delete', resource)



	######################### Core #########################
	def __call(self, method, resource, content=None, multipart=False):

		headers = {
			'User-Agent' : 'jPassCenter-Python/%s' % (__version__),
			'Accept': 'application/json, */*; q=0.01',
			'Authorization' : self.app_key
		}

		method = method.lower()

		kwargs = {}

		if method == 'post' or method == 'put':
			if multipart:
				kwargs['files'] = content
			else:
				headers['Content-Type']  = 'application/json';
				kwargs['data'] = json.dumps(content)

		if self.debug:
			logger.debug(('> %s %s%s' % (method.upper(), self.base_url, resource)) + ((': %s' % content) if content else '' ))

		response = self.session.request(method, self.base_url + resource, headers=headers, **kwargs)
		if self.debug:
			logger.debug('< %s: %s' % (response.status_code,
								   response.text if response.headers['content-type'].startswith('application/json')
												else '%s (%s bytes)' % (response.headers['content-type'], response.headers['content-length'])
								))

		if response.status_code == requests.codes.unprocessable:
			print response.json()
			raise PassCenterApiValidationException(response.json())

		if response.status_code == requests.codes.unauthorized:
			raise PassCenterApiUnauthorizedException()

		if response.status_code < 200 or response.status_code >= 300:
			raise PassCenterApiException(response.status_code, response.content)

		if response.headers['content-type'].startswith('application/json'):
			print "as json"
			return response.json()
		else:
			return response.content


	def log(self, *args, **kwargs):
		logger.log(self.level, *args, **kwargs)

	def __repr__(self):
		return '<PassCenter %s>' % self.app_key

class PassCenterObject(object):
	def __init__(self, engine, **entries):
		self.engine = engine
		self.__dict__.update(entries)

class Pass(PassCenterObject):
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)

	def download(self):
		self.data = self.engine.download_pass(self)
		return self.data

	def __repr__(self, *args, **kwargs):
		return '<Pass %s/%s>' % (self.passTypeIdentifier, self.serialNumber)


class PassCenterException(Exception):
	pass


class PassCenterApiException(PassCenterException):

	def __init__(self, status, msg=""):
		self.status = status
		self.msg = msg

	def __str__(self):
		return '[%s]: %s' % ( self.status, self.msg)


class PassCenterApiUnauthorizedException(PassCenterApiException):
	def __init__(self):
		super(self.__class__, self).__init__(401, """Unauthorized. 
			check your app key and make sure it has access to the template and pass type id""")


class PassCenterApiValidationException(PassCenterApiException):
	def __init__(self, response):
		msg = ''
		if response:
			msg = response['message']
			for error in response['errors']:
				msg += '; ' + error['field'] + ': ' + ', '.join(error['reasons'])

		super(self.__class__, self).__init__(422, msg)


if __name__ == '__main__':

	appkey = 'YOUR_APP_KEY'
	my_pass = LoyaltyPass.start(appkey)

	output = my_pass.list_programs()
	jsonFile = json.dumps(output,indent=4, sort_keys=True)
	print jsonFile


