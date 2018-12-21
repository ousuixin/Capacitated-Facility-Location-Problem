import random
import math

INSTANCE_NUMBER = 1  # 测试的时候是1，实际上一共71个测试例子
LOOP_LENGTH = 1000
MAX_TEMPERATURE = 100
MIN_TEMPERATURE = 0.5
ATTENUATION_QUOTIENT = 0.99


class LocalSearchSol:

    def __init__(self, filename):
        self.filename = filename
        self.facility_number = 0
        self.customer_number = 0
        self.F_capacity = []
        self.facility_capacity = []                             # 变量
        self.facility_open_cost = []
        self.customer_demand = []
        self.distance_to_facility = []
        self.read_file()

        self.facility_open_list = [0]*self.facility_number      # 变量

        self.customer_allocation = [0]*self.customer_number     # 变量

        self.total_cost = 0                                     # 变量

        self.best_total_cost = 0
        self.best_allocation = [0]*self.customer_number

    def read_file(self):
        fp = open(self.filename)
        problem_size = fp.readline().split()
        self.facility_number = int(problem_size[0])
        self.customer_number = int(problem_size[1])

        for i in range(0, self.facility_number):
            facility_info = fp.readline().split()
            self.F_capacity.append(int(facility_info[0]))
            self.facility_capacity.append(int(facility_info[0]))
            self.facility_open_cost.append(int(facility_info[1]))

        for i in range(0, int(self.customer_number / 10)):
            demand_info = fp.readline().split()
            for j in range(0, 10):
                self.customer_demand.append(int(demand_info[j][0:len(demand_info[j])-1]))

        for i in range(0, int(self.customer_number)):
            temp_distance = []
            for j in range(0, int(self.facility_number / 10)):
                distance_info = fp.readline().split()
                for k in range(0, 10):
                    temp_distance.append(int(distance_info[k][0:len(distance_info[k])-1]))
            self.distance_to_facility.append(temp_distance)

    def open_facility(self):
        for i in range(0, self.facility_number):
            self.facility_open_list[i] = 0
        self.total_cost = 0
        for i in range(0, self.facility_number):
            if random.random() < 0.75:
                self.facility_open_list[i] = 1
                self.total_cost += self.facility_open_cost[i]

    def alloc_customer_randomly(self):
        for i in range(0, self.customer_number):
            count = 0
            while True:
                if count == self.facility_number:
                    return False
                count += 1
                choose_facility = random.randint(0, self.facility_number - 1)
                if self.facility_open_list[choose_facility] == 1 and self.facility_capacity[choose_facility] >= self.customer_demand[i]:
                    self.facility_capacity[choose_facility] -= self.customer_demand[i]
                    self.total_cost += self.distance_to_facility[i][choose_facility]
                    self.customer_allocation[i] = choose_facility
                    break

        return True

    def generate_neighbor_by_swap_customer(self):               # 产生方式是交换两个不同工厂的顾客，缺点是无法开厂，应配合1使用
        for i in range(0, 100):                                 # 在局部搜索中，这一句改为for i in range(0, 1000)更好
            customer_1 = random.randint(0, self.customer_number - 1)
            customer_2 = random.randint(0, self.customer_number - 1)
            facility_cus_1 = self.customer_allocation[customer_1]
            facility_cus_2 = self.customer_allocation[customer_2]
            if customer_1 == customer_2 or facility_cus_1 == facility_cus_2:
                continue                                        # 产生的是这个点本身而不是邻居，重来
            if self.facility_capacity[facility_cus_1] + self.customer_demand[customer_1] - \
                    self.customer_demand[customer_2] < 0 or self.facility_capacity[facility_cus_2] + \
                    self.customer_demand[customer_2] - self.customer_demand[customer_1] < 0:
                continue                                        # 交换被拒绝，有一个工厂的容量不足
            # 交换操作可进行，计算总花费是否减少，如果减少则接受邻居解，总花费仅仅包括到工厂距离
            cost_before = self.distance_to_facility[customer_1][facility_cus_1] \
                          + self.distance_to_facility[customer_2][facility_cus_2]
            cost_after = self.distance_to_facility[customer_1][facility_cus_2] \
                          + self.distance_to_facility[customer_2][facility_cus_1]
            if cost_before <= cost_after:                       # 邻居解不能接受
                return False

            self.facility_capacity[facility_cus_1] = self.facility_capacity[facility_cus_1] + \
                                                     self.customer_demand[customer_1] - self.customer_demand[customer_2]
            self.facility_capacity[facility_cus_2] = self.facility_capacity[facility_cus_2] + \
                                                     self.customer_demand[customer_2] - self.customer_demand[customer_1]
            self.customer_allocation[customer_1] = facility_cus_2
            self.customer_allocation[customer_2] = facility_cus_1
            self.total_cost = self.total_cost - cost_before + cost_after

            return True

    def generate_neighbor(self):
        # 在之前的基础上修改open list
        facility = random.randint(0, self.facility_number-1)
        self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
        # 更新total cost
        self.total_cost = 0
        for i in range(0, self.facility_number):
            if self.facility_open_list[i] == 1:
                self.total_cost += self.facility_open_cost[i]
        if self.total_cost == 0:
            self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
            return False
        # 还原capacity
        for i in range(0, self.facility_number):
            self.facility_capacity[i] = self.F_capacity[i]
        # 重新分配顾客
        if not self.alloc_customer_randomly():
            self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
            return False

        # 开始寻找该open list对应的最好cost
        for i in range(0, LOOP_LENGTH):
            self.generate_neighbor_by_swap_customer()

        # 如果该open list对应的最好cost好于历史最优cost，做出更新
        if self.best_total_cost > self.total_cost:
            self.best_total_cost = self.total_cost
            for i in range(0, self.customer_number):
                self.best_allocation[i] = self.customer_allocation[i]
            return True

        self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
        return False

    def solve(self):
        # 初始化open list
        self.open_facility()
        while not self.alloc_customer_randomly():
            self.open_facility()
            for i in range(0, self.facility_number):
                self.facility_capacity[i] = self.F_capacity[i]
            continue
        print('初始open list:', self.facility_open_list)
        # 进入初始搜索
        for i in range(0, LOOP_LENGTH):
            self.generate_neighbor_by_swap_customer()
        self.best_total_cost = self.total_cost
        for i in range(0, self.customer_number):
            self.best_allocation[i] = self.customer_allocation[i]

        print('使用局部搜索，初始分配方案花费：', self.total_cost)
        for i in range(0, 100):
            if self.generate_neighbor():
                print('使用局部搜索，第', i, '循环 ', '接受新的邻居解，新的花费更新为：', self.total_cost)

        print('最终花销为：', self.best_total_cost, '\n', '开设工厂列表为：')
        for i in range(0, self.customer_number):
            self.facility_open_list[self.best_allocation[i]] = 1
        print(self.facility_open_list)
        print('顾客分配方案为：(按照顺序，第i个数字表示顾客i被分配到工厂的编号)')
        print(self.best_allocation)


class SimulatedAnnealingSol:

    def __init__(self, filename):
        self.filename = filename
        self.facility_number = 0
        self.customer_number = 0
        self.F_capacity = []
        self.facility_capacity = []                             # 变量
        self.facility_open_cost = []
        self.customer_demand = []
        self.distance_to_facility = []
        self.read_file()

        self.facility_open_list = [0]*self.facility_number      # 变量

        self.customer_allocation = [0]*self.customer_number     # 变量

        self.total_cost = 0                                     # 变量

        self.best_total_cost = 0
        self.best_allocation = [0]*self.customer_number

        self.temperature_inner = MAX_TEMPERATURE
        self.temperature_outer = MAX_TEMPERATURE

    def read_file(self):
        fp = open(self.filename)
        problem_size = fp.readline().split()
        self.facility_number = int(problem_size[0])
        self.customer_number = int(problem_size[1])

        for i in range(0, self.facility_number):
            facility_info = fp.readline().split()
            self.F_capacity.append(int(facility_info[0]))
            self.facility_capacity.append(int(facility_info[0]))
            self.facility_open_cost.append(int(facility_info[1]))

        for i in range(0, int(self.customer_number / 10)):
            demand_info = fp.readline().split()
            for j in range(0, 10):
                self.customer_demand.append(int(demand_info[j][0:len(demand_info[j])-1]))

        for i in range(0, int(self.customer_number)):
            temp_distance = []
            for j in range(0, int(self.facility_number / 10)):
                distance_info = fp.readline().split()
                for k in range(0, 10):
                    temp_distance.append(int(distance_info[k][0:len(distance_info[k])-1]))
            self.distance_to_facility.append(temp_distance)

    def open_facility(self):
        for i in range(0, self.facility_number):
            self.facility_open_list[i] = 0
        self.total_cost = 0
        for i in range(0, self.facility_number):
            if random.random() < 0.75:
                self.facility_open_list[i] = 1
                self.total_cost += self.facility_open_cost[i]

    def alloc_customer_randomly(self):
        for i in range(0, self.customer_number):
            count = 0
            while True:
                if count == self.facility_number:
                    return False
                count += 1
                choose_facility = random.randint(0, self.facility_number - 1)
                if self.facility_open_list[choose_facility] == 1 and self.facility_capacity[choose_facility] >= self.customer_demand[i]:
                    self.facility_capacity[choose_facility] -= self.customer_demand[i]
                    self.total_cost += self.distance_to_facility[i][choose_facility]
                    self.customer_allocation[i] = choose_facility
                    break

        return True

    def generate_neighbor_by_swap_customer(self):               # 产生方式是交换两个不同工厂的顾客，缺点是无法开厂，应配合1使用
        for i in range(0, 100):                                 # 在局部搜索中，这一句改为for i in range(0, 1000)更好
            customer_1 = random.randint(0, self.customer_number - 1)
            customer_2 = random.randint(0, self.customer_number - 1)
            facility_cus_1 = self.customer_allocation[customer_1]
            facility_cus_2 = self.customer_allocation[customer_2]
            if customer_1 == customer_2 or facility_cus_1 == facility_cus_2:
                continue                                        # 产生的是这个点本身而不是邻居，重来
            if self.facility_capacity[facility_cus_1] + self.customer_demand[customer_1] - \
                    self.customer_demand[customer_2] < 0 or self.facility_capacity[facility_cus_2] + \
                    self.customer_demand[customer_2] - self.customer_demand[customer_1] < 0:
                continue                                        # 交换被拒绝，有一个工厂的容量不足
            # 交换操作可进行，计算总花费是否减少，如果减少则接受邻居解，总花费仅仅包括到工厂距离
            cost_before = self.distance_to_facility[customer_1][facility_cus_1] \
                          + self.distance_to_facility[customer_2][facility_cus_2]
            cost_after = self.distance_to_facility[customer_1][facility_cus_2] \
                          + self.distance_to_facility[customer_2][facility_cus_1]
            if cost_before <= cost_after and random.random() > math.exp((cost_before - cost_after)/self.temperature_inner):
                return False

            self.facility_capacity[facility_cus_1] = self.facility_capacity[facility_cus_1] + \
                                                     self.customer_demand[customer_1] - self.customer_demand[customer_2]
            self.facility_capacity[facility_cus_2] = self.facility_capacity[facility_cus_2] + \
                                                     self.customer_demand[customer_2] - self.customer_demand[customer_1]
            self.customer_allocation[customer_1] = facility_cus_2
            self.customer_allocation[customer_2] = facility_cus_1
            self.total_cost = self.total_cost - cost_before + cost_after

            return True

    def generate_neighbor(self):
        # 在之前的基础上修改open list
        facility = random.randint(0, self.facility_number-1)
        self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
        # 更新total cost
        self.total_cost = 0
        for i in range(0, self.facility_number):
            if self.facility_open_list[i] == 1:
                self.total_cost += self.facility_open_cost[i]
        if self.total_cost == 0:
            self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
            return False
        # 还原capacity
        for i in range(0, self.facility_number):
            self.facility_capacity[i] = self.F_capacity[i]
        # 重新分配顾客
        if not self.alloc_customer_randomly():
            self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
            return False

        # 开始寻找该open list对应的最好cost
        while self.temperature_inner > MIN_TEMPERATURE:
            for i in range(0, 1000):
                self.generate_neighbor_by_swap_customer()
            self.temperature_inner *= ATTENUATION_QUOTIENT

        # 如果该open list对应的最好cost好于历史最优cost，做出更新
        if self.best_total_cost > self.total_cost or random.random() < math.exp((self.best_total_cost - self.total_cost)/self.temperature_outer):
            self.best_total_cost = self.total_cost
            for i in range(0, self.customer_number):
                self.best_allocation[i] = self.customer_allocation[i]
            return True

        self.facility_open_list[facility] = 1 - self.facility_open_list[facility]
        return False

    def solve(self):
        # 初始化open list
        self.open_facility()
        while not self.alloc_customer_randomly():
            self.open_facility()
            for i in range(0, self.facility_number):
                self.facility_capacity[i] = self.F_capacity[i]
            continue
        print('初始open list:', self.facility_open_list)
        # 进入初始搜索
        while self.temperature_inner > MIN_TEMPERATURE:
            for i in range(0, 100):
                self.generate_neighbor_by_swap_customer()
            self.temperature_inner *= ATTENUATION_QUOTIENT
        self.best_total_cost = self.total_cost
        for i in range(0, self.customer_number):
            self.best_allocation[i] = self.customer_allocation[i]

        print('使用模拟退火，初始分配方案花费：', self.total_cost)
        while self.temperature_outer > MIN_TEMPERATURE:
            self.temperature_inner = MAX_TEMPERATURE
            if self.generate_neighbor():
                print('使用模拟退火，外层温度：', self.temperature_outer, '接受新的邻居解，新的花费更新为：', self.total_cost)
            else:
                print('使用模拟退火，外层温度：', self.temperature_outer, '不接受新的邻居解')
            self.temperature_outer *= ATTENUATION_QUOTIENT

        print('最终花销为：', self.best_total_cost, '\n', '开设工厂列表为：')
        for i in range(0, self.customer_number):
            self.facility_open_list[self.best_allocation[i]] = 1
        print(self.facility_open_list)
        print('顾客分配方案为：(按照顺序，第i个数字表示顾客i被分配到工厂的编号)')
        print(self.best_allocation)


def main():
    print('local search solution.')
    print('一共提供如下几种解法：')
    print('1 局部搜索')
    print('2 模拟退火')
    print('3 禁忌搜索')
    command = input('请输入您想使用的算法：')
    for i in range(1, INSTANCE_NUMBER+1):
        filename = 'p' + str(i)
        if command == '1':
            solution1 = LocalSearchSol(filename)
            solution1.solve()
        elif command == '2':
            solution2 = SimulatedAnnealingSol(filename)
            solution2.solve()


if __name__ == '__main__':
    main()
