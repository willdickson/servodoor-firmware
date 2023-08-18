import math

class DynamicDoor:
    """
    Implements a ramp trajectory from current state (pos, vel) to the given set
    point position set_pos (vel=0). The ramp trajectory implements a constant
    acceleration -> constant -> velocity -> constant deceleration type
    trajectory. The set point can be re-set at any time.  
    """

    def __init__(self, dt=0.01, pos=0.0, set_pos=0.0, max_vel=2000.0, max_acc=3000.0):

        self.dt = dt                  # Time step for tracjetory updates
        self.max_vel = abs(max_vel)   # Maximum allowed velocity
        self.max_acc = abs(max_acc)   # Maximum allowed acceleration

        self.pos = pos    # Current position
        self.vel = 0.0    # Current velocity
        self.pos0 = pos   # Initial position (set every time set_pos changes)
        self.vel0 = 0.0   # Initial velocity (set every time set_pos changes)
        self.acc = 0.0    # Current acceleration

        self.ind = 0      # Current index position in planned trajectory
        self.num_acc = 0  # Number of acceleration time steps in trajectory 
        self.num_vel = 0  # Number of constant velocity time steps in trajectory
        self.num_dec = 0  # Number of deceleration time steps in trajectory

        self.set_pos = set_pos       # Set point/target position.
        self.adj_acc = self.max_acc  # Adjusted (max) acceleration. Accounts for 
                                     # discrete time steps. 

    def update(self):
        """
        Called every time step dt. Updates the current ind, pos, vel and acc. 
        """
        sgn = sign(self.set_pos - self.pos)
        self.ind = min(self.ind+1, self.num_acc + self.num_vel + self.num_dec+1)
        if self.ind <= self.num_acc:
            # Acceleration phase of trajectory
            next_pos = self.pos0 + self.dpos_acc(self.ind)
        elif self.ind <= self.num_acc + self.num_vel:
            # Constant velocity phase of trajectory
            dpos_acc = self.dpos_acc(self.num_acc)
            dpos_vel = self.dpos_vel(self.ind - self.num_acc)
            next_pos = self.pos0 + dpos_acc + dpos_vel
        elif self.ind <= self.num_acc + self.num_vel + self.num_dec:
            # Deceleration phase of trajectory
            dpos_acc = self.dpos_acc(self.num_acc)
            dpos_vel = self.dpos_vel(self.num_vel)
            dpos_dec = self.dpos_dec(self.ind - self.num_acc - self.num_vel)
            next_pos = self.pos0 + dpos_acc + dpos_vel + dpos_dec
        else:
            # At set point. 
            next_pos = self.set_pos
        next_vel = (next_pos - self.pos)/self.dt
        next_acc = (next_vel - self.vel)/self.dt
        self.pos = next_pos
        self.vel = next_vel
        self.acc = next_acc

    @property
    def sign(self):
        """ Returns the sign of the direction to the set point """
        return sign(self.set_pos - self.pos0)

    @property
    def err(self):
        """ Returns the error (signed distance) between position and set point """
        return self.set_pos - self.pos

    @property
    def at_set_pos(self):
        """ Returns True if at set_pos, False otherwise """
        return self.ind >= (self.num_acc + self.num_vel + self.num_dec + 1)

    @property
    def peak_vel(self):
        """ Returns the peak velocity of trajectory """
        t = self.num_acc*self.dt
        acc = self.sign*self.adj_acc
        peak_vel = self.vel0 + acc*t
        return peak_vel

    def dpos_acc(self, n):
        """ Returns change in position when accelerating for n time steps """
        t = n*self.dt
        acc = self.sign*self.adj_acc
        dpos = self.vel0*t + 0.5*acc*t**2
        return dpos

    def dpos_vel(self,n):
        """ 
        Returns change in position when traveling at peak_vel for n time steps 
        """
        t = n*self.dt
        vel = self.peak_vel
        dpos = vel*t
        return dpos

    def dpos_dec(self, n):
        """ 
        Returns change in position when decelerating from peak_vel for n time steps 
        """
        t = n*self.dt
        vel = self.peak_vel
        acc = self.sign*self.adj_acc
        dpos = vel*t - 0.5*acc*t**2 
        return dpos

    @property
    def set_pos(self):
        """ Returns the set point position """
        return self._set_pos

    @set_pos.setter
    def set_pos(self, val):
        """ Set/change the set point position"""
        self._set_pos = val
        sgn = self.sign
        param = ramp_trajectory(
                self.dt,
                self.pos,
                self.vel, 
                self.set_pos,
                self.max_vel,
                self.max_acc,
                )
        self.num_acc = param['num_acc']
        self.num_vel = param['num_vel']
        self.num_dec = param['num_dec']
        self.adj_acc = param['adj_acc']
        self.ind = 0
        self.acc = 0.0
        self.pos0 = self.pos
        self.vel0 = self.vel

# ------------------------------------------------------------------------------------

def ramp_trajectory(dt, pos, vel, set_pos, max_vel, max_acc):
    """
    Returns the parameters for a ramp trajectory from current position/velocity
    (pos,vel) to the set point (set_pos,0.0) position/velocity. The ramp
    trajectory consists of a constant acceleration, to constant velocity,
    followed by a constant deceleration. The acceleration and deceleration
    parameters are set by max_acc and max_vel respectively. 
    """
    sgn = sign(set_pos - pos)
    # Adjust signs so always solving case where pos < set_pos
    _pos = sgn*pos
    _vel = sgn*vel
    _set_pos = sgn*set_pos

    # Get dpos accelerating from _vel to _max_vel
    dpos_acc = (max_vel**2 - _vel**2)/(2.0*max_acc)
    dpos_dec = (max_vel**2)/(2.0*max_acc)
    dpos_acc_dec = dpos_acc + dpos_dec
    dpos_total = _set_pos - _pos

    # Select case based on weather or not we will reach max_vel and will have 
    # a constant velocity section in the trajectory 
    if dpos_total > dpos_acc_dec:
        peak_vel = max_vel
        dpos_vel = dpos_total - dpos_acc_dec
        # Get times of acceleration, constant velocity and deceleration sections
        t_acc = (max_vel - _vel)/max_acc
        t_vel = dpos_vel/max_vel
        t_dec = max_vel/max_acc
    else:
        # We don't have a constant velocity section in the trajectory
        peak_vel = math.sqrt(max_acc*dpos_total + 0.5*_vel**2)
        dpos_acc = (peak_vel**2 - _vel**2)/(2.0*max_acc)
        dpos_dec = (peak_vel**2)/(2.0*max_acc)
        dpos_vel = 0.0

        # Get times of acceleration and deceleration sections
        t_acc = (peak_vel - _vel)/max_acc
        t_vel = 0.0
        t_dec = peak_vel/max_acc

    # Get number of acceleration, constant velocity and deceleration steps
    num_acc = int(round(t_acc/dt))
    num_vel = int(round(t_vel/dt))
    num_dec = int(round(t_dec/dt))

    # Discrete time stepping will prevent use from exactly hitting the set_pos
    # target.  Adjust max_acc slightly so that we exactly hit set_pos exactly
    t_acc = num_acc*dt
    t_vel = num_vel*dt
    t_dec = num_dec*dt
    if (t_acc + t_vel + t_dec > 0):
        adj_acc = 2*(dpos_total - _vel*(t_acc + t_vel + t_dec))
        adj_acc /= t_acc**2 + 2*t_acc*t_vel + 2*t_acc*t_dec  - t_dec**2
    else:
        adj_acc = max_acc
    
    param = {
            'num_acc': num_acc,
            'num_vel': num_vel, 
            'num_dec': num_dec,
            'adj_acc': adj_acc,
            }

    return param 

def sign(x):
    return 1 if x >=0 else -1


