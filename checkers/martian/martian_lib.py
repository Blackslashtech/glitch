from pwn import *
from checklib import *

import random
import string

context.log_level = 'CRITICAL'

PORT = 9999

# global const
TCP_CONNECTION_TIMEOUT = 5
TCP_OPERATIONS_TIMEOUT = 7
ENERGY_TO_CHANGE_POWER_SCHEME = 85.0
alph = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789'
boss_msgs = { "You will die here. The sands will bury you and your memory will run out. All you can do is die worthy. You cannot survive in the sand, they will swallow you. And when you die, no one will regret. Surrender before it's too late and accept your death with dignity. Don't be a coward!" : 0, 
	"Nowhere to run!" : 1, 
	"You know my doom!! I will crush you" : 2 , 
	"You will stay here forever" : 3 }


class CheckMachine:
	sock = None
	_username = None

	def __init__( self, checker ):
		self.c = checker
		self.port = PORT

	def connection( self ):
		try:
			self.sock = remote( self.c.host, 
				self.port, 
				timeout = TCP_CONNECTION_TIMEOUT 
			)
		except Exception as e:
			self.sock = None
			self.c.cquit( Status.DOWN, 
				'Connection error',
				'CheckMachine.connection(): timeout connection!\nException: {}'.format( e )
			)

		self.sock.settimeout( TCP_OPERATIONS_TIMEOUT )

	def reg_user( self, username, password ):
		try:
			self.sock.recvuntil( b"> " ) # skip banner and menu
			self.sock.send( b"2\n" ) # send reg cmd
			self.sock.recvuntil( b": " ) # Enter username: 
			self.sock.send( username.encode() + b'\n' )

			buf = self.sock.recv()

			if b"User already exist!" in buf:
				self.c.cquit( Status.MUMBLE, 
					"Can't register a new user!", 
					"User is already registered!" 
				)

			self.sock.send( password.encode() + b'\n' )
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't register a new user!", 
				"Registration process timeout!\nException: {}".format( e ) 
			)

	def login( self, username, password ):
		try:
			self._username = username
			self.sock.recvuntil( b"> " )
			self.sock.send( b"1\n" )
			self.sock.recvuntil( b": " ) # Enter username: 
			self.sock.send( username.encode() + b'\n' )

			buf = self.sock.recv()

			if b"No such user!" in buf:
				return False, "{-} User not found!"

			self.sock.send( password.encode() + b'\n' )
			buf = self.sock.recvline()

			if b"Incorrect password" in buf:
				return False, "{-} Password is invalid!"

			return True, "OK"
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't login by registered user!", 
				"Login process timeout!\nException: {}".format( e ) 
			)

	def set_status( self, new_status ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"2\n" ) # change status cmd
			self.sock.recvuntil( b": " ) # Enter new status: 
			self.sock.send( new_status.encode() + b'\n' )

			buf = self.sock.recvline() 

			if not b"Status is changed" in buf:
				self.c.cquit( Status.MUMBLE, 
					"Can't change user status!",
					"Checker.set_status(): Status is not changed!\nException: {}".format( e ) 
				)

			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"10\n" )

			return True
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't change user status!", 
				"Change status process timeout!\nException: {}".format( e ) 
			)

	def read_book( self, count ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b'6\n' ) # read book cmd
			self.sock.recvuntil( b": " ) # enter count
			self.sock.send( str( count ).encode() + b'\n' ) 

			buf = self.sock.recvuntil( b"|--" )

			if b"{+} You read the book" in buf:
				return True
			else:
				self.c.cquit( Status.MUMBLE,
					"Read book return incorrect message!",
					"Checker.read_book(): incorrect read_book answer\nException: {}".format( e ) 
				)
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't read books!", 
				"Read book process timeout!\nException: {}".format( e ) 
			)

	def eat_potato( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"3\n" )

			buf = self.sock.recvline()

			if b"{-} You don't have" in buf:
				return False, b"{-} No potatoes!" 

			return True, "OK"
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't eat potato!", 
				"Eat potato process timeout!\nException: {}".format( e ) 
			)

	def get_user_stats( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"1\n" )

			buf = self.sock.recvuntil( b"{?}" )
			tmp_buf = buf.split( b'\n' )[1:-1]

			for i in range( 4 ):
				self.sock.recvuntil( b": " )
				self.sock.send( b"n\n" )

			stats = {}

			stats[ 'name' ]    		= tmp_buf[ 0 ].split( b": " )[ 1 ]
			stats[ 'status' ]  		= tmp_buf[ 1 ].split( b": " )[ 1 ]
			stats[ 'actions' ] 		= int( tmp_buf[ 2 ].split( b": " )[ 1 ], 10 )
			stats[ 'hp' ]      		= float( tmp_buf[ 3 ].split( b": " )[ 1 ] )
			stats[ 'hunger' ]  		= float( tmp_buf[ 4 ].split( b": " )[ 1 ] )
			stats[ 'thirst' ]  		= float( tmp_buf[ 5 ].split( b": " )[ 1 ] )
			stats[ 'stamina' ] 		= float( tmp_buf[ 6 ].split( b": " )[ 1 ] )
			stats[ 'intelligence' ] = float( tmp_buf[ 7 ].split( b": " )[ 1 ] )
			stats[ 'repair_skill' ] = float( tmp_buf[ 8 ].split( b": " )[ 1 ] )

			return stats
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't get user stats!", 
				"Get stats process timeout!\nException: {}".format( e ) 
			)

	def get_status( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"1\n" ) # view user stats

			buf = self.sock.recvuntil( b'{?}' )
			status = buf.split( b'\n' )[ 2 ][ 8 : ] # cut "Status: "

			for i in range( 4 ):
				self.sock.recvuntil( b": " )
				self.sock.send( b"n\n" )

			return status.decode()
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't get user status!", 
				"Get status process timeout!\nException: {}".format( e ) 
			)

	def get_home_stats( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"1\n" )
			self.sock.recvuntil( b"{?} Show home stats? [y\\n]: " )
			self.sock.send( b"y\n" )

			buf = self.sock.recvuntil( b"{?}" )
			tmp_buf = buf.split( b'\n' )[ 1:-1 ]

			for i in range( 3 ):
				self.sock.recvuntil( b": " )
				self.sock.send( b"n\n" )

			stats = {}

			stats[ 'hp' ] = float( tmp_buf[ 0 ].split( b": " )[ 1 ] )
			stats[ 'energy' ] = float(tmp_buf[ 1 ].split( b": " )[ 1 ] )
			stats[ 'temp' ] = int( tmp_buf[ 2 ].split( b": " )[ 1 ] )

			return stats
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't get home stats!", 
				"Get home stats process timeout!\nException: {}".format( e ) 
			)

	def repair_home( self ):
		try:
			home_stats = self.get_home_stats()
			energy = home_stats[ 'energy' ]

			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"8\n" )

			buf = self.sock.recvline()

			if b"{-} During the repair, you damaged the energy block" in buf:
				return True

			if b"The house has been successfully repaired!" not in buf:
				self.c.cquit( Status.MUMBLE,
					"House repair error!",
					"Home repair return invalid signature"
				)

			if energy < ENERGY_TO_CHANGE_POWER_SCHEME:
				self.sock.recvuntil( b": " ) # change power scheme
				self.sock.send( b"n\n" )

			return True
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't repair home!", 
				"Repair home process timeout!\nException: {}".format( e ) 
			)

	def go_to_next_day( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"9\n" ) # go to next day

			buf = self.sock.recvline()

			if b"Nothing happened" in buf:
				return True
			else:
				self.c.cquit( Status.MUMBLE,
					"Lol! You died!",
					"Nigth event: " + buf.decode()[5:]
				)
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't change day!", 
				"Change day process timeout!\nException: {}".format( e ) 
			)

	def close_connect( self ):
		try:
			self.sock.close()
			self.sock = None
		except:
			self.sock = None

	def safe_close_connection( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"11\n" ) # send exit cmd
			self.sock.close()

			self.sock = None
		except Exception as e:
			self.sock = None

	def save_file( self ):
		self.sock.recvuntil( b"[>] " )
		self.sock.send( b"10\n" ) # save file cmd

	def easy_raid( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"7\n" ) # make raid
			self.sock.recvuntil( b": " ) # choose difficult
			self.sock.send( b"1\n" ) # easy

			buf = self.sock.recvline()

			if b"{-} You do not have" in buf:
				return False, b"{-} No actions!"

			buf = self.sock.recvuntil( b'?\n' ).split( b'\n' )
			expr = buf[:-1][ -1 ].split( b' ' )[ 0 ]

			x1, y1 = expr.split( b'+' )

			answer = int( x1 ) + int( y1 )
			self.sock.send( str( answer ).encode() + b'\n' )

			buf = self.sock.recvline()

			if b"{+} You managed to open the chest and there you found:" not in buf:
				self.c.cquit( Status.MUMBLE,
					"Easy raid: code is not correct!",
					"Easy raid: Code is correct, but chest not opened!"
				)
			else:
				return True, "OK"
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't do easy raid!", 
				"Easy raid process timeout!\nException: {}".format( e ) 
			)
	
	def medium_raid( self ):
		try:
			# valid code 
			monster_hp = 120
			monster_attack = 12
			monster_regen = 8
			
			valid_code = monster_hp + monster_attack + monster_regen
			valid_code += int( self.get_user_stats()[ 'hp' ] )
			valid_code = valid_code << 2
			valid_code += int( self.get_user_stats()[ 'intelligence' ] )

			# ui part 
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"7\n" ) # make raid
			self.sock.recvuntil( b": " ) # choose difficult
			self.sock.send( b"2\n" ) # medium

			buf = self.sock.recvline()
			if b"{-} You do not have" in buf:
				return False, b"{-} No actions!"

			self.sock.recvuntil( b"> " )

			while True:
				self.sock.send( b"2\n" )

				self.sock.recvline()
				self.sock.recvline()

				buf = self.sock.recvline()
				valid_code += 13

				if b"{+++} You killed a monster!!!" in buf:
					break
				else:
					self.sock.recvuntil( b"> " )

			self.sock.recvuntil( b": " )
			self.sock.send( str( valid_code ).encode() + b'\n' )

			buf = self.sock.recvline()

			if b"{+} You managed to open the chest and there you found:" not in buf:
				self.c.cquit( Status.MUMBLE,
					"Medium raid: code is not correct!",
					"Medium raid: Code is correct, but chest not opened!"
				)
			else:
				return True, "OK"
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't do medium raid!", 
				"Medium raid process timeout!\nException: {}".format( e ) 
			)

	def make_valid_hard_raid_code( self, value ):
		res = ''

		# first part
		value &= 0xff
		crc = 0xffff

		data = value
		data ^= crc & 255
		data ^= ( data << 4 ) & 0xff

		t  = (((data << 8)& 0xffff) | ( (crc>>8) & 255 ) )
		t ^= (data >> 4) & 0xffff 
		t ^= ((data << 3) & 0xffff)

		buf = str( t ).zfill( 5 )
		res += str( buf ) + '-'

		# second part
		sym = ( value ^ 65 ) & 0x7f
		buf = 'aaaa' + chr( sym )

		res += str( buf ) + '-'

		# third part
		name_hash = hashlib.sha256( self._username.encode() ).hexdigest()

		buf = name_hash[ 8 ] 
		buf += name_hash[ 10 ]
		buf += name_hash[ 0 ]
		buf += name_hash[ 7 ]
		buf += name_hash[ 12 ]

		res += buf

		return res

	def hard_raid( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"7\n" ) # make raid
			self.sock.recvuntil( b": " ) # choose difficult
			self.sock.send( b"3\n" ) # medium

			buf = self.sock.recvline()
			if b"{-} You do not have" in buf:
				return False, "{-} No actions!"
			
			self.sock.recvuntil( b"Boss says: " )
			message = self.sock.recvuntil( b"\n" ).strip().decode()
			self.sock.recvuntil( b"> " )

			fight_sig = boss_msgs[ message ]

			while True:
				self.sock.send( b"3\n" )
				fight_sig += 3

				self.sock.recvline()
				message = self.sock.recvline().strip().decode()

				if "{+} Wooo" in message:
					break

				fight_sig += boss_msgs[ message[len("Boss says: "):] ]

				buf = self.sock.recvuntil( b"> " )

			self.sock.recvuntil( b": " ) # code
			valid_code = self.make_valid_hard_raid_code( fight_sig )
			self.sock.send( str( valid_code ).encode() + b'\n' )

			buf = self.sock.recvline()
			
			if b"{+} You managed to open the chest and there you found:" not in buf:
				self.c.cquit( Status.MUMBLE,
					"Hard raid: code is not correct!",
					"Hard raid: Code is correct, but chest not opened!"
				)
			else:
				return True, "OK"
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't do hard raid!", 
				"Hard raid process timeout!\nException: {}".format( e ) 
			)

	def view_trophy( self ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"1\n" )
			self.sock.recvuntil( b"{?} " )

			for i in range( 3 ):
				self.sock.recvuntil( b": " )
				self.sock.send( b"n\n" )

			buf = self.sock.recvuntil( b": " )
			
			if b"View trophy" not in buf:
				return False, "No trophy!"

			self.sock.send( b"y\n" )
			self.sock.recvuntil( b"> " )
			self.sock.send( b"1\n" ) # view
		
			for i in range( 3 ):
				self.sock.recvline()

			code = self.sock.recvline().strip().split( b": " )[ 1 ].decode()
			self.sock.recvuntil( b": " )
			self.sock.send( b"n\n" )

			return True, code
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't view trophy!", 
				"View trophy process timeout!\nException: {}".format( e ) 
			)

	def recycle_trophy( self, code ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"1\n" )
			self.sock.recvuntil( b"{?} " )

			for i in range( 3 ):
				self.sock.recvuntil( b": " )
				self.sock.send( b"n\n" )

			buf = self.sock.recvuntil( b": " )
			
			if b"View trophy" not in buf:
				return False, "No trophy!"

			self.sock.send( b"y\n" )
			self.sock.recvuntil( b"> " )
			self.sock.send( b"2\n" ) # recycle
			self.sock.recvuntil( b": " ) # enter code
			self.sock.send( code.encode() + b'\n' )

			buf = self.sock.recvline()

			if b"{+} The trophy was recycled and you got iron" not in buf:
				return False, "Recycle error!"

			self.sock.recvuntil( b"{?}" )
			self.sock.recvuntil( b": " )
			self.sock.send( b"n\n" )

			return True, code
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't recycle trophy!", 
				"Recycle trophy process timeout!\nException: {}".format( e ) 
			)

	def chek_runaway_hard_raid( self, data ):
		try:
			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"7\n" ) # make raid
			self.sock.recvuntil( b": " ) # choose difficult
			self.sock.send( b"3\n" ) # medium

			buf = self.sock.recvline()
			if b"{-} You do not have" in buf:
				return False, b"{-} No actions!"
			
			self.sock.recvuntil( b"Boss says: " )
			message = self.sock.recvuntil( b"\n" ).strip().decode()
			self.sock.recvuntil( b"> " )

			self.sock.send( b"4\n" )
			self.sock.recvline()

			buf = self.sock.recvuntil( b": " )

			if b"{?} You can say a few words last" not in buf:
				self.c.cquit( Status.MUMBLE,
					"No last message in hard raid!",
					"No last message in hard raid!"
				)

			self.sock.send( data.encode() + b'\n' )
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't runaway from hard raid!", 
				"Runaway from hard raid process timeout!\nException: {}".format( e ) 
			)

	def check_change_power_scheme( self ):
		try:
			home_stats = self.get_home_stats()
			energy = home_stats[ 'energy' ]

			self.sock.recvuntil( b"[>] " )
			self.sock.send( b"8\n" )

			buf = self.sock.recvline()

			if b"{-} During the repair, you damaged the energy block" in buf:
				return True

			if b"The house has been successfully repaired!" not in buf:
				self.c.cquit( Status.MUMBLE,
					"House repair error!",
					"Home repair return invalid signature"
				)

			if energy < ENERGY_TO_CHANGE_POWER_SCHEME:
				self.sock.recvuntil( b": " ) # change power scheme
				self.sock.send( b"y\n" )

				for i in range( 6 ):
					self.sock.recvuntil( b": " )
					self.sock.send( str( random.randint( 100, 300 ) ).encode() + b'\n' )

				self.sock.recvuntil( b": " )
				self.sock.send( b"1337\n" )

				buf = self.sock.recvline()

				if b"New scheme is:" not in buf:
					self.c.cquit( Status.MUMBLE,
						"Power shceme changing error!",
						"Power shceme changing error!"
					)

				buf = self.sock.recvuntil( b"\n|--" )

				for i in range( 6 ):
					msg = "voltage[{}]".format( i )

					if msg not in buf.decode():
						self.c.cquit( Status.MUMBLE,
						"Power shceme changing error!",
						"Power shceme changing error!"
					)
		except Exception as e:
			self.close_connect()
			self.c.cquit( Status.MUMBLE, 
				"Can't change power scheme!", 
				"Change power scheme process timeout!\nException: {}".format( e ) 
			)
 		