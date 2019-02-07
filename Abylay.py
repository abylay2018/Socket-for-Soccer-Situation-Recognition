
from scipy import *
from scipy.linalg import *

# runge_kutta1 is Euler's method:

def runge_kutta1( F, x, h ) : 
   k1 = F( x ) 

   return x + h * k1 

def runge_kutta21(F, x, h) :
   k1 = F( x )
   k2 = F( x + h * k1 )

   return x + h * ( 0.5 * k1 + 0.5 * k2 )

def runge_kutta22(F, x, h) :
   k1 = F( x )
   k2 = F( x + 0.5 * h * k1 )

   return x + h * k2
   
def runge_kutta31(F, x, h) :
   k1 = F( x )
   k2 = F( x + h * (2.0/3.0) * k1 )
   k3 = F( x + h * ( (1.0/3.0) * k1 + (1.0/3.0) * k2 ) )

   return x + h * ( (1.0/4.0) * k1 + (3.0/4.0) * k3 )

def runge_kutta41(F, x, h) :
   k1 = F( x );
   k2 = F( x + 0.5 * h * k1 )
   k3 = F( x + 0.5 * h * k2 )
   k4 = F( x + h * k3 )

   return x + ( 1.0 / 6.0 ) * h * ( k1 + 2.0 * k2 + 2.0 * k3 + k4 )

def runge_kutta4_kuntzmann(F, x, h) :
   k1 = f( x )
   k2 = f( x + h * (2.0/5.0) * k1 )
   k3 = f( x + h * ( (-3.0/20.0) * k1 + (3.0/4.0) * k2 ) )
   k4 = f( x + h * ( (19.0/44.0) * k1 + (-15.0/44.0) * k2 + 
                       (40.0/44.0) * k3 ) )

   return x + h * ( (55.0/360.0) * k1 + (125.0/360.0) * k2 +
                    (125.0/360.0) * k3 + (55.0/360.0) * k4 )

def runge_kutta5(F, x, h) :
   k1 = F( x )
   k2 = F( x + h * (1.0/4.0) * k1 )
   k3 = F( x + h * ( (1.0/8.0) * k1 + (1.0/8.0) * k2 ) )
   k4 = F( x + h * (1.0/2.0) * k3 )
   k5 = F( x + h * ( (3.0/16.0) * k1 + (-3.0/8.0) * k2 +
                       (3.0/8.0) * k3 + (9.0/16.0) * k4 ) )
   k6 = F( x + h * ( (-3.0/7.0) * k1 + (8.0/7.0) * k2 +
                       (6.0/7.0) * k3 + (-12.0/7.0) * k4 + 
                       (8.0/7.0) * k5 ) )
      
   return x + h*(   ( 7.0 / 90.0 ) * k1 + ( 32.0 / 90.0 ) * k3 + ( 12.0 / 90.0 ) * k4 + ( 32.0 / 90.0 ) * k5 + ( 7.0 / 90.0 ) * k6 )

def approx( h = 2.0E-6 ) :
   print( "testing Runge-Kutta methods on the catenary" )

   x0 = 0.0
   x1 = 1.0

   mu = 2.0

   s0 = array( [ 1.0 / mu, 0.0 ] )

   p = s0
   x = x0

   def cat( p ) :
      return array( [ p[1], mu * sqrt( 1.0 + p[1] * p[1] ) ] )

   while x + h < x1 :
      p = runge_kutta41( cat, p, h )
      x += h

   p = runge_kutta41( cat, p, x1 - x )
   x = x1

   print( "h = ", h )
   print( "final value = ", p )

   expected = array( [ cosh( mu * x1 ) / mu, sinh( mu * x1 ) ] )
   error = p - expected

   print( "error = ", error )

'''
  TABLE:
       ___________________________________________________
      |_______h_______|____________error_________________| 
      |               |                                  |
Euler |     0.001     |     [-0.00304834 -0.00497444]    |
      |_______________|__________________________________|
      |               |                                  |
Heun  |     0.001     | [-1.03556852e-06 -1.38790976e-06]|
      |_______________|__________________________________|
Stand.|               |                                  |
Runge |     0.001     | [-1.67421632e-13 -2.38031816e-13]|
Kutta |_______________|__________________________________|
      |               |                                  |
Euler |     0.002     |     [-0.00608604 -0.00992802]    |
      |_______________|__________________________________|
      |               |                                  |
Heun  |     0.002     | [-4.13730925e-06 -5.54565811e-06]|
      |_______________|__________________________________|
Stand.|               |                                  |
Runge |     0.002     | [-2.66120459e-12 -3.72901710e-12]|
Kutta |_______________|__________________________________|
      |               |                                  |
Euler |     0.004     |     [-0.01212979 -0.01977312]    |
      |_______________|__________________________________|
      |               |                                  |
Heun  |     0.004     | [-1.65094891e-05 -2.21345750e-05]|
      |_______________|__________________________________|
Stand.|               |                                  |
Runge |     0.004     | [-4.24467128e-11 -5.95541394e-11]|
Kutta |_______________|__________________________________|

'''

'''
WHICH IS FASTER???

Values in the table indicate the time spent for various method executions
                  ______________________________________________________________
                 |__________PYTHON__________|______________C++_________________|
                 |                          |                                  |
Euler(h = 6.0E-5)|   0.6506086219999567s    |             0.007s               |
                 |__________________________|__________________________________|
                 |                          |                                  |
Heun(h = 4.0E-6) |   25.846964964681817s    |             0.023s               |
                 |__________________________|__________________________________|   
Stand.           |                          |                                  |
Runge(h = 2.0E-6)|   96.10596629200009s     |             0.070s               |
Kutta            |__________________________|__________________________________|

In som settings C++ is faster than python about 1000 times

As we see, C++ is much faster than Python. Especially when h is decreasing, discrepancy between 
execution times of Python and C++ is being large (the reason is that loop iteration becoming large, 
and it is running slower in python code than C++ code, one of the main reasons of this is that python is dynamic language.
this means that when assigning value in every iteration in loop, dynamic typing of p takes more time than 
assigning for p in c++ which is not dynamic). 
Therefore, when h was not so small, even if C++ was
faster, difference was not much high as shown in table above. 

Also, I think that C== is much faster because it has explicit control over memory allocations(constructors, 
copy constr., movings, etc.) and it has compiler which prevents from checking during execution(interpreter which 
rakes more time than compiler).
.

'''
