data = [1, 1, 1, 1, 1, 2, 2, 2, 3, 2, 2, 4, 4, 4, 4, 4, 5, 5, 6, 7, 7, 7]

threshold = 2
from collections import OrderedDict


class ClusterInfo:
    clusters_info = OrderedDict()

    def __init__(self, number, type, start, end):
        self.number = number
        self.type = type
        self.start = start
        self.end = end
        self.strength_check()

    def create_stats(
        self,
        number,
        data,
    ):
        pass

    def strength_check(self):
        self.strength = self.end - self.start + 1

    def get_strength(self):
        return self.strength


def run_line(data):
    l = len(data)
    i, j = 0, 0
    s = ""
    while i != l:
        j = i
        while j != l and data[i] == data[j]:
            j += 1
        length = j - i
        s = s + str(data[i]).rjust(3, "0") + str(length).rjust(3, "0")
        i = j
    return s


def create_cluster_details(data):
    total_size = len(data)
    index = 0
    total_count = 0
    while index < total_size:
        cluster = int(data[index : index + 3])
        count = int(data[index + 3 : index + 6])
        start = total_count
        end = total_count + count - 1
        print(cluster, count, start, end)
        if count > 2:
            ClusterInfo.clusters_info[cluster] = ClusterInfo(
                cluster, "test", start, end
            )
        total_count = total_count + count
        index += 6
    print(ClusterInfo.clusters_info)

def get_previous_cluster():
    pass

def get_next_cluster():
    pass

def merge_cluster(data):
    total_size = len(data)
    index = 0
    total_count = 0
    previous_cluster = None
    while index < total_size:
        cluster = int(data[index : index + 3])
        count = int(data[index + 3 : index + 6])
        start = total_count
        end = total_count + count - 1
        # print(cluster, count, start, end)
        if count <= 2:
            print(cluster, "cluster_details")
            previous_strength, next_strength = -1, -1
            if previous_cluster and int(data[index - 3 : index]) >= threshold:
                print(
                    ClusterInfo.clusters_info[
                        previous_cluster
                    ].get_strength(),
                    "previous",
                )
                previous_strength =  ClusterInfo.clusters_info[
                        previous_cluster
                    ].get_strength()
            if (index + 6) < len(data) and int(
                data[index + 9 : index + 12]
            ) >= threshold:
                print(
                    ClusterInfo.clusters_info[
                        int(data[index + 6 : index + 9])
                    ].get_strength(),
                    "next",
                )
                next_strength = ClusterInfo.clusters_info[
                        int(data[index + 6 : index + 9])
                    ].get_strength()
                
            if previous_cluster == cluster or previous_strength >= next_strength:
                p_cluster = ClusterInfo.clusters_info[
                        previous_cluster
                    ]
                p_cluster.end += count
                p_cluster.strength_check()
                print(type(data[index : index + 3]))
                print(type(data[index - 6 : index -3]))
            else:
                next_cluster = ClusterInfo.clusters_info[
                        int(data[index + 6 : index + 9])
                    ]
                next_cluster.start -= count
                next_cluster.strength_check()

        else:
            previous_cluster = cluster
            # ClusterInfo.clusters_info[cluster] = ClusterInfo(cluster,"test",start,end)
        total_count = total_count + count
        index += 6
    print(ClusterInfo.clusters_info)


data = run_line(data)
print(data)

create_cluster_details(data)
merge_cluster(data)

for key, value in ClusterInfo.clusters_info.items():
    print(key, value.start,value.end)
