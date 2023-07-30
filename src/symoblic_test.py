import sympy as sym
M = sym.Symbol('M')
p = sym.Symbol('p')
b = sym.Symbol('b')

reward_if_call = p*(M+2*b) - b
desired_bet = sym.solveset(reward_if_call, b)

reward = reward_if_call.subs(b, desired_bet.inf)
