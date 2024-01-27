import numpy
import scipy

class Predictor:

    # battery_capacity in [Wh]
    # dt step in [s]
    def __init__(self, battery_capacity, dt):

        self.battery_capacity = battery_capacity*3600.0
        self.dt  = dt

        # discrete battery model
        # x(n+1)  = x(n) + k*u(n)

        self.mat_a = numpy.zeros((1, 1))
        self.mat_b = numpy.zeros((1, 1))


        self.mat_a[0][0] = 1.0
        self.mat_b[0][0] = dt

        
        #model noise covariance
        q = (10**-6)*numpy.eye(self.mat_a.shape[0])
        
        #measurement noise covariance
        r = (10**-4)*numpy.eye(self.mat_a.shape[0])
        
        #compute Kalman gain
        self.kalman_gain = self._solve_kalman_gain(self.mat_a, numpy.eye(self.mat_a.shape[0]), q, r)

        print(self.kalman_gain)

        #initial prediction
        self.x_hat = None 
    
    # p_in : input power in [W]
    # sc_measured : meassured state of charge in [%]
    # sc_req      : required state of charge in  [%]
    #
    # returns 
    #   - time in seconds, until battery reach required state of charge
    #   - if not reached in prediction horizon, returns -1
    def predict_time(self, p_in, sc_measured, sc_req, max_hours = 12):
        n_steps = int(max_hours*3600/self.dt)

        q_measured   = self.battery_capacity*sc_measured/100.0

        q_prediction = self.predict(p_in, q_measured, n_steps)

        # convert stored energy into state of charge
        c_prediction = 100.0*(q_prediction/self.battery_capacity)
    
        th = numpy.where(c_prediction > sc_req)[0]

        if len(th) > 0:
            time_until_req = th[0]*self.dt
        else:
            time_until_req = - 1

        return time_until_req, c_prediction

    '''
    predict battery state
    input:
        p_in        : input power in W
        q_measured  : batery charge in Ws (Joules)
        n_steps     : prediction steps count

    returns:
        prediction stored charge, shape (n_steps, )
    '''
    def predict(self, p_in, q_measured, n_steps):

        u = p_in*numpy.ones((1, 1))
        x = q_measured*numpy.ones((1, 1))

        #intial state
        if self.x_hat is None:
            self.x_hat = x.copy()

        #kalman prediction and correction
        self.x_hat = self.mat_a@self.x_hat + self.mat_b@u + self.kalman_gain@(x - self.x_hat)
        self.x_hat = numpy.clip(self.x_hat, 0.0, self.battery_capacity)

        # prediciton only, n-steps
        result = numpy.zeros(n_steps)

        x_pred = self.x_hat.copy()
        for n in range(n_steps):
            x_pred = self.mat_a@x_pred + self.mat_b@u
            x_pred = numpy.clip(x_pred, 0.0, self.battery_capacity)
            result[n] = x_pred[0][0]

        return result

    '''
    compute kalman gain matrix for observer : 
    x_hat(n+1) = Ax_hat(n) + Bu(n) + K(y(n) - Cx_hat(n))
    '''
    def _solve_kalman_gain(self, a, c, q, r):
        p = scipy.linalg.solve_discrete_are(a.T, c.T, q, r) 
        k = p@c.T@scipy.linalg.inv(c@p@c.T + r)

        return k



import matplotlib.pyplot as plt

if __name__ == "__main__":

    battery_capacity = 8000 # Wh

    max_hours = 12

    dt = 10.0
    predictor = Predictor(battery_capacity, dt)

    time_until_req, c_prediction = predictor.predict_time(3000.0, 18.0, 90.0, max_hours) 

    print("time until charged = ", time_until_req/3600.0)

    t_result = numpy.arange(c_prediction.shape[0])*dt/3600

    plt.clf()
    plt.plot(t_result, c_prediction)
    plt.grid()
    plt.show()