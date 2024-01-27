import numpy
import scipy

class Predictor:

    # battery_capacity in [Wh]
    # dt step in [s]
    def __init__(self, battery_capacity, dt):

        self.battery_capacity = battery_capacity
        self.dt  = dt

        # discrete battery model
        # x(n+1)  = x(n) + k*u(n)

        self.mat_a = numpy.zeros((1, 1))
        self.mat_b = numpy.zeros((1, 1))


        self.mat_a[0][0] = 1.0
        self.mat_b[0][0] = dt*(1.0/battery_capacity)*(1.0/3600.0)

        
        #model noise covariance
        q = (10**-6)*numpy.eye(self.mat_a.shape[0])
        
        #measurement noise covariance
        r = (10**-4)*numpy.eye(self.mat_a.shape[0])
        
        #compute Kalman gain
        self.kalman_gain = self._solve_kalman_gain(self.mat_a, numpy.eye(self.mat_a.shape[0]), q, r)

        print(self.kalman_gain)

        #initial prediction
        self.x_hat = numpy.zeros(self.mat_a.shape)

    # c_measured : meassured charge status in [%]
    # c_req : required charge status in [%]
    # returns time in seconds, until battery charge c_measured reach required charge c_req
    # if not reached in prediction horizon, returns -1
    def predict_time(self, p_in, c_measured, c_req, max_hours = 12):
        
        n_steps = int(max_hours*3600/self.dt)

        c_prediction = self.step(p_in, c_measured, n_steps)

        th = numpy.where(c_prediction > c_req)[0]

        if len(th) > 0:
            time_until_req = th[0]*self.dt
        else:
            time_until_req = - 1

        return time_until_req, c_prediction


    def step(self, p_in, c_measured, n_steps):

        u = p_in*numpy.ones((1, 1))
        x = c_measured*numpy.ones((1, 1))

        #kalman prediction and correction
        self.x_hat = self.mat_a@self.x_hat + self.mat_b@u + self.kalman_gain@(x - self.x_hat)

        # prediciton only, n-steps
        result = numpy.zeros(n_steps)

        #x_pred = self.x_hat.copy()
        x_pred = x.copy()
        for n in range(n_steps):
            x_pred = self.mat_a@x_pred + self.mat_b@u
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

    battery_capacity = 100 # Wh

    max_hours = 12

    dt = 0.7
    predictor = Predictor(battery_capacity, dt)

    time_until_req, c_prediction = predictor.predict_time(2.0, 90., 99.9, max_hours) 

    print("time until charged = ", time_until_req/3600.0)

    t_result = numpy.arange(c_prediction.shape[0])*dt/3600

    plt.clf()
    plt.plot(t_result, c_prediction)
    plt.grid()
    plt.show()