import random
import math
import datetime
import os
import time

INSTANCE_NUMBER = 71  # 测试的时候是1，实际上一共71个测试例子
LOOP_LENGTH = 1000
MAX_TEMPERATURE = 100
MIN_TEMPERATURE = 0.5
ATTENUATION_QUOTIENT = 0.99

MAX_NUM = 100000000


class LocalSearchSol:

    def __init__(self, filename):
        self.filename = filename
        self.facility_number = 0
        self.customer_number = 0
        self.facility_capacity = []                             # 变量
        self.facility_open_cost = []
        self.customer_demand = []
        self.distance_to_facility = []
        self.read_file()

        self.facility_open_list = [0]*self.facility_number      # 变量

        self.customer_allocation = []                           # 变量

        self.total_cost = 0                                     # 变量

    def init_alloc_customer(self):
        for i in range(0, self.customer_number):
            while True:
                choose_facility = random.randint(0, self.facility_number-1)
                if self.facility_capacity[choose_facility] >= self.customer_demand[i]:
                    if self.facility_open_list[choose_facility] == 0:
                        self.total_cost += self.facility_open_cost[choose_facility]
                    self.facility_open_list[choose_facility] += 1
                    self.facility_capacity[choose_facility] -= self.customer_demand[i]
                    self.total_cost += self.distance_to_facility[i][choose_facility]

                    self.customer_allocation.append(choose_facility)
                    break

    def read_file(self):
        fp = open(self.filename)
        problem_size = fp.readline().split()
        self.facility_number = int(problem_size[0])
        self.customer_number = int(problem_size[1])

        for i in range(0, self.facility_number):
            facility_info = fp.readline().split()
            self.facility_capacity.append(int(facility_info[0]))
            self.facility_open_cost.append(int(facility_info[1]))

        while len(self.customer_demand) < self.customer_number:
            demand_info = fp.readline().split()
            for i in range(0, len(demand_info)):
                self.customer_demand.append(float(demand_info[i]))

        distance_infos = []
        while len(distance_infos) < self.facility_number:
            distance_info = []
            while len(distance_info) < self.customer_number:
                temp = fp.readline().split()
                for i in range(0, len(temp)):
                    distance_info.append(float(temp[i]))
            distance_infos.append(distance_info)
        for i in range(0, self.customer_number):
            temp_distance = []
            for j in range(0, self.facility_number):
                temp_distance.append(distance_infos[j][i])
            self.distance_to_facility.append(temp_distance)

    def write_file(self):
        fp = open('Detailed Solution Of Local Search/result for ' + self.filename.split('/')[1], 'w')
        fp.write(str(self.total_cost) + '\n')
        for i in range(0, self.facility_number):
            if self.facility_open_list[i] != 0:
                fp.write('1 ')
            else:
                fp.write('0 ')
        fp.write('\n')
        for i in range(0, self.customer_number):
            fp.write(str(self.customer_allocation[i]) + ' ')

    def generate_neighbor_by_change_facility(self):             # 产生方式为：将一个顾客从A工厂移到B工厂
        while True:
            choose_customer = random.randint(0, self.customer_number-1)
            choose_facility = random.randint(0, self.facility_number-1)
            if self.customer_allocation[choose_customer] == choose_facility:
                continue                                        # 产生的是这个点本身而不是邻居，重来
            if self.facility_capacity[choose_facility] < self.customer_demand[choose_customer]:
                continue                                        # 交换被拒绝，因为目标工厂容量不足
            # 交换操作可进行，计算总花费是否减少，如果减少则接受邻居解，总花费包括 到工厂距离+开工厂费用
            allocated_facility_before = self.customer_allocation[choose_customer]
            # print('尝试操作：将顾客', choose_customer, '从工厂', allocated_facility_before, '转到工厂', choose_facility)
            cost_before = self.distance_to_facility[choose_customer][allocated_facility_before]
            if self.facility_open_list[allocated_facility_before] == 1:
                cost_before += self.facility_open_cost[allocated_facility_before]
            cost_after = self.distance_to_facility[choose_customer][choose_facility]
            if self.facility_open_list[choose_facility] == 0:
                cost_after += self.facility_open_cost[choose_facility]
            if cost_before <= cost_after:                       # 邻居解不能接受
                return False

            self.facility_capacity[allocated_facility_before] += self.customer_demand[choose_customer]
            self.facility_capacity[choose_facility] -= self.customer_demand[choose_customer]

            self.facility_open_list[allocated_facility_before] -= 1
            self.facility_open_list[choose_facility] += 1

            self.customer_allocation[choose_customer] = choose_facility
            self.total_cost = self.total_cost - cost_before + cost_after

            return True

    def generate_neighbor_by_swap_customer(self):               # 产生方式是交换两个不同工厂的顾客，缺点是无法开厂，应配合1使用
        while True:
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

    def solve(self):
        self.init_alloc_customer()                              # 随机得到一个分配方案
        print('使用局部搜索，初始分配方案花费：', self.total_cost)
        for i in range(0, 100*LOOP_LENGTH):
            if self.generate_neighbor_by_change_facility():
                print('使用局部搜索1，第', i, '循环 ', '接受新的邻居解：', '新的花费更新为：', self.total_cost)
            # elif self.generate_neighbor_by_swap_customer():
            #     print('使用局部搜索2，第', i, '循环 ', '接受新的邻居解：', '新的花费更新为：', self.total_cost)
        self.write_file()
        return self.total_cost


class SimulatedAnnealingSol:

    def __init__(self, filename):
        self.filename = filename
        self.facility_number = 0
        self.customer_number = 0
        self.facility_capacity = []                             # 变量
        self.facility_open_cost = []
        self.customer_demand = []
        self.distance_to_facility = []
        self.read_file()

        self.facility_open_list = [0]*self.facility_number      # 变量

        self.customer_allocation = []                           # 变量

        self.total_cost = 0                                     # 变量

        self.temperature = MAX_TEMPERATURE

    def init_alloc_customer(self):
        for i in range(0, self.customer_number):
            while True:
                choose_facility = random.randint(0, self.facility_number - 1)
                if self.facility_capacity[choose_facility] >= self.customer_demand[i]:
                    if self.facility_open_list[choose_facility] == 0:
                        self.total_cost += self.facility_open_cost[choose_facility]
                    self.facility_open_list[choose_facility] += 1
                    self.facility_capacity[choose_facility] -= self.customer_demand[i]
                    self.total_cost += self.distance_to_facility[i][choose_facility]

                    self.customer_allocation.append(choose_facility)
                    break

    def read_file(self):
        fp = open(self.filename)
        problem_size = fp.readline().split()
        self.facility_number = int(problem_size[0])
        self.customer_number = int(problem_size[1])

        for i in range(0, self.facility_number):
            facility_info = fp.readline().split()
            self.facility_capacity.append(int(facility_info[0]))
            self.facility_open_cost.append(int(facility_info[1]))

        while len(self.customer_demand) < self.customer_number:
            demand_info = fp.readline().split()
            for i in range(0, len(demand_info)):
                self.customer_demand.append(float(demand_info[i]))

        distance_infos = []
        while len(distance_infos) < self.facility_number:
            distance_info = []
            while len(distance_info) < self.customer_number:
                temp = fp.readline().split()
                for i in range(0, len(temp)):
                    distance_info.append(float(temp[i]))
            distance_infos.append(distance_info)
        for i in range(0, self.customer_number):
            temp_distance = []
            for j in range(0, self.facility_number):
                temp_distance.append(distance_infos[j][i])
            self.distance_to_facility.append(temp_distance)

    def write_file(self):
        fp = open('Detailed Solution Of Simulated Annealing/result for ' + self.filename.split('/')[1], 'w')
        fp.write(str(self.total_cost) + '\n')
        for i in range(0, self.facility_number):
            if self.facility_open_list[i] != 0:
                fp.write('1 ')
            else:
                fp.write('0 ')
        fp.write('\n')
        for i in range(0, self.customer_number):
            fp.write(str(self.customer_allocation[i]) + ' ')

    def generate_neighbor_by_change_facility(self):             # 产生方式为：将一个顾客从A工厂移到B工厂
        while True:
            choose_customer = random.randint(0, self.customer_number-1)
            choose_facility = random.randint(0, self.facility_number-1)
            if self.customer_allocation[choose_customer] == choose_facility:
                continue                                        # 产生的是这个点本身而不是邻居，重来
            if self.facility_capacity[choose_facility] < self.customer_demand[choose_customer]:
                continue                                        # 交换被拒绝，因为目标工厂容量不足
            # 交换操作可进行，计算总花费是否减少，如果减少则接受邻居解，总花费包括 到工厂距离+开工厂费用
            allocated_facility_before = self.customer_allocation[choose_customer]
            # print('尝试操作：将顾客', choose_customer, '从工厂', allocated_facility_before, '转到工厂', choose_facility)
            cost_before = self.distance_to_facility[choose_customer][allocated_facility_before]
            if self.facility_open_list[allocated_facility_before] == 1:
                cost_before += self.facility_open_cost[allocated_facility_before]
            cost_after = self.distance_to_facility[choose_customer][choose_facility]
            if self.facility_open_list[choose_facility] == 0:
                cost_after += self.facility_open_cost[choose_facility]

            if cost_before <= cost_after and \
                    random.random() > math.exp((cost_before - cost_after)/self.temperature):
                return False

            self.facility_capacity[allocated_facility_before] += self.customer_demand[choose_customer]
            self.facility_capacity[choose_facility] -= self.customer_demand[choose_customer]

            self.facility_open_list[allocated_facility_before] -= 1
            self.facility_open_list[choose_facility] += 1

            self.customer_allocation[choose_customer] = choose_facility
            self.total_cost = self.total_cost - cost_before + cost_after

            return True

    def generate_neighbor_by_swap_customer(self):               # 产生方式是交换两个不同工厂的顾客，缺点是无法开厂，应配合1使用
        while True:
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
            if cost_before <= cost_after and \
                    random.random() > math.exp((cost_before - cost_after)/cost_before/self.temperature):
                return False

            self.facility_capacity[facility_cus_1] = self.facility_capacity[facility_cus_1] + \
                                                     self.customer_demand[customer_1] - self.customer_demand[customer_2]
            self.facility_capacity[facility_cus_2] = self.facility_capacity[facility_cus_2] + \
                                                     self.customer_demand[customer_2] - self.customer_demand[customer_1]
            self.customer_allocation[customer_1] = facility_cus_2
            self.customer_allocation[customer_2] = facility_cus_1
            self.total_cost = self.total_cost - cost_before + cost_after

            return True

    def solve(self):
        self.init_alloc_customer()
        print('使用模拟退火，初始分配方案花费：', self.total_cost)
        while self.temperature > MIN_TEMPERATURE:
            for i in range(0, LOOP_LENGTH):
                # if i % 3 != 0:
                #     if self.generate_neighbor_by_swap_customer():
                #         print('使用模拟退火，当前温度：', self.temperature, '，第', i, '循环 ', '接受新的邻居解,花费更新为：', self.total_cost)
                #     continue
                if self.generate_neighbor_by_change_facility():
                    print('使用模拟退火，当前温度：', self.temperature, '，第', i, '循环 ', '接受新的邻居解,花费更新为：', self.total_cost)
            self.temperature *= ATTENUATION_QUOTIENT
        self.write_file()
        return self.total_cost


class TabuSearch:

    def __init__(self, filename):
        self.filename = filename
        self.facility_number = 0
        self.customer_number = 0
        self.facility_capacity = []                             # 变量
        self.facility_open_cost = []
        self.customer_demand = []
        self.distance_to_facility = []
        self.read_file()

        # 下面三个变量通过init_alloc_customer初始化
        self.facility_open_list = [0]*self.facility_number      # 变量
        self.customer_allocation = []                           # 变量
        self.total_cost = 0                                     # 变量

        self.best_solution = [0]*self.customer_number
        self.min_cost = MAX_NUM

        self.tabu_list = []
        for i in range(0, self.customer_number):
            temp = []
            for j in range(0, self.facility_number):
                temp.append(0)
            self.tabu_list.append(temp)

        self.neighbor_index1 = 0
        self.neighbor_index2 = 0
        self.neighbor_index3 = 0
        self._round = 0

    def init_alloc_customer(self):
        for i in range(0, self.customer_number):
            while True:
                choose_facility = random.randint(0, self.facility_number-1)
                if self.facility_capacity[choose_facility] >= self.customer_demand[i]:
                    if self.facility_open_list[choose_facility] == 0:
                        self.total_cost += self.facility_open_cost[choose_facility]
                    self.facility_open_list[choose_facility] += 1
                    self.facility_capacity[choose_facility] -= self.customer_demand[i]
                    self.total_cost += self.distance_to_facility[i][choose_facility]

                    self.customer_allocation.append(choose_facility)
                    break

    def read_file(self):
        fp = open(self.filename)
        problem_size = fp.readline().split()
        self.facility_number = int(problem_size[0])
        self.customer_number = int(problem_size[1])

        for i in range(0, self.facility_number):
            facility_info = fp.readline().split()
            self.facility_capacity.append(int(facility_info[0]))
            self.facility_open_cost.append(int(facility_info[1]))

        while len(self.customer_demand) < self.customer_number:
            demand_info = fp.readline().split()
            for i in range(0, len(demand_info)):
                self.customer_demand.append(float(demand_info[i]))

        distance_infos = []
        while len(distance_infos) < self.facility_number:
            distance_info = []
            while len(distance_info) < self.customer_number:
                temp = fp.readline().split()
                for i in range(0, len(temp)):
                    distance_info.append(float(temp[i]))
            distance_infos.append(distance_info)
        for i in range(0, self.customer_number):
            temp_distance = []
            for j in range(0, self.facility_number):
                temp_distance.append(distance_infos[j][i])
            self.distance_to_facility.append(temp_distance)

    def update_best_solution(self):
        if self.total_cost < self.min_cost:
            self.min_cost = self.total_cost
            for i in range(0, self.customer_number):
                self.best_solution[i] = self.customer_allocation[i]
            print('第', self._round, '轮，最优解更新为：', self.total_cost, '分配方案：')
            print(self.customer_allocation)
            # time.sleep(0.1)

    def update_tabu_list(self):
        self.tabu_list[self.neighbor_index1][self.neighbor_index2] = \
            self._round + self.facility_number*self.customer_number*0.1
        self.tabu_list[self.neighbor_index1][self.neighbor_index3] = \
            self._round + self.facility_number*self.customer_number*0.1

    def generate_best_neighbor(self):
        best_neighbor_cost = MAX_NUM
        self.neighbor_index1 = 0
        self.neighbor_index2 = 0
        self.neighbor_index3 = 0
        for i in range(0, self.customer_number):
            for j in range(0, self.facility_number):
                if random.random() > 0.4:
                    continue                                  # 只取一部分领域
                if self.customer_allocation[i] == j:
                    continue                                    # 不是邻居是本身
                if self.facility_capacity[j] < self.customer_demand[i]:
                    continue                                    # 容量不够拒绝操作
                facility_before = self.customer_allocation[i]
                cost_before = self.distance_to_facility[i][facility_before]
                if self.facility_open_list[facility_before] == 1:
                    cost_before += self.facility_open_cost[facility_before]
                cost_after = self.distance_to_facility[i][j]
                if self.facility_open_list[j] == 0:
                    cost_after += self.facility_open_cost[j]
                if cost_after - cost_before >= best_neighbor_cost:
                    continue                                    # 肯定不是最优邻居，直接忽略
                if self.neighbor_in_tabu_list(i, j) and self.total_cost + cost_after - cost_before >= self.min_cost:
                    continue                                    # 这个邻居在禁忌表当中，不能选，除非满足特赦准则
                # 满足所有条件之后，更新最佳邻居
                best_neighbor_cost = cost_after - cost_before
                self.neighbor_index1 = i
                self.neighbor_index2 = j
                self.neighbor_index3 = self.customer_allocation[self.neighbor_index1]
        # 使用最佳邻居作为下一节点：
        if best_neighbor_cost == MAX_NUM:
            print('严重错误，禁忌表过大，找不到下一个可行邻居')
            exit(0)
        customer_choosed = self.neighbor_index1
        facility_before = self.customer_allocation[self.neighbor_index1]
        facility_after = self.neighbor_index2
        self.facility_capacity[facility_before] += self.customer_demand[customer_choosed]
        self.facility_capacity[facility_after] -= self.customer_demand[customer_choosed]

        self.facility_open_list[facility_before] -= 1
        self.facility_open_list[facility_after] += 1

        self.customer_allocation[customer_choosed] = facility_after
        self.total_cost = self.total_cost + best_neighbor_cost

        self._round += 1

    def neighbor_in_tabu_list(self, customer_choosed, facility_choosed):
        return self.tabu_list[customer_choosed][facility_choosed] > self._round

    def solve(self):
        temp_min_cost = MAX_NUM
        temp_best_solution = []
        for k in range(0, 2):
            self.__init__(self.filename)
            # 初始化
            self.init_alloc_customer()
            self.update_best_solution()

            # 开始搜索
            for i in range(0, 10 * LOOP_LENGTH):
                self.generate_best_neighbor()
                # print(i)
                # print('第', i, '轮，当前分配方案开销：', self.total_cost, '分配方案：')
                # print(self.customer_allocation)
                self.update_best_solution()
                self.update_tabu_list()
            print('求得的最优解花费：', self.min_cost, '分配方案：\n', self.best_solution)

            if self.min_cost < temp_min_cost:
                temp_min_cost = self.min_cost
                temp_best_solution = self.best_solution
        print('\n\n最后的最优解：', temp_min_cost, '分配方案：')
        print(temp_best_solution)

        temp_open_list = [0]*self.facility_number
        fp = open('Detailed Solution Of Tabu Search/result for ' + self.filename.split('/')[1], 'w')
        fp.write(str(temp_min_cost) + '\n')
        for i in range(0, self.customer_number):
            temp_open_list[self.customer_allocation[i]] = 1
        for i in range(0, self.facility_number):
            fp.write(str(temp_open_list[i]) + ' ')
        fp.write('\n')
        for i in range(0, self.customer_number):
            fp.write(str(temp_best_solution[i]) + ' ')
        return temp_min_cost


def main():
    print('local search solution.')
    print('一共提供如下几种解法：')
    print('1 局部搜索')
    print('2 模拟退火')
    print('3 禁忌搜索')
    command = input('请输入您想使用的算法：')
    write_file_name = ''
    if command == '1':
        write_file_name = 'Result Table Of Local Search'
    elif command == '2':
        write_file_name = 'Result Table Of Simulated Annealing'
    elif command == '3':
        write_file_name = 'Result Table Of Tabu Search'
    fp = open(write_file_name, 'a')
    if os.stat(write_file_name).st_size == 0:
        fp.write(''.ljust(10) + 'Result'.ljust(20) + 'Time(s)\n')

    for i in range(1, INSTANCE_NUMBER+1):
        filename = 'Instances/p' + str(i)
        res = 0
        start_time = datetime.datetime.now()
        if command == '1':
            solution1 = LocalSearchSol(filename)
            res = solution1.solve()
        elif command == '2':
            solution2 = SimulatedAnnealingSol(filename)
            res = solution2.solve()
        elif command == '3':
            solution3 = TabuSearch(filename)
            res = solution3.solve()
        end_time = datetime.datetime.now()
        fp.write(('p' + str(i)).ljust(10) + str(res).ljust(20) + str((end_time - start_time).seconds) + '\n')


if __name__ == '__main__':
    main()
