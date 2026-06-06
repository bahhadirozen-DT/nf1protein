# simulations/confinement_analyzer.py
"""
Structure-Informed Stability & Stochastic Escape Analyzer Engine
-----------------------------------------------------------------
Bu modül, asimetrik sinyal manifoldlarının Lyapunov kararlılığını ve
hücresel gürültü (stokastik) altında kaçış olasılıklarını hesaplar.
"""
import numpy as np

class GlobalStabilityEngine:
    def __init__(self, R=1.58, gamma=1.45, r=1.0, n=2.0, K=1.0):
        self.R = R
        self.gamma = gamma
        self.r = r
        self.n = n
        self.K = K
        self.lambda_damp = 0.8
        self.nonlinear_drag = 0.3

    def compute_system_vector_field(self, x, y):
        hill = (x**self.n) / (self.K**self.n + x**self.n) if x > 0 else 0
        asymmetric_radius = (x**2) / self.gamma + (y**2) * self.gamma
        dxdt = y
        dydt = -self.r * x + (self.R**2 - asymmetric_radius) * y * hill - (self.lambda_damp * y) - (self.nonlinear_drag * (y**3))
        return dxdt, dydt

    def calculate_lyapunov_derivative(self, X, Y):
        asymmetric_radius = (X**2) / self.gamma + (Y**2) * self.gamma
        dV_dx = 2.0 * (asymmetric_radius - self.R**2) * (X / self.gamma)
        dV_dy = 2.0 * (asymmetric_radius - self.R**2) * (Y * self.gamma)
        
        V_dot = np.zeros_like(X)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                dxdt, dydt = self.compute_system_vector_field(X[i,j], Y[i,j])
                V_dot[i,j] = dV_dx[i,j] * dxdt + dV_dy[i,j] * dydt
        return V_dot

    def run_stochastic_escape_test(self, sigma=0.5, num_trials=150, T=40, dt=0.02):
        N = int(T / dt)
        escape_count = 0
        escape_threshold = self.R * 1.5 
        
        for trial in range(num_trials):
            x, y = self.R * np.sqrt(self.gamma), 0.0 
            for step in range(N):
                dxdt, dydt = self.compute_system_vector_field(x, y)
                x += dxdt * dt + sigma * np.random.normal(0, np.sqrt(dt))
                y += dydt * dt + sigma * np.random.normal(0, np.sqrt(dt))
                
                current_radius = np.sqrt((x**2)/self.gamma + (y**2)*self.gamma)
                if current_radius > escape_threshold:
                    escape_count += 1
                    break 
        return (escape_count / num_trials) * 100
