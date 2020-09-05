import random

total_cash = 0

class model():
    round_cash = 30000
    round_count = 500
    low_range = 0.5
    high_range = 1.5
    const_num = 0


    def next(self, current_step=None, total_cash=None):
        rand_num = random.random() * (self.high_range - self.low_range) + self.low_range
        cash = int(((2 * self.round_cash / self.round_count) -
                    current_step * (2 * self.round_cash / self.round_count) / self.round_count) \
                   * rand_num + self.const_num)
        if cash < 100 and current_step < 100:
            cash = 102
        if current_step == self.round_count and total_cash < self.round_cash:
            cash = self.round_cash - total_cash
        print current_step, cash, total_cash
        return cash


if __name__ == "__main__":
    model()
    for i in range(500):
        cash = model().next(i+1, total_cash)
        total_cash += cash
