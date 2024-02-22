#!/usr/bin/env python3

from gevent import monkey

monkey.patch_all()

import sys
import os
import string
import random
import copy

from checklib import *

argv = copy.deepcopy( sys.argv )
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from martian_lib import *

# my utils
def idg( size = 8, chars = alph ):
	return ''.join( random.choice( chars ) for _ in range( size ) )

def generate_correct_random_name():
	return idg( 1, string.ascii_uppercase ) + idg()

def generate_correct_random_password():
	password = idg( 1, string.ascii_uppercase )

	tmp  = idg( 4, string.ascii_uppercase ) 
	tmp += idg( 4, string.ascii_lowercase ) 
	tmp += idg( 4, string.digits )
	
	tmp = list( tmp )

	random.shuffle( tmp )
	password += ''.join( tmp )

	return password

class Checker(BaseChecker):
	def __init__(self, *args, **kwargs):
		super(Checker, self).__init__(*args, **kwargs)
		self.mch = CheckMachine(self)

	def action(self, action, *args, **kwargs):
		super( Checker, self ).action( action, *args, **kwargs )

	def check( self ):
		self.mch.connection()

		# check register and login
		username = generate_correct_random_name()
		password = generate_correct_random_password()

		self.mch.reg_user( username, password )
		logined, err_msg = self.mch.login( username, password )

		if not logined:
			self.cquit( Status.MUMBLE, 
				"Can't login by registered user",
				"Checker.login(): err_msg = {}".format( err_msg )
			)

		# test read book
		_stats = self.mch.get_user_stats()
		start_int = _stats[ 'intelligence' ]

		if self.mch.read_book( 1 ):
			# Check int diff
			_stats = self.mch.get_user_stats()

			if ( _stats[ 'intelligence' ] - start_int ) != 35:
				self.cquit( Status.MUMBLE, 
					"Incorrect intelligence changing!",
					"Checker.read_book(): INT changing error!"
				)
		else:	
			self.cquit( Status.MUMBLE, 
				"Read book error!",
				"Checker.read_book(): basic read book"
			)

		# just farm book reading to increase INT and get some cap
		self.mch.read_book( 20 )

		# go to next day
		self.mch.go_to_next_day()
 
		_stats = self.mch.get_user_stats()
		actions = _stats[ 'actions' ]

		# check action-points changing
		if actions != 24:
			self.cquit( Status.MUMBLE,
				"Actions difference error!",
				"Recovering points when switching to another day does not work correctly"
			)

		# repair home
		self.mch.repair_home()

		# test easy raid
		# go to raid
		retcode, err_msg = self.mch.easy_raid()
		
		if not retcode:
			self.cquit( Status.MUMBLE,
				"Can't do easy raid!",
				"No actions to make easy raid!"
			)

		# farm INT and potatoes
		self.mch.go_to_next_day()

		# test medium raid
		retcode, err_msg = self.mch.medium_raid()
		
		if not retcode:
			self.cquit( Status.MUMBLE,
				"Can't do medium raid!",
				"No actions to make medium raid!"
			)

		# regen HP
		for i in range( 2 ):
			ret_code, _ = self.mch.eat_potato()

			if not retcode:
				self.cquit( Status.MUMBLE,
					"No potatoes, but many raids already completed!",
					"No potatoes, but many raids already completed!"
				)

		self.mch.go_to_next_day()
		
		# test hard raid
		retcode, _ = self.mch.hard_raid()
			
		if not retcode:
			self.cquit( Status.MUMBLE,
				"Can't do hard raid!",
				"No actions to make hard raid!"
			)

		# view trophy and recycle it
		retcode, msg = self.mch.view_trophy()

		if not retcode:
			self.cquit( Status.MUMBLE,
				"Can't view trophy",
				"Can't view trophy, msg: {}".format( msg ) 
			)
		
		valid_code = msg
		retcode, msg = self.mch.recycle_trophy( valid_code )

		if not retcode:
			self.cquit( Status.MUMBLE,
				"Can't recycle trophy",
				"Can't recycle trophy, msg: {}".format( msg )
			)

		# check runaway in hard raid
		self.mch.go_to_next_day()
		self.mch.chek_runaway_hard_raid( idg( 8 ) )

		# check power scheme changing
		self.mch.check_change_power_scheme()

		self.mch.save_file()
		self.mch.safe_close_connection()
		self.cquit( Status.OK )

	def put( self, flag_id, flag, vuln ):
		if vuln == '1':
			username = generate_correct_random_name()
			password = generate_correct_random_password()

		else:
			username = "Item" + idg()
			password = generate_correct_random_password()

		self.mch.connection()
		self.mch.reg_user( username, password )

		logined, err_msg = self.mch.login( username, password )

		if not logined:
			self.cquit( Status.MUMBLE, 
				"Can't login by registered user",
				"Checker.login(): err_msg = {}".format( err_msg )
			)

		self.mch.set_status( flag )
		self.mch.safe_close_connection()

		self.cquit( Status.OK, f'{username}:{password}' ) 

	def get( self, flag_id, flag, vuln ):
		username, password = flag_id.split( ":" )

		self.mch.connection() 
		logined, err_msg = self.mch.login( username, password )

		if not logined:
			self.cquit( Status.CORRUPT,
				"Can't login and flag check!",
				"Checker.login(): err_msg = {}".format( err_msg ) 
			)

		status = self.mch.get_status()

		if status != flag:
			self.cquit( Status.CORRUPT,
				"Incorrect flag",
				"Checker.get_status(): valid_flag = {}, user_flag = {}".format(
					flag, status )
			)

		self.cquit( Status.OK )

if __name__ == '__main__':
	c = Checker(argv[2])

	try:
		c.action(argv[1], *argv[3:])
	except c.get_check_finished_exception():
		cquit(Status(c.status), c.public, c.private)